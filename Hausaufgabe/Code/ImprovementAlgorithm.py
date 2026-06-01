from __future__ import annotations

#from Neigborhood import *
import math
from copy import deepcopy
from typing import TYPE_CHECKING
from abc import ABC

import numpy as np

from Neighbourhood import BaseNeighborhood, InsertionNeighborhood, SwapNeighborhood
from OutputData import Solution, SolutionPool

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
    ) -> None:
        """Initialisiert Simulated Annealing mit den Einstellungen der Basisklasse."""
        super().__init__(inputData, neighborhoodEvaluationStrategy, neighborhoodTypes)
        self.temperature = temperature
        self.coolingSpeed = coolingSpeed
        self.threshold= threshold
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

    def CoolDown(self) -> None:
        """Berechnet die nächste Temperatur."""
        self.temperature *= self.coolingSpeed

    def CoolDownFormula(self):
        """Berechnet die nächste Temperatur nach der Formel in Laarhoven, Aarts & Lenstra (1992)"""
        # ck+1 = ck / (1 + (ck * ln(1 + d))/ 3 sigmaK)
        previousSolutions = self.SolutionPool.Solutions  
        previousResults = [sol.NumberOfBins for sol in previousSolutions]
        sigma = np.std(previousResults) #the standard deviation of the cost values of the configurations obtained by generating the kth Markov chain
            
        #sigma = self.SolutionPool.Solutions # standardabweichung der anzahl der bins der permutationen
        self.temperature = self.temperature / (1 + (self.temperature * np.log(1 + self.coolingSpeed) / 3 * sigma))


    def CreateRandomNeighbor(self, currentSolution: Solution) -> Solution:
        """Erzeugt eine zufällige zulässige Nachbarlösung durch Umlegen eines Items."""
        allocation = deepcopy(currentSolution.Allocation)
        itemIds = list(allocation.keys())
        sourceItemId = int(self.RNG.choice(itemIds))
        sourceBinId = allocation[sourceItemId]
        binIds = sorted(set(allocation.values()))
        candidateBinIds = [binId for binId in binIds if binId != sourceBinId]

        if not candidateBinIds:
            return Solution(allocation)

        targetBinId = int(self.RNG.choice(candidateBinIds))
        targetWeight = sum(
            self.InputData.InputItems[itemId].weight
            for itemId, binId in allocation.items()
            if binId == targetBinId
        )
        itemWeight = self.InputData.InputItems[sourceItemId].weight

        if targetWeight + itemWeight <= self.InputData.InputBinCapacity.capacity:
            allocation[sourceItemId] = targetBinId

        neighborSolution = Solution(allocation)
        self.EvaluationLogic.CalculateNumberOfBins(neighborSolution)
        return neighborSolution
    
    def Run(self, startSolution: Solution) -> Solution:
        """Führt Simulated Annealing ab einer Startlösung aus."""

        self.EvaluationLogic.CalculateNumberOfBins(startSolution)
        currentSolution = startSolution
        bestSolution = deepcopy(startSolution)
        markovLength = min(
            max(1, startSolution.NumberOfBins * max(1, startSolution.NumberOfItems - 1)),
            1000,
        )

        while self.temperature > 1e-6:
            while len(self.markovChain.Solutions) < markovLength:
                neighborSolution = self.CreateRandomNeighbor(currentSolution)
                self.markovChain.AddSolution(neighborSolution)

                if self.AcceptNeighborSolution(currentSolution, neighborSolution, self.temperature):
                    currentSolution = neighborSolution

                    if currentSolution.NumberOfBins < bestSolution.NumberOfBins:
                        bestSolution = deepcopy(currentSolution)
                        self.SolutionPool.AddSolution(bestSolution)

            self.CoolDown()
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
            newBinId = neighborSolution.NumberOfBins + 1

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