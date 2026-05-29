from __future__ import annotations

#from Neigborhood import *
import math
from copy import deepcopy
from typing import TYPE_CHECKING
from abc import ABC

import numpy as np

from Neighbourhood import BaseNeighborhood, InsertionNeighborhood, SwapNeighborhood
from OutputData import Solution

if TYPE_CHECKING:
    from EvaluationLogic import EvaluationLogic
    from InputData import InputData
    from OutputData import SolutionPool

""" Basisklasse für Improvement Algorithms """ 
class ImprovementAlgorithm(ABC):
    """Basisklasse für Verbesserungsalgorithmen."""

    def __init__(
        self,
        inputData: InputData,
        neighborhoodEvaluationStrategy: str = 'FirstImprovement',
        neighborhoodTypes: list[str] | None = None,
    ) -> None:
        """Initialisiert gemeinsame Daten und Einstellungen für Verbesserungsverfahren."""
        self.InputData = inputData

        self.EvaluationLogic = {}
        self.SolutionPool = {}

        self.NeighborhoodEvaluationStrategy = neighborhoodEvaluationStrategy
        self.NeighborhoodTypes = neighborhoodTypes if neighborhoodTypes is not None else ['RepackBins']
        self.Neighborhoods = {}

    def Initialize(self, evaluationLogic: EvaluationLogic, solutionPool: SolutionPool, rng: np.random.Generator = np.random.default_rng()) -> None:
        """Setzt Bewertungslogik, Lösungspool und Zufallsgenerator für den Algorithmus."""
        self.EvaluationLogic = evaluationLogic
        self.SolutionPool = solutionPool
        self.RNG = rng
        
    def Run(self, startSolution: Solution) -> Solution:
        """Führt den Verbesserungsalgorithmus ab einer Startlösung aus."""
        raise NotImplementedError("Run() must be implemented by concrete improvement algorithms.")

    def CreateNeighborhood(self, neighborhoodType: str, bestCurrentSolution: Solution) -> BaseNeighborhood:
        """Erzeugt eine Nachbarschaft des angegebenen Typs für die aktuelle Lösung."""
        if neighborhoodType == 'Swap':
            return SwapNeighborhood(self.InputData, bestCurrentSolution.Permutation, self.EvaluationLogic, self.SolutionPool)
        elif neighborhoodType == 'Insertion':
            return InsertionNeighborhood(self.InputData, bestCurrentSolution.Permutation, self.EvaluationLogic, self.SolutionPool)
        else:
            raise NotImplementedError(f"Neighborhood type {neighborhoodType} is not implemented.")

    def InitializeNeighborhoods(self, solution: Solution) -> None:
        """Initialisiert alle im Algorithmus konfigurierten Nachbarschaften."""
        for neighborhoodType in self.NeighborhoodTypes:
            neighborhood = self.CreateNeighborhood(neighborhoodType, solution)
            self.Neighborhoods[neighborhoodType] = neighborhood

class simulatedAnnealing(ImprovementAlgorithm):
    """Platzhalterklasse für ein Simulated-Annealing-Verfahren."""

    def __init__(
        self,
        inputData: InputData,
        neighborhoodEvaluationStrategy: str = 'FirstImprovement',
        neighborhoodTypes: list[str] | None = None,
        temperature: float = 0.95,
        coolingSpeed: float = 0.1,        
    ) -> None:
        """Initialisiert Simulated Annealing mit den Einstellungen der Basisklasse."""
        super().__init__(inputData, neighborhoodEvaluationStrategy, neighborhoodTypes)
        self.temperature = temperature
        self.coolingSpeed = coolingSpeed
        self.markovChain = self.SolutionPool()

    def AcceptNeighborSolution(self, currentSolution: Solution, neighborSolution: Solution, temperature: float) -> bool:
        """Entscheidet, ob eine Nachbarlösung akzeptiert wird."""
        self.EvaluationLogic.CalculateNumberOfBins(currentSolution)
        self.EvaluationLogic.CalculateNumberOfBins(neighborSolution)
        if self.RNG.random() <= self.temperature:
            return True
        return currentSolution > neighborSolution          

    def CoolDown(self) -> None:
        """Berechnet die nächste Temperatur."""
        sigma = np.std(self.SolutionPool.Solutions)
        self.temperature = self.temperature / (1 + (self.temperature * (math.log(1+self.coolingSpeed))/3*sigma))
    
    def Run(self, startSolution: Solution) -> Solution:
        """Führt Simulated Annealing ab einer Startlösung aus."""
        
        markovLength = Solution.NumberOfBins * (Solution.NumberOfItems-1)
        curSolution = startSolution
        while self.temperature > 0:
            while len(self.markovChain) < markovLength:
                neighborhood = self.CreateNeighborhood(self.NeighborhoodTypes[0],curSolution)
                for move in neighborhood.DiscoverMoves():
                    newSolution = move.permutation
                    self.markovChain.AddSolution(newSolution)
                    if self.AcceptNeighborSolution(newSolution):
                        curSolution = newSolution
                        break
            self.CoolDown()
            self.markovChain.ClearSolutionPool()
        
        return curSolution




""" Simulated Annealing or Tabu Search or Variable Neighborhood Search or ..."""
