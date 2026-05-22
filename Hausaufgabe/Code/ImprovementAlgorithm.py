#from Neigborhood import *
import math
from copy import deepcopy

""" Basisklasse für Improvement Algorithms """ 
class ImprovementAlgorithm:
    def __init__(self, inputData, neighborhoodEvaluationStrategy = 'FirstImprovement', neighborhoodTypes = ['RepackBins']):
        self.InputData = inputData

        self.EvaluationLogic = {}
        self.SolutionPool = {}

        self.NeighborhoodEvaluationStrategy = neighborhoodEvaluationStrategy
        self.NeighborhoodTypes = neighborhoodTypes
        self.Neighborhoods = {}

    def Initialize(self, evaluationLogic, solutionPool, rng):
        self.EvaluationLogic = evaluationLogic
        self.SolutionPool = solutionPool
        self.RNG = rng


""" Simulated Annealing or Tabu Search or Variable Neighborhood Search or ..."""
