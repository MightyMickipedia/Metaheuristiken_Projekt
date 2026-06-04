from __future__ import annotations

#from Neigborhood import *
import math
from copy import deepcopy
from typing import TYPE_CHECKING
from abc import ABC

import numpy as np

from Neighbourhood import BaseNeighborhood, EmptyBinNeighborhood, RepackItemNeighborhood
from OutputData import Solution, SolutionPool

if TYPE_CHECKING:
    from EvaluationLogic import EvaluationLogic
    from InputData import InputData
    from OutputData import SolutionPool

""" Basisklasse für Improvement Algorithms """ 
class ImprovementAlgorithm(ABC):
    """Basisklasse für Verbesserungsalgorithmen."""

    NeighborhoodRegistry = {
        'RepackItem': RepackItemNeighborhood,
        'RepackItems': RepackItemNeighborhood,
        'EmptyBin': EmptyBinNeighborhood,
    }

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
        self.NeighborhoodTypes = neighborhoodTypes if neighborhoodTypes is not None else ['RepackItems']
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
        neighborhoodClass = self.NeighborhoodRegistry.get(neighborhoodType)
        if neighborhoodClass is None:
            supportedTypes = ', '.join(sorted(self.NeighborhoodRegistry.keys()))
            raise ValueError(
                f"Neighborhood type {neighborhoodType} is not implemented. "
                f"Supported types are: {supportedTypes}."
            )

        return neighborhoodClass(self.InputData, bestCurrentSolution, self.EvaluationLogic, self.SolutionPool)

    def InitializeNeighborhoods(self, solution: Solution) -> None:
        """Initialisiert alle im Algorithmus konfigurierten Nachbarschaften."""
        for neighborhoodType in self.NeighborhoodTypes:
            neighborhood = self.CreateNeighborhood(neighborhoodType, solution)
            self.Neighborhoods[neighborhoodType] = neighborhood


