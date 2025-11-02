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

AUTHOR: Philipp Kaintoch
DATE: 2025-11-02
VERSION: 2.0.1
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from .data_loader import DataLoader


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

    def load_data(self):
        """
        Load and validate data using DataLoader.

        This method must be called before running analysis.
        """
        print("[INFO] Loading data...")
        self.data_loader.detect_structure()
        self.data_loader.find_cell_folders()
        print(self.data_loader.get_summary())

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
                    count = len(distances)

                    # Store results
                    interactions[interaction_name] = {
                        'mean': mean_distance,
                        'count': count
                    }

                    print(f"  {interaction_name}: mean={mean_distance:.3f}, count={count}")

                except Exception as e:
                    print(f"  [ERROR] Failed to process {interaction_name}: {str(e)}")
                    continue

        return interactions

    def analyze_all_cells(self):
        """
        Analyze all cells in the dataset.

        This method processes all cells and stores results in self.results.
        """
        print("\n[INFO] Analyzing all cells...")

        unique_cells = self.data_loader.unique_cells
        total_cells = len(unique_cells)

        for idx, cell_id in enumerate(unique_cells, 1):
            print(f"\n[{idx}/{total_cells}] Processing cell: {cell_id}")

            cell_interactions = self.analyze_cell(cell_id)
            self.results[cell_id] = cell_interactions

        print(f"\n[INFO] Completed analysis of {total_cells} cells")

    def build_summary_tables(self):
        """
        Build summary tables with format: row per interaction, column per cell.

        Creates two DataFrames:
        - mean_distance_df: Mean distances for each interaction (rows) across cells (columns)
        - count_df: Count of measurements for each interaction (rows) across cells (columns)
        """
        print("\n[INFO] Building summary tables...")

        if not self.results:
            raise ValueError("No results available. Run analyze_all_cells() first.")

        # Collect all unique interactions across all cells
        all_interactions = set()
        for cell_data in self.results.values():
            all_interactions.update(cell_data.keys())

        all_interactions = sorted(all_interactions)
        all_cells = sorted(self.results.keys())

        print(f"[INFO] Found {len(all_interactions)} unique interactions")
        print(f"[INFO] Found {len(all_cells)} cells")

        # Build mean distance and count tables
        # Format: rows = interactions, columns = cells
        mean_data = []
        count_data = []

        for interaction in all_interactions:
            # Build row for this interaction across all cells
            mean_row = {'Interaction': interaction}
            count_row = {'Interaction': interaction}

            for cell_id in all_cells:
                cell_interactions = self.results[cell_id]

                if interaction in cell_interactions:
                    mean_row[cell_id] = cell_interactions[interaction]['mean']
                    count_row[cell_id] = cell_interactions[interaction]['count']
                else:
                    # Use NaN for missing interactions
                    mean_row[cell_id] = np.nan
                    count_row[cell_id] = 0

            mean_data.append(mean_row)
            count_data.append(count_row)

        # Create DataFrames
        self.mean_distance_df = pd.DataFrame(mean_data)
        self.count_df = pd.DataFrame(count_data)

        print("[INFO] Summary tables created successfully")
        print(f"[INFO] Table dimensions: {self.mean_distance_df.shape}")

    def export_to_excel(self, output_path: str):
        """
        Export results to Excel file with separate sheets for mean and count.

        Parameters:
        -----------
        output_path : str
            Path to the output Excel file
        """
        if self.mean_distance_df is None or self.count_df is None:
            raise ValueError("Summary tables not built. Run build_summary_tables() first.")

        output_path = Path(output_path)
        print(f"\n[INFO] Exporting to Excel: {output_path.name}")

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

        print(f"[SUCCESS] Results exported to: {output_path}")

    def export_to_csv(self, output_dir: str):
        """
        Export results to CSV files (separate files for mean and count).

        Parameters:
        -----------
        output_dir : str
            Directory to save CSV files
        """
        if self.mean_distance_df is None or self.count_df is None:
            raise ValueError("Summary tables not built. Run build_summary_tables() first.")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n[INFO] Exporting to CSV: {output_dir}")

        # Export mean distances
        mean_path = output_dir / "one_way_interactions_mean_distance.csv"
        self.mean_distance_df.to_csv(mean_path, index=False)
        print(f"[INFO] Mean distances saved to: {mean_path.name}")

        # Export counts
        count_path = output_dir / "one_way_interactions_count.csv"
        self.count_df.to_csv(count_path, index=False)
        print(f"[INFO] Counts saved to: {count_path.name}")

        print(f"[SUCCESS] CSV export complete")

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
        print("=" * 60)
        print("ONE-WAY INTERACTION ANALYSIS")
        print("=" * 60)

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

        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)

    def get_results_summary(self) -> str:
        """
        Get a human-readable summary of analysis results.

        Returns:
        --------
        str : Summary text
        """
        if self.mean_distance_df is None:
            return "No results available yet."

        summary = []
        summary.append("=" * 60)
        summary.append("ANALYSIS RESULTS SUMMARY")
        summary.append("=" * 60)
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

        summary.append("=" * 60)
        return "\n".join(summary)
