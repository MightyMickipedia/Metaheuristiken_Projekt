from __future__ import annotations

from OutputData import *
from InputData import *
import EvaluationLogic
import numpy as np


class ConstructiveHeuristics:
    """Erzeugt Startlösungen mit konstruktiven Heuristiken."""

    def __init__(
        self,
        evaluationLogic: EvaluationLogic.EvaluationLogic,
        solutionPool: SolutionPool,
        rng: np.random.Generator | None = None,
    ) -> None:
        """Initialisiert die Heuristiken mit Bewertung, Lösungspool und Zufallsgenerator."""
        self.EvaluationLogic = evaluationLogic
        self.SolutionPool = solutionPool
        self.RNG = rng if rng is not None else np.random.default_rng()


    def BinPerItem(self, data: InputData) -> Solution: # Jedes Item wird in einen eigenen Bin platziert
        """Erzeugt eine Lösung, in der jedes Item einem eigenen Bin zugeordnet wird."""
        allocation = dict()
        itemList = data.InputItems

        for item in itemList:
          allocation[item.itemId] = item.itemId

        tmpsolution = Solution(allocation)

        self.EvaluationLogic.CalculateNumberOfBins(tmpsolution)
        return tmpsolution



    def Run(self, inputData: InputData, solutionMethod: str, rng: np.random.Generator) -> None: # Ausführung der Constructive Heuristics
        """Führt die gewählte konstruktive Heuristik aus und speichert die Lösung."""
        print('Generating an initial solution according to ' + solutionMethod + '.')

        if solutionMethod == 'BPI':
            solution = self.BinPerItem(inputData)
        else:
            print('Unknown constructive solution method: ' + solutionMethod + '.')

        self.SolutionPool.AddSolution(solution)
