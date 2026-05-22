from __future__ import annotations

from InputData import *
from OutputData import *
from ConstructiveHeuristics import *
from ImprovementAlgorithm import *
from EvaluationLogic import *



class Solver:
    """Koordiniert Konstruktion, Verbesserung und Prüfung einer Lösung."""

    def __init__(self, inputData: InputData) -> None:
        """Initialisiert den Solver mit Eingabedaten und benötigten Hilfskomponenten."""
        self.InputData = inputData

        self.Seed = 2
        self.RNG = np.random.default_rng(self.Seed)
        self.EvaluationLogic = EvaluationLogic(inputData)
        self.SolutionPool = SolutionPool()

        self.ConstructiveHeuristics = ConstructiveHeuristics(self.EvaluationLogic, self.SolutionPool, self.RNG)


    def ConstructionPhase(self, constructiveSolutionMethod: str) -> Solution: # Erstellung der Startlösung
        """Erzeugt eine Startlösung mit der angegebenen konstruktiven Methode."""
        self.ConstructiveHeuristics.Run(self.InputData, constructiveSolutionMethod, self.RNG)

        bestInitalSolution = self.SolutionPool.GetLowestNumberOfBinsSolution()

        print(f"Constructive solution found: {bestInitalSolution} \n")
        return bestInitalSolution


    def ImprovementPhase(self, startSolution: Solution, algorithm: ImprovementAlgorithm) -> None: # Ausführung der Verbesserungsphase
        """Führt den übergebenen Verbesserungsalgorithmus auf der Startlösung aus."""
        algorithm.Initialize(self.EvaluationLogic, self.SolutionPool, self.RNG)
        bestSolution = algorithm.Run(startSolution)

        print(f"Best found Solution: {bestSolution}\n")

 
    def Run(self, constructiveSolutionMethod: str, algorithm: ImprovementAlgorithm) -> Solution: # Ausführen des Solvers
        """Führt den vollständigen Lösungsablauf aus und gibt die beste Lösung zurück."""
        
        startSolution = self.ConstructionPhase(constructiveSolutionMethod)
        self.ImprovementPhase(startSolution, algorithm)
        bestSolution = self.SolutionPool.GetLowestNumberOfBinsSolution()
        bestSolution.FeasibilityCheck(self.InputData)


        return bestSolution
