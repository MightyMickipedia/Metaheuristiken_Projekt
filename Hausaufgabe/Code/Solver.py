from InputData import *
from OutputData import *
from ConstructiveHeuristics import *
from ImprovementAlgorithm import *
from EvaluationLogic import *



class Solver:

    def __init__(self, inputData):
        self.InputData = inputData

        self.Seed = 2
        self.RNG = np.random.default_rng(self.Seed)
        self.EvaluationLogic = EvaluationLogic(inputData)
        self.SolutionPool = SolutionPool()

        self.ConstructiveHeuristics = ConstructiveHeuristics(self.EvaluationLogic, self.SolutionPool, self.RNG)


    def ConstructionPhase(self, constructiveSolutionMethod): # Erstellung der Startlösung
        self.ConstructiveHeuristics.Run(self.InputData, constructiveSolutionMethod, self.RNG)

        bestInitalSolution = self.SolutionPool.GetLowestNumberOfBinsSolution()

        print(f"Constructive solution found: {bestInitalSolution} \n")
        return bestInitalSolution


    def ImprovementPhase(self, startSolution, algorithm): # Ausführung der Verbesserungsphase
        algorithm.Initialize(self.EvaluationLogic, self.SolutionPool, self.RNG)
        bestSolution = algorithm.Run(startSolution)

        print(f"Best found Solution: {bestSolution}\n")

 
    def Run(self, constructiveSolutionMethod, algorithm): # Ausführen des Solvers
        
        startSolution = self.ConstructionPhase(constructiveSolutionMethod)
        self.ImprovementPhase(startSolution, algorithm)
        bestSolution = self.SolutionPool.GetLowestNumberOfBinsSolution()
        bestSolution.FeasibilityCheck(self.InputData)


        return bestSolution
