from OutputData import *


class EvaluationLogic:
    def __init__(self, inputData):
        self.InputData = inputData


    def CalculateNumberOfBins(self, solution): # Berechnung der Bin Anzahl --> einziges Entschiedungskriterium
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