class SimulatedAnnealing(ImprovementAlgorithm):
    """Simulated Annealing für Bin-Packing-Lösungen."""

    def __init__(
        self,
        inputData: InputData,
        neighborhoodEvaluationStrategy: str = 'FirstImprovement',
        neighborhoodTypes: list[str] | None = None,
        temperature: float = 0.95,
        coolingSpeed: float = 0.1,      
        threshold : float = 1e-6,
        maxMarkovLength: int = 1000, 
        numberOfMoves: int = 50,
    ) -> None:
        """Initialisiert Simulated Annealing mit den Einstellungen der Basisklasse."""
        super().__init__(inputData, neighborhoodEvaluationStrategy, neighborhoodTypes)
        self.temperature = temperature
        self.coolingSpeed = coolingSpeed
        self.threshold= threshold
        self.maxMarkovLength =maxMarkovLength 
        self.numberOfMoves = numberOfMoves
        self.markovChain = SolutionPool()

    def AcceptNeighborSolution(self, currentSolution: Solution, neighborSolution: Solution, temperature: float) -> bool:
        """Entscheidet, ob eine Nachbarlösung akzeptiert wird."""
        self.EvaluationLogic.CalculateNumberOfBins(currentSolution)
        self.EvaluationLogic.CalculateNumberOfBins(neighborSolution)

        delta = neighborSolution.NumberOfBins - currentSolution.NumberOfBins
        if delta <= 0:
            return True

        acceptanceProbability = math.exp(-delta / max(temperature, 1e-12))

       
        return self.RNG.random() <= acceptanceProbability


    def CoolDownFormula(self):
        """Berechnet die nächste Temperatur nach der Formel in Laarhoven, Aarts & Lenstra (1992)"""
        # ck+1 = ck / (1 + (ck * ln(1 + d))/ 3 sigmaK)
        previousSolutions = self.SolutionPool.Solutions  
        previousResults = [sol.NumberOfBins for sol in self.markovChain.Solutions]
        sigma = np.std(previousResults) #the standard deviation of the cost values of the configurations obtained by generating the kth Markov chain

        if sigma == 0:
            self.temperature *= 0.9
            return
        #sigma = self.SolutionPool.Solutions # standardabweichung der anzahl der bins der permutationen
        self.temperature = self.temperature / (1 + (self.temperature * np.log(1 + self.coolingSpeed) / (3 * sigma)))


    def CreateRandomNeighbor(self, currentSolution: Solution) -> Solution:
        """Erzeugt eine zufällige Nachbarlösung mit der ersten konfigurierten Nachbarschaft."""
        neighborhoodType = self.NeighborhoodTypes[0]
        neighborhood = self.CreateNeighborhood(neighborhoodType, currentSolution)
        neighborhood.DiscoverMoves(self.numberOfMoves)

        if not neighborhood.Moves:
            return currentSolution

        selectedMove = self.RNG.choice(neighborhood.Moves)
        neighborSolution = Solution(selectedMove.Allocation)
        self.EvaluationLogic.CalculateNumberOfBins(neighborSolution)
        return neighborSolution
    
    def Run(self, startSolution: Solution) -> Solution:
        """Führt Simulated Annealing ab einer Startlösung aus."""
        print("start SA")

        self.EvaluationLogic.CalculateNumberOfBins(startSolution)
        currentSolution = startSolution
        bestSolution = deepcopy(startSolution)
        markovLength = min(
            max(1, startSolution.NumberOfBins * max(1, startSolution.NumberOfItems - 1)),
            self.maxMarkovLength,
        )

        while self.temperature > self.threshold:
            while len(self.markovChain.Solutions) < markovLength:
                neighborSolution = self.CreateRandomNeighbor(currentSolution)
                self.markovChain.AddSolution(neighborSolution)

                if self.AcceptNeighborSolution(currentSolution, neighborSolution, self.temperature):
                    currentSolution = neighborSolution

                    if currentSolution.NumberOfBins < bestSolution.NumberOfBins:
                        bestSolution = deepcopy(currentSolution)
                        self.SolutionPool.AddSolution(bestSolution)

            self.CoolDownFormula()
            print(self.temperature)
            self.markovChain.ClearSolutionPool()

        return bestSolution


    def CreateNeighbor(self,currentSolution: Solution) ->Solution:
        neighborSolution = deepcopy(currentSolution)
        self.EvaluationLogic.CalculateNumberOfBins(neighborSolution)
            
        #move any random item into a new bin that has enough space 
        movedItemId = np.random.choice(list(neighborSolution.Allocation.keys()))
        movedItem = self.InputData.InputItems[movedItemId]
        maximum_capacity = self.InputData.InputBinCapacity.capacity
        candidates = [bin  for bin in neighborSolution.Bins if (maximum_capacity - neighborSolution.Bins[bin]) >= movedItem.weight]
        if len(candidates) > 0 :
            newBinId = np.random.choice(candidates)
        else:
            newBinId = neighborSolution.NumberOfBins

        neighborSolution.Allocation[movedItemId] = newBinId

        self.EvaluationLogic.CalculateNumberOfBins(neighborSolution)
        return neighborSolution


    def Run2(self, startSolution:Solution) -> Solution:
        
        currentSolution = deepcopy(startSolution)
        while self.temperature > self.threshold:
            #print(self.temperature)
            neighbor = self.CreateNeighbor(currentSolution)
            self.EvaluationLogic.CalculateNumberOfBins(currentSolution)
            self.EvaluationLogic.CalculateNumberOfBins(neighbor)
            if(neighbor.NumberOfBins < currentSolution.NumberOfBins) :
                self.SolutionPool.AddSolution(neighbor)
                self.CoolDownFormula()
            else :
                acceptanceCriterium = min(1, np.exp(- (neighbor.NumberOfBins - currentSolution.NumberOfBins) / self.temperature))
                if( np.random.random() > acceptanceCriterium):
                    self.SolutionPool.AddSolution(neighbor)
                    self.CoolDownFormula()
        return self.SolutionPool.Solutions[-1] 
