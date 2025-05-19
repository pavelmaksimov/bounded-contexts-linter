import ast
import tomllib
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

from bounded_contexts_linter.utils import find_modules_by_patterns, match_pattern


def load_bounded_contexts(config_path: str) -> Dict[str, List[str]]:
    """
    Load bounded contexts configuration from a TOML file.

    Args:
        config_path: Path to the configuration file

    Returns:
        Dictionary mapping context names to lists of patterns
    """
    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    contexts = {}
    for name in config["bounded-contexts"]["names"]:
        if name in config["bounded-contexts"]:
            contexts[name] = config["bounded-contexts"][name].get("contains", [])

    return contexts


def check_overlapping_modules(
    project_dir: str, bounded_contexts: Dict[str, List[str]]
) -> List[Tuple[str, str, Set[str]]]:
    """
    Check if modules of one pattern group overlap with modules of another pattern group.

    Args:
        project_dir: Directory to search for modules
        bounded_contexts: Dictionary mapping context names to lists of patterns

    Returns:
        List of tuples (context1, context2, overlapping_modules) where overlapping_modules
        is a set of module names that belong to both context1 and context2
    """
    # Find modules for each context
    context_modules = {}
    for context_name, patterns in bounded_contexts.items():
        context_modules[context_name] = find_modules_by_patterns(project_dir, patterns)

    if not all(bool(data) for data in context_modules.values()):
        raise ValueError(f"In {project_dir} no bounded contexts found, check your config")

    # Check for overlaps
    overlaps = []
    processed_pairs = set()

    for context1, modules1 in context_modules.items():
        for context2, modules2 in context_modules.items():
            # Skip self-comparison and already processed pairs
            if (
                context1 == context2
                or (context1, context2) in processed_pairs
                or (context2, context1) in processed_pairs
            ):
                continue

            # Skip if one of the contexts is sharedkernel or sharedscope
            if context1 in ["sharedkernel", "sharedscope"] or context2 in [
                "sharedkernel",
                "sharedscope",
            ]:
                continue

            # Find overlapping modules
            overlap = modules1.intersection(modules2)
            if overlap:
                overlaps.append((context1, context2, overlap))

            # Mark this pair as processed
            processed_pairs.add((context1, context2))

    return overlaps


def get_bounded_context_name_for_module(
    module_name: str, bounded_contexts: Dict[str, List[str]]
) -> Optional[str]:
    """
    Determine which bounded context a module belongs to.

    Args:
        module_name: Name of the module
        bounded_contexts: Dictionary mapping context names to lists of patterns

    Returns:
        Name of the context the module belongs to, or None if it doesn't belong to any context
    """
    for context_name, patterns in bounded_contexts.items():
        for pattern in patterns:
            if match_pattern(module_name, pattern):
                return context_name
    return None


def extract_imports(file_path: str) -> List[Tuple[str, int]]:
    """
    Extract all imports from a Python file.

    Args:
        file_path: Path to the Python file

    Returns:
        List of tuples (imported_module, line_number)
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    tree = ast.parse(content, filename=file_path)

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.append((name.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                imports.append((node.module, node.lineno))

    return imports


def check_imports_isolation(
    project_dir: str, bounded_contexts: Dict[str, List[str]]
) -> List[Tuple[str, int, str, str, str]]:
    """
    Check if imports between modules respect bounded contexts isolation.

    Args:
        project_dir: Directory to search for modules
        bounded_contexts: Dictionary mapping context names to lists of patterns

    Returns:
        List of tuples (file_path, line_number, importing_module, imported_module, violation_message)
        where violation_message describes the isolation violation
    """
    violations = []

    # Find all Python files in the project directory
    project_path = Path(project_dir)

    if not project_path.exists():
        raise ValueError(f"Project directory '{project_dir}' does not exist")

    # Process each Python file
    for file_path in project_path.rglob("*.py"):
        # Get the relative path from the project directory
        rel_path = file_path.relative_to(project_path.parent)
        # Convert the file path to a module name
        module_parts = list(rel_path.parent.parts)
        module_parts.append(rel_path.stem)
        module_name = ".".join(module_parts)

        # Get the context of the module
        bounded_context_name_for_module = get_bounded_context_name_for_module(
            module_name, bounded_contexts
        )
        if bounded_context_name_for_module is None:
            continue  # Skip modules that don't belong to any context

        # Extract imports from the file
        imports = extract_imports(str(file_path))

        # Check each import
        for imported_module, line_number in imports:
            # Skip relative imports
            if imported_module.startswith("."):
                continue

            # Get the context of the imported module
            bounded_context_name_for_import = get_bounded_context_name_for_module(
                imported_module, bounded_contexts
            )
            if bounded_context_name_for_import is None:
                continue  # Skip imports that don't belong to any context

            exclusion = {bounded_context_name_for_module, bounded_context_name_for_import} & {
                "sharedkernel",
                "sharedscope",
            }
            if exclusion:
                continue

            # Check if the import violates isolation
            if bounded_context_name_for_module != bounded_context_name_for_import:
                violation_message = (
                    f"Module from bounded context '{bounded_context_name_for_module}' imports module "
                    f"from bounded context '{bounded_context_name_for_import}', violating bounded contexts isolation"
                )
                violations.append(
                    (str(file_path), line_number, module_name, imported_module, violation_message)
                )

    return violations


def check_bounded_contexts(
    project_dir: str, config_path: Optional[str] = None
) -> List[Tuple[str, str, Set[str]]]:
    """
    Check if bounded contexts are properly isolated.

    Args:
        project_dir: Directory to search for modules
        config_path: Path to the configuration file (default: bounded-contexts.toml in current working directory)

    Returns:
        List of tuples (context1, context2, overlapping_modules) where overlapping_modules
        is a set of module names that belong to both context1 and context2
    """
    if config_path is None:
        config_path = Path.cwd() / "bounded-contexts.toml"

    contexts = load_bounded_contexts(config_path)
    return check_overlapping_modules(project_dir, contexts)
