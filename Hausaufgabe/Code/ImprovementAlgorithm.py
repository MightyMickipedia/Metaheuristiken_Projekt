from __future__ import annotations

#from Neigborhood import *
import math
from copy import deepcopy
from typing import TYPE_CHECKING
from abc import ABC

import numpy as np

from Neighbourhood import InsertionNeighborhood, SwapNeighborhood
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

    def Initialize(self, evaluationLogic: EvaluationLogic, solutionPool: SolutionPool, rng: np.random.Generator) -> None:
        """Setzt Bewertungslogik, Lösungspool und Zufallsgenerator für den Algorithmus."""
        self.EvaluationLogic = evaluationLogic
        self.SolutionPool = solutionPool
        self.RNG = rng
        
    def CreateNeighborhood(self, neighborhoodType: str, bestCurrentSolution: Solution) -> SwapNeighborhood | InsertionNeighborhood:
        """Erzeugt eine Nachbarschaft des angegebenen Typs für die aktuelle Lösung."""
        if neighborhoodType == 'Swap':
            return SwapNeighborhood(self.InputData, bestCurrentSolution.Permutation, self.EvaluationLogic, self.SolutionPool)
        elif neighborhoodType == 'Insertion':
            return InsertionNeighborhood(self.InputData, bestCurrentSolution.Permutation, self.EvaluationLogic, self.SolutionPool)
        else:
            raise Exception(f"Neighborhood type {neighborhoodType} not defined.")

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
    ) -> None:
        """Initialisiert Simulated Annealing mit den Einstellungen der Basisklasse."""
        super().__init__(inputData, neighborhoodEvaluationStrategy, neighborhoodTypes)
    
    #TODO Implement SA


""" Simulated Annealing or Tabu Search or Variable Neighborhood Search or ..."""
