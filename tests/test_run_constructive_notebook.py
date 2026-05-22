import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = PROJECT_ROOT / "Hausaufgabe" / "Code"
NOTEBOOK_PATH = CODE_DIR / "RunConstructive.ipynb"


@pytest.fixture(scope="module")
def notebook_namespace():
    """Execute the notebook code cells once and return their namespace."""

    if str(CODE_DIR) not in sys.path:
        sys.path.insert(0, str(CODE_DIR))

    namespace = {"__name__": "__notebook_test__"}
    assert NOTEBOOK_PATH.exists(), f"Expected notebook at {NOTEBOOK_PATH}, but it does not exist."

    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))

    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] != "code":
            continue

        source = "".join(cell["source"])
        try:
            exec(compile(source, f"{NOTEBOOK_PATH}:cell_{index}", "exec"), namespace)
        except Exception as error:
            pytest.fail(
                f"Notebook code cell {index} could not be executed. "
                f"Fix this cell before testing the notebook functions. Original error: {error}"
            )

    return namespace


def make_input_data(weights, capacity):
    """Create the smallest data object needed by the notebook functions."""

    return SimpleNamespace(
        InputItems=[
            SimpleNamespace(itemId=item_id, weight=weight)
            for item_id, weight in enumerate(weights)
        ],
        InputBinCapacity=SimpleNamespace(capacity=capacity),
    )


def test_simulated_annealing_parameters_have_intuitive_defaults(notebook_namespace):
    """The default SA parameters should be usable without extra setup."""

    parameters = notebook_namespace["SimulatedAnnealingParameters"]()

    assert parameters.startTemperature > parameters.minTemperature, (
        "startTemperature must be larger than minTemperature so the cooling loop can run."
    )
    assert 0 < parameters.coolingRate < 1, (
        "coolingRate must be between 0 and 1 so the temperature decreases over time."
    )
    assert parameters.maxIterations > 0, "maxIterations must allow at least one SA step."
    assert parameters.iterationsPerTemperature > 0, (
        "iterationsPerTemperature must be positive to avoid division or loop errors."
    )
    assert parameters.maxIterationsWithoutImprovement > 0, (
        "maxIterationsWithoutImprovement must be positive so stagnation can be detected."
    )


def test_documentation_checklist_contains_required_assignment_terms(notebook_namespace):
    """The notebook checklist should cover all terms required by the assignment."""

    checklist_text = " ".join(notebook_namespace["documentation_checklist"]()).lower()

    required_terms = [
        "klassifizierung",
        "suchoperatoren",
        "diversifizierung",
        "intensivierung",
        "terminierungskriterium",
        "parameter",
        "schwierigkeiten",
    ]

    for term in required_terms:
        assert term in checklist_text, (
            f"The documentation checklist should mention '{term}' because it is required "
            "by Aufgabenstellung.pdf."
        )


def test_acceptance_probability_accepts_better_solutions(notebook_namespace):
    """Better neighbors should always be accepted."""

    try:
        probability = notebook_namespace["acceptance_probability"](delta=-1, temperature=10)
    except NotImplementedError:
        pytest.fail(
            "acceptance_probability is still a stub. Implement: return 1.0 for delta <= 0."
        )

    assert probability == pytest.approx(1.0), (
        "A better neighbor has delta <= 0 and should always have acceptance probability 1.0."
    )


def test_acceptance_probability_rejects_impossible_temperature(notebook_namespace):
    """A non-positive temperature should not accept worse solutions."""

    try:
        probability = notebook_namespace["acceptance_probability"](delta=2, temperature=0)
    except NotImplementedError:
        pytest.fail(
            "acceptance_probability is still a stub. Implement a safe result for temperature <= 0."
        )

    assert probability == pytest.approx(0.0), (
        "For worse neighbors and temperature <= 0, the acceptance probability should be 0.0."
    )


def test_acceptance_probability_uses_sa_formula(notebook_namespace):
    """Worse neighbors should be accepted according to exp(-delta / temperature)."""

    try:
        probability = notebook_namespace["acceptance_probability"](delta=2, temperature=10)
    except NotImplementedError:
        pytest.fail(
            "acceptance_probability is still a stub. Implement math.exp(-delta / temperature)."
        )

    assert probability == pytest.approx(0.818730753), (
        "For delta=2 and temperature=10, acceptance_probability should be exp(-2 / 10)."
    )


