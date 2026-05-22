import numpy as np
import os

class Solution:
    def __init__(self, allocation):
        self.Allocation = allocation
        self.NumberOfBins = np.inf 
        self.Bins = dict()

    def __str__(self):
        return f"The number of bins is {self.NumberOfBins}."
    
    def FeasibilityCheck(self, inputData): # Überprüfung der erzeugten Lösung mittels Feasibility Check

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
    def __init__(self):
        self._Solutions = []

    def AddSolution(self, newSolution):
        self._Solutions.append(newSolution)

    def ClearSolutionPool(self):
        self._Solutions = []

    def GetLowestNumberOfBinsSolution(self): # Hier wird die beste (aktuelle) Lösung ermittelt
        self._Solutions.sort(key=lambda solution: solution.NumberOfBins)
        return self._Solutions[0]

    @property
    def Solutions(self):
        return self._Solutions
