from __future__ import annotations

from OutputData import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from InputData import InputData


class EvaluationLogic:
    """Berechnet Bewertungskennzahlen für Lösungen."""

    def __init__(self, inputData: InputData) -> None:
        """Initialisiert die Bewertungslogik mit den Eingabedaten."""
        self.InputData = inputData


    def CalculateNumberOfBins(self, solution: Solution) -> None: # Berechnung der Bin Anzahl --> einziges Entschiedungskriterium
        """Berechnet Anzahl und Gewichte der verwendeten Bins einer Lösung."""
        Bins = {}
        allocation = solution.Allocation

        for itemId, binId in allocation.items():
            if binId not in Bins:
                Bins[binId] = 0
            Bins[binId] += self.InputData.InputItems[itemId].weight

        solution.NumberOfBins = len(set(allocation.values()))
        solution.Allocation = allocation
        Bins = {key: Bins[key] for key in sorted(Bins.keys())}
        solution.Bins = Bins
