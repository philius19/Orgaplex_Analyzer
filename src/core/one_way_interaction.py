"""
One-Way Interaction Analysis Module

This module analyzes one-way organelle interactions from Imaris-generated
segmentation data. It calculates mean distances between organelles for each cell.

Output Format:
    Row per interaction, columns for each cell
    Example:
        Interaction  | control_1 | control_2 | control_3 | ...
        ER-to-LD     | 5.87      | 6.12      | 7.33      | ...
        ER-to-Ly     | 0.27      | 0.31      | 0.09      | ...
        M-to-ER      | 0.001     | 0.013     | 0.000     | ...

Author: Philipp Kaintoch
Date: 2025-11-18
Version: 2.2.0
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from .data_loader import DataLoader
from ..utils.logging_config import get_logger
from ..utils.sorting import sort_cell_ids
from ..__version__ import __version__

# Initialize logger
logger = get_logger(__name__)


class OneWayInteractionAnalyzer:
    """
    Analyzes one-way organelle interactions.

    This class processes distance measurements between organelles and
    generates summary statistics per cell.
    """

    def __init__(self, input_dir: str):
        """
        Initialize the analyzer.

        Parameters:
        -----------
        input_dir : str
            Path to the directory containing the data
        """
        self.input_dir = input_dir
        self.data_loader = DataLoader(input_dir)
        self.results = {}
        self.mean_distance_df = None
        self.count_df = None
        self.missing_data_df = None  # Track data completeness
        self.metadata = {}  # Store provenance information

    def _generate_metadata(self) -> Dict[str, str]:
        """
        Generate metadata for data provenance and reproducibility.

        Returns:
        --------
        dict : Metadata including software version, timestamp, environment info
        """
        metadata = {
            'Software': 'Orgaplex-Analyzer',
            'Version': __version__,
            'Analysis_Type': 'One-Way Interaction Analysis',
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Python_Version': sys.version.split()[0],
            'Pandas_Version': pd.__version__,
            'NumPy_Version': np.__version__,
            'Input_Directory': str(self.input_dir),
            'Total_Cells': str(len(self.data_loader.unique_cells)) if hasattr(self.data_loader, 'unique_cells') else 'N/A',
            'Total_Organelles': str(len(self.data_loader.all_organelles)) if hasattr(self.data_loader, 'all_organelles') else 'N/A',
            'Organelles_List': ', '.join(self.data_loader.all_organelles) if hasattr(self.data_loader, 'all_organelles') else 'N/A',
            'Total_Interactions': str(len(self.mean_distance_df)) if self.mean_distance_df is not None else 'N/A',
        }

        self.metadata = metadata
        return metadata

    def load_data(self):
        """
        Load and validate data using DataLoader.

        This method must be called before running analysis.
        """
        logger.info("Loading data...")
        self.data_loader.detect_structure()
        self.data_loader.find_cell_folders()
        # Get summary uses logger internally, so just call it
        summary = self.data_loader.get_summary()
        for line in summary.split('\n'):
            if line.strip():
                logger.info(line)

    def analyze_cell(self, cell_id: str) -> Dict[str, Dict[str, float]]:
        """
        Analyze all organelle interactions for a single cell.

        Parameters:
        -----------
        cell_id : str
            Cell identifier (e.g., "control_1")

        Returns:
        --------
        dict : Dictionary of interactions
            {
                'ER-to-LD': {'mean': 5.87, 'count': 2260},
                'ER-to-Ly': {'mean': 0.27, 'count': 2260},
                ...
            }
        """
        interactions = {}

        # Get all organelles for this cell
        cell_folders = [
            f for f in self.data_loader.cell_folders
            if f['cell_id'] == cell_id
        ]

        # Process each source organelle
        for folder_info in cell_folders:
            source_org = folder_info['organelle']

            # Get distance files for this source organelle
            distance_files = self.data_loader.get_distance_files(cell_id, source_org)

            for file_path, target_org in distance_files:
                # Create interaction name
                interaction_name = f"{source_org}-to-{target_org}"

                try:
                    # Load distance data
                    distances = self.data_loader.load_distance_file(file_path)

                    # Calculate statistics
                    mean_distance = distances.mean()
                    count = (distances <= 0).sum()  

                    # CRITICAL VALIDATION: Verify calculated mean is valid
                    if pd.isna(mean_distance):
                        raise ValueError(
                            f"Calculated mean is NaN for {interaction_name} in cell {cell_id}. "
                            f"This indicates a calculation error."
                        )

                    if np.isinf(mean_distance):
                        raise ValueError(
                            f"Calculated mean is infinite for {interaction_name} in cell {cell_id}. "
                            f"This indicates a calculation error."
                        )

                    # Store results
                    interactions[interaction_name] = {
                        'mean': mean_distance,
                        'count': count
                    }

                    logger.debug(f"  {interaction_name}: mean={mean_distance:.3f}, count={count}")

                except Exception as e:
                    logger.error(f"Failed to process {interaction_name}: {str(e)}")
                    continue

        return interactions

    def analyze_all_cells(self):
        """
        Analyze all cells in the dataset.

        This method processes all cells and stores results in self.results.
        """
        logger.info("Analyzing all cells...")

        unique_cells = self.data_loader.unique_cells
        total_cells = len(unique_cells)

        for idx, cell_id in enumerate(unique_cells, 1):
            logger.info(f"[{idx}/{total_cells}] Processing cell: {cell_id}")

            cell_interactions = self.analyze_cell(cell_id)
            self.results[cell_id] = cell_interactions

        logger.info(f"Completed analysis of {total_cells} cells")

    def build_summary_tables(self):
        """
        Build summary tables with format: row per interaction, column per cell.

        Creates three DataFrames:
        - mean_distance_df: Mean distances for each interaction (rows) across cells (columns)
        - count_df: Count of measurements for each interaction (rows) across cells (columns)
        - missing_data_df: Data completeness tracking ('Present' or 'Missing')
        """
        logger.info("Building summary tables...")

        if not self.results:
            raise ValueError("No results available. Run analyze_all_cells() first.")

        # Collect all unique interactions across all cells
        all_interactions = set()
        for cell_data in self.results.values():
            all_interactions.update(cell_data.keys())

        all_interactions = sorted(all_interactions)
        all_cells = sort_cell_ids(list(self.results.keys()))

        logger.info(f"Found {len(all_interactions)} unique interactions")
        logger.info(f"Found {len(all_cells)} cells")

        # Build mean distance, count, and missing data tables
        # Format: rows = interactions, columns = cells
        mean_data = []
        count_data = []
        missing_data = []
        missing_count = 0

        for interaction in all_interactions:
            # Build row for this interaction across all cells
            mean_row = {'Interaction': interaction}
            count_row = {'Interaction': interaction}
            missing_row = {'Interaction': interaction}

            for cell_id in all_cells:
                cell_interactions = self.results[cell_id]

                if interaction in cell_interactions:
                    mean_row[cell_id] = cell_interactions[interaction]['mean']
                    count_row[cell_id] = cell_interactions[interaction]['count']
                    missing_row[cell_id] = 'Present'
                else:
                    # Use NaN for missing interactions
                    mean_row[cell_id] = np.nan
                    count_row[cell_id] = 0
                    missing_row[cell_id] = 'Missing'
                    missing_count += 1
                    logger.debug(f"Missing data: {interaction} not found in {cell_id}")

            mean_data.append(mean_row)
            count_data.append(count_row)
            missing_data.append(missing_row)

        # Create DataFrames
        self.mean_distance_df = pd.DataFrame(mean_data)
        self.count_df = pd.DataFrame(count_data)
        self.missing_data_df = pd.DataFrame(missing_data)

        logger.info("Summary tables created successfully")
        logger.info(f"Table dimensions: {self.mean_distance_df.shape}")

        if missing_count > 0:
            total_possible = len(all_interactions) * len(all_cells)
            missing_percentage = (missing_count / total_possible) * 100
            logger.warning(f"{missing_count}/{total_possible} ({missing_percentage:.1f}%) data points are missing")
        else:
            logger.info("No missing data detected - complete dataset")

    def export_to_excel(self, output_path: str):
        """
        Export results to Excel file with separate sheets for mean, count, and data completeness.

        Parameters:
        -----------
        output_path : str
            Path to the output Excel file
        """
        if self.mean_distance_df is None or self.count_df is None:
            raise ValueError("Summary tables not built. Run build_summary_tables() first.")

        output_path = Path(output_path)
        logger.info(f"Exporting to Excel: {output_path.name}")

        # Generate metadata for provenance
        metadata = self._generate_metadata()

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Write mean distances
            self.mean_distance_df.to_excel(
                writer,
                sheet_name='Mean_Distance',
                index=False
            )

            # Write counts
            self.count_df.to_excel(
                writer,
                sheet_name='Count',
                index=False
            )

            # Write missing data report
            if self.missing_data_df is not None:
                self.missing_data_df.to_excel(
                    writer,
                    sheet_name='Data_Completeness',
                    index=False
                )

            # Write metadata for data provenance
            metadata_df = pd.DataFrame(list(metadata.items()), columns=['Parameter', 'Value'])
            metadata_df.to_excel(
                writer,
                sheet_name='Metadata',
                index=False
            )

        logger.info(f"Results exported to: {output_path}")
        logger.info("Excel file contains 4 sheets: Mean_Distance, Count, Data_Completeness, Metadata")

    def export_to_csv(self, output_dir: str):
        """
        Export results to CSV files (separate files for mean, count, and data completeness).

        Parameters:
        -----------
        output_dir : str
            Directory to save CSV files
        """
        if self.mean_distance_df is None or self.count_df is None:
            raise ValueError("Summary tables not built. Run build_summary_tables() first.")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Exporting to CSV: {output_dir}")

        # Generate metadata for provenance
        metadata = self._generate_metadata()

        # Export mean distances
        mean_path = output_dir / "one_way_interactions_mean_distance.csv"
        self.mean_distance_df.to_csv(mean_path, index=False)
        logger.info(f"Mean distances saved to: {mean_path.name}")

        # Export counts
        count_path = output_dir / "one_way_interactions_count.csv"
        self.count_df.to_csv(count_path, index=False)
        logger.info(f"Counts saved to: {count_path.name}")

        # Export missing data report
        if self.missing_data_df is not None:
            missing_path = output_dir / "one_way_interactions_data_completeness.csv"
            self.missing_data_df.to_csv(missing_path, index=False)
            logger.info(f"Data completeness saved to: {missing_path.name}")

        # Export metadata for data provenance
        metadata_df = pd.DataFrame(list(metadata.items()), columns=['Parameter', 'Value'])
        metadata_path = output_dir / "one_way_interactions_metadata.csv"
        metadata_df.to_csv(metadata_path, index=False)
        logger.info(f"Metadata saved to: {metadata_path.name}")

        logger.info("CSV export complete")

    def run(self, output_path: str, file_format: str = 'excel'):
        """
        Run the complete analysis pipeline.

        This is a convenience method that runs all steps in sequence.

        Parameters:
        -----------
        output_path : str
            Path for output file (if excel) or directory (if csv)
        file_format : str
            Either 'excel' or 'csv'
        """

        logger.info("Starting One-Way Interaction Analysis")

        # Step 1: Load data
        self.load_data()

        # Step 2: Analyze all cells
        self.analyze_all_cells()

        # Step 3: Build summary tables
        self.build_summary_tables()

        # Step 4: Export results
        if file_format == 'excel':
            self.export_to_excel(output_path)
        elif file_format == 'csv':
            self.export_to_csv(output_path)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

        
        logger.info("Analysis Complete")
        

    def get_results_summary(self) -> str:
        """
        Get a summary of analysis results.

        Returns:
        --------
        str : Summary text
        """
        if self.mean_distance_df is None:
            return "No results available yet."

        summary = []

        summary.append(f"Total cells analyzed: {len(self.results)}")
        summary.append(f"Total unique interactions: {len(self.mean_distance_df)}")
        summary.append(f"Output shape: {self.mean_distance_df.shape}")
        summary.append("\nSample interactions (mean across all cells):")

        # Show first few interactions
        # With new format: rows = interactions, columns = cells
        for idx, row in self.mean_distance_df.head(5).iterrows():
            interaction_name = row['Interaction']
            # Calculate mean across all cells (excluding the Interaction column)
            cell_columns = [col for col in self.mean_distance_df.columns if col != 'Interaction']
            mean_val = row[cell_columns].mean()
            summary.append(f"  {interaction_name}: mean = {mean_val:.3f}")

        
        return "\n".join(summary)
