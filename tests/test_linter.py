from pathlib import Path
from bounded_contexts_linter.main import check_imports_isolation, load_bounded_contexts


def test_linter_detects_isolation_violation():
    project_path = Path(__file__).parent / "example" / "project"
    config_path = Path(__file__).parent / "example" / "bounded-contexts.toml"

    bounded_contexts = load_bounded_contexts(str(config_path))

    violations = check_imports_isolation(str(project_path), bounded_contexts)

    assert violations

    expected_file_path = str(project_path / "domains" / "crm" / "services.py")
    expected_line_number = 2
    expected_importing_module = "project.domains.crm.services"
    expected_imported_module = "project.domains.sales.models"
    expected_message = (
        "Module from bounded context 'crm' imports module from bounded context 'sales', "
        "violating bounded contexts isolation"
    )

    expected_violation = (
        expected_file_path,
        expected_line_number,
        expected_importing_module,
        expected_imported_module,
        expected_message,
    )

    assert expected_violation in violations
