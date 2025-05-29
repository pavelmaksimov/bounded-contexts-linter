from pathlib import Path
from bounded_contexts_linter.main import (
    check_imports_isolation,
    load_bounded_contexts,
    check_overlapping_modules,
)


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


def test_no_overlapping_modules():
    project_path = Path(__file__).parent / "example" / "project"
    config_path = Path(__file__).parent / "example" / "bounded-contexts.toml"

    bounded_contexts = load_bounded_contexts(str(config_path))

    overlaps = check_overlapping_modules(str(project_path), bounded_contexts)

    assert overlaps == []


def test_overlapping_modules():
    project_path = Path(__file__).parent / "example" / "project"
    config_path = Path(__file__).parent / "example" / "bounded-contexts.toml"

    bounded_contexts = load_bounded_contexts(str(config_path))
    bounded_contexts["crm"].append("project.domains.sales.models")

    overlaps = check_overlapping_modules(str(project_path), bounded_contexts)

    assert len(overlaps) == 1

    context1, context2, overlap = overlaps[0]

    assert (context1 == "crm" and context2 == "sales") or (
        context1 == "sales" and context2 == "crm"
    )
    assert overlap == {"project.domains.sales.models"}


def test_overlapping_modules_excludes_shared_contexts():
    project_path = Path(__file__).parent / "example" / "project"
    config_path = Path(__file__).parent / "example" / "bounded-contexts.toml"

    bounded_contexts = load_bounded_contexts(str(config_path))
    bounded_contexts["crm"].append("project.domains.user.models")  # Overlap with sharedkernel
    bounded_contexts["sales"].append("project.domains.crm.port")  # Overlap with sharedscope

    overlaps = check_overlapping_modules(str(project_path), bounded_contexts)

    assert overlaps == []
