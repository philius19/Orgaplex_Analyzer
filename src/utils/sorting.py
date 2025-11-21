"""
Sorting Utilities for Orgaplex-Analyzer

Provides natural numerical sorting for cell identifiers and labels.

Author: Philipp Kaintoch
Date: 2025-11-18
Version: 2.2.0
"""

import re
from typing import List, Union


def natural_sort_key(text: str) -> List:
    """
    Generate a key for natural (numerical) sorting.

    Converts numeric substrings to integers for proper numerical ordering.
    Ensures numerical components are ordered correctly (e.g., "Cell 2" before "Cell 10").

    Parameters:
    -----------
    text : str
        String to generate sort key for

    Returns:
    --------
    List : Sort key with integers for numerical parts, strings otherwise

    Examples:
    ---------
    >>> sorted(["1h LPS 1", "1h LPS 10", "1h LPS 2"], key=natural_sort_key)
    ['1h LPS 1', '1h LPS 2', '1h LPS 10']

    >>> sorted(["control_10", "control_2", "control_1"], key=natural_sort_key)
    ['control_1', 'control_2', 'control_10']

    >>> sorted(["IgE 1", "1h LPS 1", "2h LPS 1"], key=natural_sort_key)
    ['1h LPS 1', '2h LPS 1', 'IgE 1']

    Notes:
    ------
    - Non-numeric parts are converted to lowercase for case-insensitive sorting
    - Empty strings sort before non-empty strings
    - Works with mixed alphanumeric strings
    - Ensures type consistency to avoid comparison errors
    """
    def convert_to_int_or_lower(substring: str):
        """Convert numeric strings to (0, int), others to (1, lowercase)."""
        # Use tuple with type indicator to ensure consistent comparison
        # Numbers (type 0) sort before strings (type 1) at same position
        if substring.isdigit():
            return (0, int(substring))
        else:
            return (1, substring.lower())

    # Split on digit boundaries, keeping digits as separate tokens
    # re.split with capturing group keeps the delimiters
    parts = re.split(r'(\d+)', text)

    # Convert each part to comparable tuple
    # Filter out empty strings from split
    return [convert_to_int_or_lower(part) for part in parts if part]


def sort_cell_ids(cell_ids: List[str]) -> List[str]:
    """
    Sort cell IDs using natural numerical sorting.

    Parameters:
    -----------
    cell_ids : List[str]
        List of cell identifier strings

    Returns:
    --------
    List[str] : Sorted list of cell IDs in natural order

    Raises:
    -------
    TypeError : If cell_ids is not a list or contains non-string elements

    Examples:
    ---------
    >>> sort_cell_ids(["1h LPS 10", "1h LPS 2", "1h LPS 1"])
    ['1h LPS 1', '1h LPS 2', '1h LPS 10']

    >>> sort_cell_ids(["2h LPS IFNY 5", "1h LPS 10", "1h LPS 2"])
    ['1h LPS 2', '1h LPS 10', '2h LPS IFNY 5']

    >>> sort_cell_ids([])
    []

    Notes:
    ------
    - Empty list returns empty list
    - Handles None values by raising TypeError (fail-fast)
    - Case-insensitive sorting
    - Preserves original strings (doesn't modify them)
    """
    if not isinstance(cell_ids, list):
        raise TypeError(f"Expected list, got {type(cell_ids).__name__}")

    if not cell_ids:
        return []

    # Validate all elements are strings
    if not all(isinstance(item, str) for item in cell_ids):
        raise TypeError("All cell IDs must be strings")

    return sorted(cell_ids, key=natural_sort_key)
