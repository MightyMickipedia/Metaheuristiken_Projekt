from __future__ import annotations

from typing import TYPE_CHECKING

from OutputData import Solution, SolutionPool
from abc import ABC
import numpy as np

if TYPE_CHECKING:
    from EvaluationLogic import EvaluationLogic
    from InputData import InputData


class BaseNeighborhood(ABC):
    """Basisklasse für Nachbarschaften einer Bin Packing-Lösung."""

    def __init__(
        self,
        inputData: InputData,
        initialSolution: Solution,
        evaluationLogic: EvaluationLogic,
        solutionPool: SolutionPool,
    ) -> None:
        """Initialisiert gemeinsame Daten für die Erzeugung und Bewertung von Moves."""
        self.InputData = inputData
        self.InitialSolution = initialSolution
        self.EvaluationLogic = evaluationLogic
        self.SolutionPool = solutionPool

        self.Moves  = []

    def DiscoverMoves(self) -> None:
        """Erzeugt alle Moves der konkreten Nachbarschaft."""
        raise Exception('DiscoverMoves() is not implemented for the abstract BaseNeighborhood class.')

    def EvaluateMoves(self, evaluationStrategy: str) -> None:
        """Bewertet die erzeugten Moves mit der gewählten Bewertungsstrategie."""
        #self.SolutionPool.ClearSolutionPool()
        if evaluationStrategy == 'BestImprovement':
            self.EvaluateMovesBestImprovement()
        elif evaluationStrategy == 'FirstImprovement':
            self.EvaluateMovesFirstImprovement()
        else:
            raise Exception(f'Evaluation strategy {evaluationStrategy} not implemented.')
        

    def EvaluateMovesBestImprovement(self) -> None:
        """Bewertet alle erzeugten Moves und speichert die entstehenden Lösungen."""
        
        for move in self.Moves:
            moveSolution = Solution(move.Allocation)
            if moveSolution.FeasibilityCheck(self.InputData):
                self.EvaluationLogic.CalculateNumberOfBins(moveSolution)
                self.SolutionPool.AddSolution(moveSolution)

    def EvaluateMovesFirstImprovement(self) -> None:
        """Bewertet Moves bis zur ersten Verbesserung gegenüber der besten bekannten Lösung."""
        
        bestObjective = self.InitialSolution.NumberOfBins
        print(len(self.Moves))
        for move in self.Moves:
            moveSolution = Solution(move.Allocation)
            self.EvaluationLogic.CalculateNumberOfBins(moveSolution)
            self.SolutionPool.AddSolution(moveSolution)
            if moveSolution.NumberOfBins < bestObjective:
                return
    
class RepackItemMove:
    """Setze ein Element in einen neuen Bin."""

    def __init__(self, initialAllocation: dict, itemIndex:int, binIndex:int) -> None:
        """Erzeugt eine neue Allokation, in der das Item mit itemIndex in den Bin binIndex platziert wird."""
        self.Allocation = dict(initialAllocation)
        self.Allocation[itemIndex] = binIndex
        
class RepackItemNeighborhood(BaseNeighborhood):
    """Enthält n RepackMoves, bei denen n Items in alle möglichen Bins gepackt werden."""

    def __init__(
        self,
        inputData: InputData,
        initialSolution: Solution,
        evaluationLogic: EvaluationLogic,
        solutionPool: SolutionPool,
    ) -> None:
        """Initialisiert die Repacking-Nachbarschaft."""
        super().__init__(inputData, initialSolution, evaluationLogic, solutionPool)


    def DiscoverMoves(self,numberOfMoves:int=50) -> None:
        """Erzeugt alle möglichen Moves und prüft, ob diese erlaubt sind. Gibt alle legalen Moves zurück."""
        
        self.EvaluationLogic.CalculateNumberOfBins(self.InitialSolution)
        initialBins = self.InitialSolution.Bins
        initialAllocation = self.InitialSolution.Allocation
        maximumCapacity = self.InputData.InputBinCapacity.capacity

        self.Moves = []
        if numberOfMoves == len(initialAllocation.keys()):
            for itemId in list(set(initialAllocation.keys())):
                movedItem = self.InputData.InputItems[itemId]
                candidates = [bin  for bin in initialBins if (maximumCapacity - initialBins[bin]) >= movedItem.weight]
                for binId in candidates:
                    repackMove = RepackItemMove(initialAllocation, itemId, binId)
                    self.Moves.append(repackMove)

        else:             
            for _ in range(numberOfMoves):
                movedItemId = np.random.choice(list(initialAllocation.keys()))
                movedItem = self.InputData.InputItems[movedItemId]
                candidates = [bin  for bin in initialBins if (maximumCapacity - initialBins[bin]) >= movedItem.weight]
                if len(candidates) == 0: return
            
                binId = np.random.choice(candidates)
                repackMove = RepackItemMove(initialAllocation, movedItemId, binId)
                self.Moves.append(repackMove)

