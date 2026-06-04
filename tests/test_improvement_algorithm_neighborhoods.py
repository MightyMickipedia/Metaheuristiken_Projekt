import sys
from pathlib import Path

import numpy as np
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = PROJECT_ROOT / "Hausaufgabe" / "Code"

if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from EvaluationLogic import EvaluationLogic
from ImprovementAlgorithm import SimulatedAnnealing
from Neighbourhood import EmptyBinNeighborhood, RepackItemNeighborhood
from OutputData import Solution, SolutionPool


class FakeBinCapacity:
    def __init__(self, capacity):
        self.capacity = capacity


class FakeItem:
    def __init__(self, weight):
        self.weight = weight


class FakeInputData:
    def __init__(self):
        self.InputBinCapacity = FakeBinCapacity(10)
        self.InputItems = [
            FakeItem(5),
            FakeItem(3),
            FakeItem(2),
        ]


def initialized_algorithm(neighborhood_types=None, **parameters):
    input_data = FakeInputData()
    algorithm = SimulatedAnnealing(input_data, neighborhoodTypes=neighborhood_types, **parameters)
    algorithm.Initialize(
        EvaluationLogic(input_data),
        SolutionPool(),
        np.random.default_rng(2),
    )
    return algorithm


def start_solution():
    solution = Solution({0: 0, 1: 1, 2: 1})
    return solution


def test_default_neighborhood_creates_random_repack_neighbor():
    algorithm = initialized_algorithm()

    neighbor = algorithm.CreateRandomNeighbor(start_solution())

    assert isinstance(neighbor, Solution)
    assert neighbor.NumberOfBins < np.inf


def test_repack_item_alias_is_supported():
    algorithm = initialized_algorithm(["RepackItem"])

    neighbor = algorithm.CreateRandomNeighbor(start_solution())

    assert isinstance(neighbor, Solution)
    assert neighbor.NumberOfBins < np.inf


def test_empty_bin_neighborhood_can_be_created():
    algorithm = initialized_algorithm()

    neighborhood = algorithm.CreateNeighborhood("EmptyBin", start_solution())

    assert isinstance(neighborhood, EmptyBinNeighborhood)


def test_unknown_neighborhood_type_raises_clear_value_error():
    algorithm = initialized_algorithm()

    with pytest.raises(ValueError, match="Supported types"):
        algorithm.CreateNeighborhood("UnknownType", start_solution())


def test_random_neighbor_uses_only_first_configured_neighborhood():
    algorithm = initialized_algorithm(["RepackItems", "UnknownType"])

    neighbor = algorithm.CreateRandomNeighbor(start_solution())

    assert isinstance(neighbor, Solution)
    assert neighbor.NumberOfBins < np.inf


def test_number_of_moves_is_passed_to_neighborhood(monkeypatch):
    discovered_number_of_moves = []

    def discover_moves(self, numberOfMoves=50):
        discovered_number_of_moves.append(numberOfMoves)
        self.Moves = []

    monkeypatch.setattr(RepackItemNeighborhood, "DiscoverMoves", discover_moves)
    algorithm = initialized_algorithm(numberOfMoves=7)

    neighbor = algorithm.CreateRandomNeighbor(start_solution())

    assert neighbor is not None
    assert discovered_number_of_moves == [7]
