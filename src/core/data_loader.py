"""
Data Loader Module for Organelle Analysis

This module handles data extraction and validation from Imaris-generated
segmentation data. It provides a central control instance to ensure data
is loaded correctly.

Key Features:
- Automatic folder structure detection (LD vs non-LD datasets)
- Pattern-based organelle recognition (no hardcoded organelles)
- Robust file parsing with error handling
- Data validation and integrity checks

AUTHOR: Philipp Kaintoch
DATE: 2025-11-02
VERSION: 2.0.0
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import pandas as pd


class DataStructureError(Exception):
    """Raised when data structure doesn't match expected format."""
    pass


class DataLoader:
    """
    Handles loading and validation of organelle interaction data.

    This class is responsible for:
    - Detecting folder structure
    - Parsing cell IDs and organelle names
    - Loading distance measurement files
    - Validating data integrity
    """

    def __init__(self, parent_dir: str):
        """
        Initialize the DataLoader.

        Parameters:
        -----------
        parent_dir : str
            Path to the parent directory containing the data
        """
        self.parent_dir = Path(parent_dir)

        # Data storage
        self.search_dir = None
        self.has_ld = False
        self.cell_folders = []
        self.all_organelles = []
        self.unique_cells = []

        # Regex patterns for parsing folder and file names
        # Pattern to extract cell ID: everything before the last organelle_Statistics
        # Example: "control_1_ER_Statistics" -> "control_1"
        self.cell_id_pattern = re.compile(r'^(.+?)_[A-Z][A-Z0-9a-z]*_Statistics$')

        # Pattern to extract organelle from folder name
        # Example: "control_1_ER_Statistics" -> "ER"
        self.organelle_pattern = re.compile(r'_([A-Z][A-Z0-9a-z]*)_Statistics$')

        # Pattern to extract target organelle from filename
        # Example: "control_1_ER_Shortest_Distance_to_Surfaces_Surfaces=LD.csv" -> "LD"
        self.target_pattern = re.compile(r'Surfaces=([A-Z][A-Z0-9a-z]*)')

        # Validation flag
        self._is_validated = False

    def detect_structure(self) -> bool:
        """
        Detect the folder structure to determine if dataset contains LD.

        Returns:
        --------
        bool : True if structure detected successfully

        Raises:
        -------
        DataStructureError : If folder structure cannot be detected

        Structure 1 (WITH LD): Folders directly in parent_dir
            parent_dir/control_1_ER_Statistics/...

        Structure 2 (WITHOUT LD): Folders in subdirectories
            parent_dir/Control/control_1_ER_Statistics/...
        """
        if not self.parent_dir.exists():
            raise DataStructureError(f"Parent directory does not exist: {self.parent_dir}")

        # Get all items in parent directory
        all_items = list(self.parent_dir.iterdir())
        all_dirs = [item for item in all_items if item.is_dir()]

        # Check if any directory ends with "_Statistics"
        has_statistics_dirs = any(d.name.endswith('_Statistics') for d in all_dirs)

        if has_statistics_dirs:
            # Structure 1: Direct (WITH LD)
            self.search_dir = self.parent_dir
            self.has_ld = True
            print(f"[INFO] Structure: Direct - Dataset contains LD")
        else:
            # Structure 2: Nested (WITHOUT LD)
            print(f"[INFO] Structure: Nested - Searching subdirectories...")

            # Find subdirectories containing Statistics folders
            search_dirs = []
            for subdir in all_dirs:
                subdir_contents = list(subdir.iterdir())
                subdir_dirs = [item for item in subdir_contents if item.is_dir()]
                if any(d.name.endswith('_Statistics') for d in subdir_dirs):
                    search_dirs.append(subdir)

            if not search_dirs:
                raise DataStructureError(
                    "No valid Statistics folders found in parent directory or subdirectories"
                )

            print(f"[INFO] Found {len(search_dirs)} subdirectories with data")
            # Use the first subdirectory (typically "Control")
            self.search_dir = search_dirs[0]
            self.has_ld = False

        return True

    def find_cell_folders(self) -> bool:
        """
        Identify all cell folders and extract cell IDs and organelles.

        This method uses pattern matching to discover all organelles,
        not hardcoded organelle names.

        Returns:
        --------
        bool : True if cell folders found successfully

        Raises:
        -------
        DataStructureError : If no valid cell folders found
        """
        if self.search_dir is None:
            raise DataStructureError("Must call detect_structure() first")

        # Find all directories ending with "_Statistics"
        stat_dirs = [d for d in self.search_dir.iterdir()
                     if d.is_dir() and d.name.endswith('_Statistics')]

        if not stat_dirs:
            raise DataStructureError("No folders ending with '_Statistics' found")

        # Parse each folder to extract cell ID and organelle
        self.cell_folders = []
        for folder in stat_dirs:
            folder_name = folder.name

            # Extract cell ID
            cell_match = self.cell_id_pattern.match(folder_name)
            if not cell_match:
                print(f"[WARNING] Could not parse cell ID from {folder_name}")
                continue
            cell_id = cell_match.group(1)

            # Extract organelle
            org_match = self.organelle_pattern.search(folder_name)
            if not org_match:
                print(f"[WARNING] Could not parse organelle from {folder_name}")
                continue
            organelle = org_match.group(1)

            self.cell_folders.append({
                'full_path': folder,
                'folder_name': folder_name,
                'cell_id': cell_id,
                'organelle': organelle
            })

        if not self.cell_folders:
            raise DataStructureError("No valid cell folders could be parsed")

        # Extract unique values
        self.unique_cells = sorted(set(f['cell_id'] for f in self.cell_folders))
        self.all_organelles = sorted(set(f['organelle'] for f in self.cell_folders))

        print(f"[INFO] Found {len(self.unique_cells)} unique cells")
        print(f"[INFO] Found {len(self.all_organelles)} unique organelles: {', '.join(self.all_organelles)}")

        self._is_validated = True
        return True

    def load_distance_file(self, file_path: Path) -> pd.Series:
        """
        Load a distance CSV file and return distance values.

        Parameters:
        -----------
        file_path : Path
            Path to the CSV file

        Returns:
        --------
        pd.Series : Series containing distance values

        Raises:
        -------
        IOError : If file cannot be read
        """
        try:
            # Skip first 4 rows (headers), no column names
            df = pd.read_csv(file_path, skiprows=4, header=None)

            # Extract first column and drop NaN values
            distances = df.iloc[:, 0].dropna()

            return distances
        except Exception as e:
            raise IOError(f"Error reading {file_path.name}: {str(e)}")

    def get_distance_files(self, cell_id: str, source_organelle: str) -> List[Tuple[Path, str]]:
        """
        Get all distance files for a specific cell and source organelle.

        Parameters:
        -----------
        cell_id : str
            Cell identifier (e.g., "control_1")
        source_organelle : str
            Source organelle (e.g., "ER")

        Returns:
        --------
        List[Tuple[Path, str]] : List of (file_path, target_organelle) tuples
        """
        if not self._is_validated:
            raise DataStructureError("Must call find_cell_folders() first")

        # Find the folder for this cell and organelle
        matching_folders = [
            f for f in self.cell_folders
            if f['cell_id'] == cell_id and f['organelle'] == source_organelle
        ]

        if not matching_folders:
            return []

        source_folder = matching_folders[0]['full_path']

        # Find all distance files
        distance_files = list(source_folder.glob('*Shortest_Distance_to_Surfaces_Surfaces*.csv'))

        # Extract target organelles
        result = []
        for file_path in distance_files:
            filename = file_path.name

            # Extract target organelle from filename
            target_match = self.target_pattern.search(filename)
            if target_match:
                target_org = target_match.group(1)
                result.append((file_path, target_org))
            else:
                print(f"[WARNING] Could not identify target in {filename}")

        return result

    def get_cells_by_organelle(self, organelle: str) -> List[str]:
        """
        Get all cells that have data for a specific organelle.

        Parameters:
        -----------
        organelle : str
            Organelle name (e.g., "ER")

        Returns:
        --------
        List[str] : List of cell IDs
        """
        if not self._is_validated:
            raise DataStructureError("Must call find_cell_folders() first")

        cells = [
            f['cell_id'] for f in self.cell_folders
            if f['organelle'] == organelle
        ]
        return sorted(set(cells))

    def validate_data(self) -> Dict[str, any]:
        """
        Perform comprehensive data validation.

        Returns:
        --------
        dict : Validation report containing:
            - total_cells: Number of unique cells
            - total_organelles: Number of unique organelles
            - organelles: List of organelle names
            - cells: List of cell IDs
            - missing_data: List of warnings about missing data
        """
        if not self._is_validated:
            raise DataStructureError("Must call find_cell_folders() first")

        report = {
            'total_cells': len(self.unique_cells),
            'total_organelles': len(self.all_organelles),
            'organelles': self.all_organelles,
            'cells': self.unique_cells,
            'missing_data': []
        }

        # Check for cells missing certain organelles
        for cell_id in self.unique_cells:
            cell_organelles = [
                f['organelle'] for f in self.cell_folders
                if f['cell_id'] == cell_id
            ]
            missing = set(self.all_organelles) - set(cell_organelles)
            if missing:
                report['missing_data'].append(
                    f"Cell {cell_id} is missing organelles: {', '.join(missing)}"
                )

        return report

    def get_summary(self) -> str:
        """
        Get a human-readable summary of the loaded data.

        Returns:
        --------
        str : Summary text
        """
        if not self._is_validated:
            return "Data not yet loaded. Call detect_structure() and find_cell_folders() first."

        summary = []
        summary.append("=" * 60)
        summary.append("DATA LOADER SUMMARY")
        summary.append("=" * 60)
        summary.append(f"Dataset type: {'WITH LD' if self.has_ld else 'WITHOUT LD'}")
        summary.append(f"Search directory: {self.search_dir}")
        summary.append(f"Total cells: {len(self.unique_cells)}")
        summary.append(f"Total organelles: {len(self.all_organelles)}")
        summary.append(f"Organelles: {', '.join(self.all_organelles)}")
        summary.append(f"Cells: {', '.join(self.unique_cells)}")
        summary.append("=" * 60)

        return "\n".join(summary)
