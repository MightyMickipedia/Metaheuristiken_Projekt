from __future__ import annotations

#from Neigborhood import *
import math
from copy import deepcopy
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from EvaluationLogic import EvaluationLogic
    from InputData import InputData
    from OutputData import SolutionPool

""" Basisklasse für Improvement Algorithms """ 
class ImprovementAlgorithm:
    """Basisklasse für Verbesserungsalgorithmen."""

    def __init__(self, inputData: InputData, neighborhoodEvaluationStrategy: str = 'FirstImprovement', neighborhoodTypes: list[str] = ['RepackBins']) -> None:
        """Initialisiert gemeinsame Daten und Einstellungen für Verbesserungsverfahren."""
        self.InputData = inputData

        self.EvaluationLogic = {}
        self.SolutionPool = {}

        self.NeighborhoodEvaluationStrategy = neighborhoodEvaluationStrategy
        self.NeighborhoodTypes = neighborhoodTypes
        self.Neighborhoods = {}

    def Initialize(self, evaluationLogic: EvaluationLogic, solutionPool: SolutionPool, rng: Any) -> None:
        """Setzt Bewertungslogik, Lösungspool und Zufallsgenerator für den Algorithmus."""
        self.EvaluationLogic = evaluationLogic
        self.SolutionPool = solutionPool
        self.RNG = rng


""" Simulated Annealing or Tabu Search or Variable Neighborhood Search or ..."""
