"""
File Filtering Utilities

Provides centralized filtering for macOS metadata files and other exclusions.

Author: Philipp Kaintoch
Date: 2025-11-18
Version: 2.2.0
"""

from pathlib import Path
from typing import List, Iterator


def is_macos_metadata_file(path: Path) -> bool:
    """
    Check if a path represents a macOS metadata file.

    macOS creates hidden metadata files starting with '._' (AppleDouble format)
    when files are copied to non-Mac file systems. These files contain resource
    fork data and extended attributes, not actual data.

    Parameters:
    -----------
    path : Path
        File or directory path to check

    Returns:
    --------
    bool : True if the path is a macOS metadata file

    Examples:
    ---------
    >>> is_macos_metadata_file(Path("._Volume.csv"))
    True
    >>> is_macos_metadata_file(Path("Volume.csv"))
    False
    >>> is_macos_metadata_file(Path("._1h_LPS_1_ER_Statistics"))
    True
    """
    return path.name.startswith('._')


def filter_metadata_files(paths: Iterator[Path]) -> List[Path]:
    """
    Filter out macOS metadata files from a collection of paths.

    This function should be used consistently across all file discovery
    operations to ensure data integrity and prevent processing of metadata
    files.

    Parameters:
    -----------
    paths : Iterator[Path]
        Iterator of Path objects (e.g., from glob or directory listing)

    Returns:
    --------
    List[Path] : Filtered list with metadata files removed

    Examples:
    ---------
    >>> files = Path(".").glob("*.csv")
    >>> clean_files = filter_metadata_files(files)

    >>> from pathlib import Path
    >>> folders = [Path("._test"), Path("real_folder"), Path("._another")]
    >>> filter_metadata_files(iter(folders))
    [PosixPath('real_folder')]

    Notes:
    ------
    - Converts iterator to list for easier handling
    - Preserves original order of non-metadata files
    - Safe to use with empty iterators
    """
    return [p for p in paths if not is_macos_metadata_file(p)]