def test_should_accept_neighbor_always_accepts_improvement(notebook_namespace):
    """The SA acceptance decision should always accept improvements."""

    rng = notebook_namespace["np"].random.default_rng(2)

    try:
        accepted = notebook_namespace["should_accept_neighbor"](delta=-1, temperature=1, rng=rng)
    except NotImplementedError:
        pytest.fail(
            "should_accept_neighbor is still a stub. Implement unconditional acceptance for delta <= 0."
        )

    assert accepted is True, "An improving neighbor must always be accepted."


def test_is_solution_feasible_detects_feasible_solution(notebook_namespace):
    """A solution whose bins stay below capacity should be feasible."""

    data = make_input_data(weights=[4, 3, 2], capacity=7)
    solution = notebook_namespace["Solution"]({0: 0, 1: 0, 2: 1})

    try:
        feasible = notebook_namespace["is_solution_feasible"](data, solution)
    except NotImplementedError:
        pytest.fail(
            "is_solution_feasible is still a stub. Sum weights per bin and compare them to capacity."
        )

    assert feasible is True, "Bins weigh 7 and 2, so this solution should be feasible."


def test_is_solution_feasible_detects_capacity_violation(notebook_namespace):
    """A solution whose bin exceeds capacity should be infeasible."""

    data = make_input_data(weights=[4, 3, 2], capacity=6)
    solution = notebook_namespace["Solution"]({0: 0, 1: 0, 2: 1})

    try:
        feasible = notebook_namespace["is_solution_feasible"](data, solution)
    except NotImplementedError:
        pytest.fail(
            "is_solution_feasible is still a stub. It should return False when any bin is overweight."
        )

    assert feasible is False, "Bin 0 weighs 7 with capacity 6, so this solution must be infeasible."


def test_normalize_bin_ids_removes_gaps(notebook_namespace):
    """Bin IDs should be compact and 0-indexed after normalization."""

    solution = notebook_namespace["Solution"]({0: 5, 1: 5, 2: 9})

    try:
        normalized = notebook_namespace["normalize_bin_ids"](solution)
    except NotImplementedError:
        pytest.fail(
            "normalize_bin_ids is still a stub. Map used bin IDs to compact IDs 0, 1, 2, ..."
        )

    assert normalized.Allocation == {0: 0, 1: 0, 2: 1}, (
        "Old bin IDs 5 and 9 should be remapped to compact 0-indexed IDs 0 and 1."
    )
    assert normalized.NumberOfBins == 2, "NumberOfBins should match the number of used bins."


def test_generate_move_neighbor_returns_feasible_neighbor(notebook_namespace):
    """MoveItem should return a feasible Solution object."""

    data = make_input_data(weights=[4, 3, 2], capacity=7)
    solution = notebook_namespace["Solution"]({0: 0, 1: 0, 2: 1})
    rng = notebook_namespace["np"].random.default_rng(2)

    try:
        neighbor = notebook_namespace["generate_move_neighbor"](data, solution, rng)
    except NotImplementedError:
        pytest.fail(
            "generate_move_neighbor is still a stub. Move one item to another feasible bin or a new bin."
        )

    assert isinstance(neighbor, notebook_namespace["Solution"]), (
        "generate_move_neighbor should return a Solution object."
    )

    try:
        feasible = notebook_namespace["is_solution_feasible"](data, neighbor)
    except NotImplementedError:
        pytest.fail(
            "generate_move_neighbor returned a Solution, but is_solution_feasible is still a stub. "
            "Implement feasibility checking so this test can verify the neighbor."
        )

    assert feasible, (
        "MoveItem must not return a neighbor that violates bin capacity."
    )


def test_save_solution_csv_creates_expected_file(notebook_namespace, tmp_path):
    """The CSV export should create a Solution-<instance>.csv file."""

    solution = notebook_namespace["Solution"]({0: 0, 1: 1, 2: 1})
    instance_path = "../Data/example.json"

    try:
        output_path = notebook_namespace["save_solution_csv"](
            instance_path,
            solution,
            outputFolder=str(tmp_path),
        )
    except NotImplementedError:
        pytest.fail(
            "save_solution_csv is still a stub. Create the output folder and write the item-bin mapping."
        )

    output_path = Path(output_path)
    assert output_path.exists(), "save_solution_csv should return the path of an existing CSV file."
    assert output_path.name == "Solution-example.csv", (
        "The output file should follow the required naming scheme Solution-<instance>.csv."
    )
    assert output_path.read_text(encoding="utf-8").strip(), (
        "The solution CSV should not be empty; it must contain the item-to-bin assignment."
    )
