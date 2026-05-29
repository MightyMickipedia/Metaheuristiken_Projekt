from __future__ import annotations

import numpy as np
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from InputData import InputData

class Solution:
    """Repräsentiert eine Zuordnung von Items zu Bins."""

    def __init__(self, allocation: dict[int, int]) -> None:
        """Initialisiert eine Lösung mit einer gegebenen Item-Bin-Zuordnung."""
        self.Allocation = allocation
        self.NumberOfBins = np.inf 
        self.Bins = dict()

    def __str__(self) -> str:
        """Gibt eine kurze Beschreibung der Lösung zurück."""
        return f"The number of bins is {self.NumberOfBins}."

    @property
    def NumberOfItems(self) -> int:
        """Gibt die Gesamtanzahl der Items in der Lösung zurück."""
        return len(self.Allocation)
    
    def FeasibilityCheck(self, inputData: InputData) -> None: # Überprüfung der erzeugten Lösung mittels Feasibility Check
        """Prüft, ob alle Bins die Kapazitätsgrenze einhalten."""

        finalAllocation = self.Allocation

        binWeights = {value: 0 for value in sorted(set(finalAllocation.values()))}

        for itemid, binid in finalAllocation.items():
            binWeights[binid] += inputData.InputItems[itemid].weight

        feasible = True
        for binID, weight in binWeights.items():
            binCapacity = inputData.InputBinCapacity.capacity
            if weight > binCapacity:
                print(f"The sum of weights ({weight}) in Bin {binID} exceeds the capacity of {binCapacity} units.")
                feasible = False

        if feasible:
            print("The allocation is feasible! All bins remain within their capacity.")
        else:
            print("The allocation is not feasible!")

        print("Maximum weight in a bin:", max(binWeights.values()))
        print("Minimum weight in a bin:", min(binWeights.values()))


class SolutionPool: # Lösungen innerhalb der Suche werden dem Solution Pool hinzugefügt
    """Verwaltet gefundene Lösungen während der Suche."""

    def __init__(self) -> None:
        """Initialisiert einen leeren Lösungspool."""
        self._Solutions = []

    def AddSolution(self, newSolution: Solution) -> None:
        """Fügt dem Lösungspool eine neue Lösung hinzu."""
        self._Solutions.append(newSolution)

    def ClearSolutionPool(self) -> None:
        """Entfernt alle Lösungen aus dem Lösungspool."""
        self._Solutions = []

    def GetLowestNumberOfBinsSolution(self) -> Solution: # Hier wird die beste (aktuelle) Lösung ermittelt
        """Gibt die Lösung mit der geringsten Anzahl an Bins zurück."""
        self._Solutions.sort(key=lambda solution: solution.NumberOfBins)
        return self._Solutions[0]

    @property
    def Solutions(self) -> list[Solution]:
        """Gibt alle gespeicherten Lösungen zurück."""
        return self._Solutions
