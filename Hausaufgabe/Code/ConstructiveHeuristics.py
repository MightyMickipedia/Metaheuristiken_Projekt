from OutputData import *
from InputData import *
import EvaluationLogic


class ConstructiveHeuristics:
    def __init__(self, evaluationLogic, solutionPool, rng):
        self.EvaluationLogic = evaluationLogic
        self.SolutionPool = solutionPool
        self.RNG = rng


    def BinPerItem(self, data): # Jedes Item wird in einen eigenen Bin platziert
        allocation = dict()
        itemList = data.InputItems

        for item in itemList:
          allocation[item.itemId] = item.itemId

        tmpsolution = Solution(allocation)

        self.EvaluationLogic.CalculateNumberOfBins(tmpsolution)
        return tmpsolution



    def Run(self, inputData, solutionMethod, rng): # Ausführung der Constructive Heuristics
        print('Generating an initial solution according to ' + solutionMethod + '.')

        if solutionMethod == 'BPI':
            solution = self.BinPerItem(inputData)
        else:
            print('Unknown constructive solution method: ' + solutionMethod + '.')

        self.SolutionPool.AddSolution(solution)