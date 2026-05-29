from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from OutputData import Solution, SolutionPool
from copy import deepcopy
from abc import ABC

if TYPE_CHECKING:
    from EvaluationLogic import EvaluationLogic
    from InputData import InputData


Permutation: TypeAlias = list[int]


class BaseNeighborhood(ABC):
    """Basisklasse für Nachbarschaften auf einer Permutationslösung."""

    def __init__(
        self,
        inputData: InputData,
        initialPermutation: Permutation,
        evaluationLogic: EvaluationLogic,
        solutionPool: SolutionPool,
    ) -> None:
        """Initialisiert gemeinsame Daten für die Erzeugung und Bewertung von Moves."""
        self.InputData = inputData
        self.Permutation = initialPermutation
        self.EvaluationLogic = evaluationLogic
        self.SolutionPool = solutionPool

        self.Moves: list[SwapMove | InsertionMove] = []
        self.MoveSolutions: list[Solution] = []

        self.Type = 'None'

    def DiscoverMoves(self) -> None:
        """Erzeugt alle Moves der konkreten Nachbarschaft."""
        raise Exception('DiscoverMoves() is not implemented for the abstract BaseNeighborhood class.')

    def EvaluateMoves(self, evaluationStrategy: str) -> None:
        """Bewertet die erzeugten Moves mit der gewählten Bewertungsstrategie."""
        if evaluationStrategy == 'BestImprovement':
            self.EvaluateMovesBestImprovement()
        elif evaluationStrategy == 'FirstImprovement':
            self.EvaluateMovesFirstImprovement()
        else:
            raise Exception(f'Evaluation strategy {evaluationStrategy} not implemented.')

    def EvaluateMovesBestImprovement(self) -> None:
        """Bewertet alle erzeugten Moves und speichert die entstehenden Lösungen."""
        for move in self.Moves:
            moveSolution = Solution(self.InputData.InputJobs, move.Permutation)

            self.EvaluationLogic.DefineStartEnd(moveSolution)
            
            self.MoveSolutions.append(moveSolution)

    def EvaluateMovesFirstImprovement(self) -> None:
        """Bewertet Moves bis zur ersten Verbesserung gegenüber der besten bekannten Lösung."""
        bestObjective = self.SolutionPool.GetLowestMakespanSolution().Makespan

        for move in self.Moves:
            moveSolution = Solution(self.InputData.InputJobs, move.Permutation)

            if self.Type == 'BestInsertion':
                self.EvaluationLogic.DetermineBestInsertionAccelerated(moveSolution, move.removedJob)
            else:
                self.EvaluationLogic.DefineStartEnd(moveSolution)

            self.MoveSolutions.append(moveSolution)

            if moveSolution.Makespan < bestObjective:
                # abort neighborhood evaluation because an improvement has been found
                return

    def MakeBestMove(self) -> Solution:
        """Gibt die beste bewertete Nachbarschaftslösung zurück."""
        self.MoveSolutions.sort(key = lambda solution: solution.Makespan) # sort solutions according to makespan

        bestNeighborhoodSolution = self.MoveSolutions[0]

        return bestNeighborhoodSolution

    def Update(self, permutation: Permutation) -> None:
        """Aktualisiert die Ausgangspermutation und löscht alte Moves und Bewertungen."""
        self.Permutation = permutation

        self.Moves.clear()
        self.MoveSolutions.clear()

    def LocalSearch(self, neighborhoodEvaluationStrategy: str, solution: Solution) -> None:
        """Wendet die Nachbarschaft wiederholt an, bis kein verbessernder Move gefunden wird."""
        hasSolutionImproved = True

        while hasSolutionImproved:
            self.Update(solution.Permutation)
            self.DiscoverMoves()
            self.EvaluateMoves(neighborhoodEvaluationStrategy)

            bestNeighborhoodSolution = self.MakeBestMove()

            if bestNeighborhoodSolution.Makespan < solution.Makespan:
                # print("New best solution has been found!")
                print(bestNeighborhoodSolution)

                self.SolutionPool.AddSolution(bestNeighborhoodSolution)

                solution.Permutation = bestNeighborhoodSolution.Permutation
                solution.Makespan = bestNeighborhoodSolution.Makespan
            else:
                print(f"Reached local optimum of {self.Type} neighborhood. Stop local search.")
                hasSolutionImproved = False        

class SwapMove:
    """Tauscht zwei Elemente einer Permutation."""

    def __init__(self, initialPermutation: Permutation, indexA: int, indexB: int) -> None:
        """Erzeugt eine neue Permutation, in der die Positionen indexA und indexB getauscht sind."""
        self.Permutation = list(initialPermutation) # create a copy of the permutation
        self.IndexA = indexA
        self.IndexB = indexB

        self.Permutation[indexA] = initialPermutation[indexB]
        self.Permutation[indexB] = initialPermutation[indexA]
        
class SwapNeighborhood(BaseNeighborhood):
    """Enthält alle paarweisen Swap-Moves für eine Permutation."""

    def __init__(
        self,
        inputData: InputData,
        initialPermutation: Permutation,
        evaluationLogic: EvaluationLogic,
        solutionPool: SolutionPool,
    ) -> None:
        """Initialisiert die Swap-Nachbarschaft."""
        super().__init__(inputData, initialPermutation, evaluationLogic, solutionPool)

        self.Type = 'Swap'

    def DiscoverMoves(self) -> None:
        """Erzeugt alle n über 2 möglichen Swap-Moves."""
        for i in range(len(self.Permutation)):
            for j in range(len(self.Permutation)):
                if i < j:
                    swapMove = SwapMove(self.Permutation, i, j)
                    self.Moves.append(swapMove)

class InsertionMove:
    """Verschiebt ein Element einer Permutation an eine andere Position."""

    def __init__(self, initialPermutation: Permutation, indexA: int, indexB: int) -> None:
        """Erzeugt eine neue Permutation, in der das Element indexA bei indexB eingefügt wird."""
        self.Permutation = [] # create a copy of the permutation
        self.IndexA = indexA
        self.IndexB = indexB

        for k in range(len(initialPermutation)):
            if k == indexA:
                continue

            self.Permutation.append(initialPermutation[k])

        self.Permutation.insert(indexB, initialPermutation[indexA])

class InsertionNeighborhood(BaseNeighborhood):
    """Enthält alle zulässigen Insertion-Moves für eine Permutation."""

    def __init__(
        self,
        inputData: InputData,
        initialPermutation: Permutation,
        evaluationLogic: EvaluationLogic,
        solutionPool: SolutionPool,
    ) -> None:
        """Initialisiert die Insertion-Nachbarschaft."""
        super().__init__(inputData, initialPermutation, evaluationLogic, solutionPool)

        self.Type = 'Insertion'

    def DiscoverMoves(self) -> None:
        """Erzeugt alle Insertion-Moves außer wirkungslosen Direktverschiebungen."""
        for i in range(len(self.Permutation)):
            for j in range(len(self.Permutation)):
                if i == j or i == j + 1:
                    continue

                insertionMove = InsertionMove(self.Permutation, i, j)
                self.Moves.append(insertionMove)
                
