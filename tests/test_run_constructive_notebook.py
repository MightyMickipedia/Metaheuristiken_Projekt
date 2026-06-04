import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = PROJECT_ROOT / "Hausaufgabe" / "Code"
NOTEBOOK_PATH = CODE_DIR / "RunConstructive.ipynb"


def load_notebook():
    assert NOTEBOOK_PATH.exists(), f"Expected notebook at {NOTEBOOK_PATH}, but it does not exist."
    return json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))


def notebook_code() -> str:
    notebook = load_notebook()
    return "\n".join(
        "".join(cell["source"])
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
    )


def notebook_text() -> str:
    notebook = load_notebook()
    return "\n".join("".join(cell["source"]) for cell in notebook["cells"])


def test_notebook_code_cells_execute_without_data_folder():
    """The linear notebook scaffold should run even before instance data is present."""

    if str(CODE_DIR) not in sys.path:
        sys.path.insert(0, str(CODE_DIR))

    namespace = {"__name__": "__notebook_test__"}

    for index, cell in enumerate(load_notebook()["cells"]):
        if cell["cell_type"] != "code":
            continue

        source = "".join(cell["source"])
        exec(compile(source, f"{NOTEBOOK_PATH}:cell_{index}", "exec"), namespace)

    assert "dataSets" in namespace
    assert "constructiveResults" in namespace
    assert "finalResults" in namespace
    assert "results" in namespace


def test_notebook_uses_linear_execution_instead_of_function_scaffold():
    """Notebook steps should be written directly in cells, not as function wrappers."""

    code = notebook_code()

    removed_function_names = [
        "def load_problem_paths",
        "def print_available_instances",
        "def run_constructive_phase",
        "def evaluate_start_solution",
        "def is_solution_feasible",
        "def normalize_bin_ids",
        "def generate_move_neighbor",
        "def generate_swap_neighbor",
        "def generate_neighbor",
        "def acceptance_probability",
        "def should_accept_neighbor",
        "def run_simulated_annealing",
        "def save_solution_csv",
        "def append_result",
        "def print_results_table",
        "def solve_all_instances",
        "def documentation_checklist",
    ]

    for function_name in removed_function_names:
        assert function_name not in code

    assert "for data in dataSets:" in code
    assert "for result in constructiveResults:" in code
    assert "for result in finalResults:" in code


def test_notebook_comments_reference_implementation_files():
    """Notebook code comments should reference the implementation files."""

    code = notebook_code()

    expected_references = [
        "InputData.py",
        "ConstructiveHeuristics.py",
        "Solver.py",
        "ImprovementAlgorithm.py",
        "EvaluationLogic.py",
        "OutputData.py",
    ]

    for reference in expected_references:
        assert reference in code


def test_documentation_contains_required_assignment_terms():
    """The notebook documentation should cover the assignment vocabulary."""

    text = notebook_text().lower()

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
        assert term in text
