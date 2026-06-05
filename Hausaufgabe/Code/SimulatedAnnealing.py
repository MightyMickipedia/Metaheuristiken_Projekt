from __future__ import annotations

import csv
import os
import time

from Solver import *


START_HEURISTIC = 'FAMAP'

SA_PARAMETERS = {
    'neighborhoodTypes': ['EmptyBin'],
    'temperature': 0.95,
    'coolingSpeed': 0.5,
    'threshold': 1e-2,
    'maxMarkovLength': 200,
    'numberOfMoves': 100,
}

CODE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


def load_data_sets():
    files = Files()

    try:
        paths = sorted(files.GetFiles())
    except FileNotFoundError:
        print("Kein Data-Ordner gefunden. Lege ../Data an oder passe InputData.Files an.")
        return []

    fileNames = [path.split('/')[-1] for path in paths]
    print(f"Alle Dateien im Zielordner sind: {fileNames} \n")

    dataSets = []
    for path in paths:
        print("________________________________________________________________________________________")
        print(f"Lade Instanz: {path.split('/')[-1]}")

        inputPath = path if os.path.isabs(path) else os.path.abspath(os.path.join(CODE_DIRECTORY, path))
        dataSets.append(InputData(inputPath))

    return dataSets


def make_constructive_results(dataSets):
    constructiveResults = []

    for data in dataSets:
        print("________________________________________________________________________________________")
        print(f"Konstruktive Phase fuer: {data.filename}")

        startTime = time.time()
        solver = Solver(data)
        startSolution = solver.ConstructionPhase(START_HEURISTIC)
        startSolution.FeasibilityCheckOutput(data)

        constructiveResults.append({
            'path': data.path,
            'instance': data.filename,
            'data': data,
            'constructiveHeuristic': START_HEURISTIC,
            'startSolution': startSolution,
            'constructiveRuntime': time.time() - startTime,
        })

    return constructiveResults


def run_simulated_annealing(constructiveResults):
    finalResults = []

    for result in constructiveResults:
        data = result['data']

        algorithm = SimulatedAnnealing(
            inputData=data,
            **SA_PARAMETERS,
        )
        solver = Solver(data)
        startTime = time.time()
        finalSolution = solver.Run(result['constructiveHeuristic'], algorithm)
        runtime = time.time() - startTime
        print(f"Number of bins: {finalSolution.NumberOfBins}")

        result['finalSolution'] = finalSolution
        result['improvementRuntime'] = runtime
        finalResults.append(result)

    return finalResults


def calculate_bin_weights(solution, data):
    binWeights = {binId: 0 for binId in sorted(set(solution.Allocation.values()))}

    for itemId, binId in solution.Allocation.items():
        binWeights[binId] += data.InputItems[itemId].weight

    return binWeights


def is_feasible(solution, data):
    binWeights = calculate_bin_weights(solution, data)
    capacity = data.InputBinCapacity.capacity
    return all(weight <= capacity for weight in binWeights.values())


def write_solution_csv(solution, data, outputFolder=None):
    if outputFolder is None:
        outputFolder = os.path.abspath(os.path.join(CODE_DIRECTORY, '..', 'Solutions'))

    os.makedirs(outputFolder, exist_ok=True)

    instanceName = os.path.splitext(data.filename)[0]
    outputPath = os.path.join(outputFolder, f'Solution-{instanceName}.csv')
    binIdMap = {binId: index for index, binId in enumerate(sorted(set(solution.Allocation.values())))}

    with open(outputPath, 'w', newline='') as outputFile:
        writer = csv.writer(outputFile)
        writer.writerow(['itemId', 'binId'])

        for itemId in sorted(solution.Allocation):
            writer.writerow([itemId, binIdMap[solution.Allocation[itemId]]])

    return outputPath


def print_results(finalResults):
    results = []

    for result in finalResults:
        data = result['data']
        finalSolution = result['finalSolution']
        feasible = finalSolution.FeasibilityCheck(data)
        solutionPath = write_solution_csv(finalSolution, data) if feasible else None

        if solutionPath is not None:
            print(f"Loesung gespeichert: {solutionPath}")
        else:
            print(f"Keine CSV geschrieben, da die Loesung fuer {result['instance']} nicht zulaessig ist.")

        results.append({
            'Instanz': result['instance'],
            'Konstruktionsheuristik': result['constructiveHeuristic'],
            'StartBins': result['startSolution'].NumberOfBins,
            'FinalBins': finalSolution.NumberOfBins,
            'Konstruktionszeit': round(result['constructiveRuntime'], 4),
            'Verbesserungszeit': round(result['improvementRuntime'], 4),
            'Erlaubt': feasible,
            'SolutionFile': solutionPath,
        })

    columns = ['Instanz', 'Konstruktionsheuristik', 'StartBins', 'FinalBins', 'Konstruktionszeit', 'Verbesserungszeit', 'Erlaubt', 'SolutionFile']
    columnWidths = {
        column: max([len(column), *(len(str(row[column])) for row in results)])
        for column in columns
    }

    header = ' | '.join(column.ljust(columnWidths[column]) for column in columns)
    separator = '-+-'.join('-' * columnWidths[column] for column in columns)
    print(header)
    print(separator)

    for row in results:
        print(' | '.join(str(row[column]).ljust(columnWidths[column]) for column in columns))

    return results


def main():
    dataSets = load_data_sets()
    constructiveResults = make_constructive_results(dataSets)
    finalResults = run_simulated_annealing(constructiveResults)
    return print_results(finalResults)


if __name__ == '__main__':
    main()