class EmptyBinMove:
    "Leere einen Bin."
    
    def __init__(
        self,
        initialAllocation: dict,
        maximumCapacity: float,
        sourceBinId: int,
        sortedSourceItemIds: np.ndarray,
        sortedSourceItemWeights: np.ndarray,
        targetBinIds: np.ndarray,
        targetBinWeights: np.ndarray,
    ) -> None:
        """Erzeugt eine neue Allokation, in der ein Bin geleert wird. Dabei werden die Elemente auf verfügbare Bins verteilt."""
        self.SourceBinId = sourceBinId
        self.Allocation = dict(initialAllocation)
        self.IsFeasible = False

        if sortedSourceItemIds.size == 0 or targetBinIds.size == 0:
            return

        workingTargetBinWeights = targetBinWeights.copy()
        for itemId, itemWeight in zip(sortedSourceItemIds, sortedSourceItemWeights):
            remainingCapacityAfterMove = maximumCapacity - (workingTargetBinWeights + itemWeight)
            feasibleTargetIndices = np.flatnonzero(remainingCapacityAfterMove >= 0)

            if feasibleTargetIndices.size == 0:
                self.Allocation = dict(initialAllocation)
                return

            bestFitIndex = feasibleTargetIndices[
                np.argmin(remainingCapacityAfterMove[feasibleTargetIndices])
            ]
            targetBinId = int(targetBinIds[bestFitIndex])
            self.Allocation[int(itemId)] = targetBinId
            workingTargetBinWeights[bestFitIndex] += itemWeight

        self.IsFeasible = True
    

class EmptyBinNeighborhood(BaseNeighborhood):

    def __init__(
        self,
        inputData: InputData,
        initialSolution: Solution,
        evaluationLogic: EvaluationLogic,
        solutionPool: SolutionPool,
    ) -> None:
        """Initialisiert die EmptyBin-Nachbarschaft."""
        super().__init__(inputData, initialSolution, evaluationLogic, solutionPool)

    def GetRandomMove(
        self,
        sourceBinIds: np.ndarray,
        sourceMoveData: dict[
            int,
            tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
        ],
        maximumCapacity: float,
    ):
        selectedBinIndex = np.random.randint(sourceBinIds.size)
        binId = int(sourceBinIds[selectedBinIndex])
        (
            sortedSourceItemIds,
            sortedSourceItemWeights,
            targetBinIds,
            targetBinWeights,
        ) = sourceMoveData[binId]
        emptybinMove = EmptyBinMove(
            self.InitialSolution.Allocation,
            maximumCapacity,
            binId,
            sortedSourceItemIds,
            sortedSourceItemWeights,
            targetBinIds,
            targetBinWeights,
        )
        if emptybinMove.IsFeasible:
            self.Moves.append(emptybinMove)
        return emptybinMove


    def DiscoverMoves(self,numberOfMoves:int=50) -> None:
        """Erzeugt alle Nachbarschaften, bei denen ein Bin geleert wird."""
        self.EvaluationLogic.CalculateNumberOfBins(self.InitialSolution)
        self.Moves = []
        initialBins = self.InitialSolution.Bins
        if len(initialBins) <= 1:
            return

        maximumCapacity = self.InputData.InputBinCapacity.capacity
        binIds = np.fromiter(initialBins.keys(), dtype=int, count=len(initialBins))
        binWeights = np.fromiter(initialBins.values(), dtype=float, count=len(initialBins))
        itemWeightsById = np.asarray(
            [item.weight for item in self.InputData.InputItems],
            dtype=float,
        )

        binItems = {}
        for itemId, binId in self.InitialSolution.Allocation.items():
            binItems.setdefault(binId, []).append(itemId)

        sourceMoveData = {}
        for binId, itemIds in binItems.items():
            if not itemIds:
                continue

            sourceItemIds = np.asarray(itemIds, dtype=int)
            sourceItemWeights = itemWeightsById[sourceItemIds]
            sortedIndices = np.argsort(-sourceItemWeights, kind="stable")
            targetMask = binIds != binId
            if not np.any(targetMask):
                continue

            sourceMoveData[int(binId)] = (
                sourceItemIds[sortedIndices],
                sourceItemWeights[sortedIndices],
                binIds[targetMask],
                binWeights[targetMask],
            )

        if not sourceMoveData:
            return

        sourceBinIds = np.fromiter(
            sourceMoveData.keys(),
            dtype=int,
            count=len(sourceMoveData),
        )
        for _ in range(numberOfMoves):
            self.GetRandomMove(sourceBinIds, sourceMoveData, maximumCapacity)
