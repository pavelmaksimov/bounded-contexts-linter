import fnmatch
from functools import lru_cache
from pathlib import Path
from typing import List, Set


@lru_cache(maxsize=500)
def match_pattern(module_name: str, pattern: str) -> bool:
    """
    Check if module name matches the given pattern.

    Args:
        module_name: Full module name (e.g., 'project.domains.crm.models')
        pattern: Pattern to match (e.g., "project.crm", "project.crm.*", "*.crm", "crm.*", "*.crm.*", "project.*.crm")

    Returns:
        True if the module name matches the pattern, False otherwise

    Examples for pattern
        "project.crm"
        "project.domains.crm"
        "project.domains.crm.*"
        "*.crm",
        "crm.*",
        "*.crm.*",
        "project.*.crm"
    """
    return fnmatch.fnmatch(module_name, pattern)


@lru_cache(maxsize=10)
def find_modules_in_directory(directory: str) -> List[str]:
    """
    Find all Python modules in the given directory and its subdirectories.

    Args:
        directory (str): Directory to search in.
        base_package (str): Base package name for the modules.

    Returns:
        List of module names.
    """
    modules = []
    root_path = Path(directory)

    for file_path in root_path.rglob("*.py"):
        relative_path = file_path.relative_to(root_path.parent)
        parts = list(relative_path.with_suffix("").parts)
        module_name = ".".join(parts)
        modules.append(module_name)

    return modules


def find_modules_by_patterns(directory: str, patterns: List[str]) -> Set[str]:
    """
    Find all modules in the given directory that match any of the patterns.

    Args:
        directory: Directory to search in
        patterns: List of patterns to match
        patterns example: [
            "project.crm",
            "project.domains.crm",
            "project.domains.crm.*",
            "*.crm",
            "crm.*",
            "*.crm.*",
            "project.*.crm",
        ]

    Returns:
        Set of module names that match any of the patterns
    """
    all_modules = find_modules_in_directory(directory)
    matching_modules = set()

    for module in all_modules:
        for pattern in patterns:
            # Check if the module name matches the pattern directly
            if match_pattern(module, pattern):
                matching_modules.add(module)
                break

    return matching_modules
