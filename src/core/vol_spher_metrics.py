"""
Volume and Sphericity Metrics Analysis Module

Analyzes volume and sphericity statistics for organelles from Imaris-generated
CSV files.

Author: Philipp Kaintoch
Date: 2025-11-18
Version: 2.2.0
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import sys
from datetime import datetime
from ..utils.logging_config import get_logger
from ..utils.sorting import sort_cell_ids
from ..utils.file_filters import filter_metadata_files
from ..__version__ import __version__

logger = get_logger(__name__)


class VolSpherMetricsAnalyzer:
    """
    Analyzes volume and sphericity metrics from Imaris CSV exports.

    This class processes individual Volume.csv and Sphericity.csv files
    for each cell and generates summary statistics per organelle.

    Data Structure Expected:
    ------------------------
    Input directory contains folders: {cell_id}_{organelle}_Statistics/
    Each folder contains:
    - {cell_id}_{organelle}_Volume.csv
    - {cell_id}_{organelle}_Sphericity.csv

    Output Format:
    --------------
    Excel file with one sheet per organelle:
    - Rows: Metrics (Mean_Sphericity, Count_Sphericity, Mean_Volume, Count_Volume, Total_Volume, Max_Volume)
    - Columns: Cells (numerically sorted)
    """

    def __init__(self, input_dir: str):
        """
        Initialize the analyzer.

        Parameters:
        -----------
        input_dir : str
            Path to directory containing organelle Statistics folders

        Raises:
        -------
        FileNotFoundError : If input directory does not exist
        """
        self.input_dir = Path(input_dir)

        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory does not exist: {self.input_dir}")

        self.results = {}  # organelle -> DataFrame
        self.metadata = {}

    def load_metric_file(self, file_path: Path, metric_name: str) -> pd.Series:
        """
        Load a Volume or Sphericity CSV file from Imaris.

        Parameters:
        -----------
        file_path : Path
            Path to the CSV file
        metric_name : str
            Name of metric column ("Volume" or "Sphericity")

        Returns:
        --------
        pd.Series : Series containing metric values

        Raises:
        -------
        ValueError : If data validation fails

        Notes:
        ------
        - Skips first 4 rows (Imaris headers)
        - Validates data is numeric
        - Checks for reasonable value ranges
        """
        try:
            # Skip first 4 rows (Imaris CSV headers)
            df = pd.read_csv(file_path, skiprows=4, header=None, encoding='utf-8')

            # Validate file structure
            if df.shape[1] < 1:
                raise ValueError(f"File has no columns: {file_path.name}")

            if df.shape[0] < 1:
                raise ValueError(f"File has no data rows: {file_path.name}")

            # Extract first column (metric values) and drop NaN
            values = df.iloc[:, 0].dropna()

            # Validation: Check for empty data
            if len(values) == 0:
                raise ValueError(f"No valid {metric_name} values in {file_path.name}")

            # Validation: Ensure data is numeric
            if not pd.api.types.is_numeric_dtype(values):
                raise ValueError(f"{metric_name} data is not numeric in {file_path.name}")

            # Validation: Check for infinite values
            if np.isinf(values).any():
                raise ValueError(f"Infinite {metric_name} values found in {file_path.name}")

            # Metric-specific validation
            if metric_name == "Sphericity":
                # Sphericity should be in [0, 1]
                if (values < 0).any() or (values > 1).any():
                    logger.warning(
                        f"Sphericity values outside expected range [0, 1] in {file_path.name}. "
                        f"Min: {values.min():.3f}, Max: {values.max():.3f}"
                    )

            elif metric_name == "Volume":
                # Volume should be positive
                if (values < 0).any():
                    raise ValueError(f"Negative volume values found in {file_path.name}")

                # Warn about suspiciously large values (>1000 µm³)
                if (values > 1000).any():
                    logger.warning(
                        f"Unusually large volume values (>1000 µm³) in {file_path.name}. "
                        f"Max: {values.max():.3f}"
                    )

            return values

        except pd.errors.EmptyDataError:
            raise ValueError(f"File is empty or has no data: {file_path.name}")
        except Exception as e:
            raise IOError(f"Failed to read {file_path.name}: {e}")

    def analyze_organelle(self, organelle: str) -> pd.DataFrame:
        """
        Analyze all cells for a specific organelle.

        Parameters:
        -----------
        organelle : str
            Organelle name (e.g., "ER", "M", "G")

        Returns:
        --------
        pd.DataFrame : Results with metrics as rows, cells as columns
            Rows: Mean_Sphericity, Count_Sphericity, Mean_Volume, Count_Volume, Total_Volume, Max_Volume
            Columns: Cell IDs (numerically sorted)
        """
        # Find all Statistics folders for this organelle
        pattern = f"*_{organelle}_Statistics"
        organelle_folders = filter_metadata_files(
            self.input_dir.glob(pattern)
        )

        if not organelle_folders:
            logger.warning(f"No folders found for organelle: {organelle}")
            return pd.DataFrame()

        logger.info(f"Found {len(organelle_folders)} cells for {organelle}")

        results_dict = {}

        for folder in organelle_folders:
            # Extract cell ID from folder name
            # Pattern: {cell_id}_{organelle}_Statistics
            folder_name = folder.name
            cell_id = folder_name.replace(f"_{organelle}_Statistics", "")

            # Find Volume and Sphericity files
            volume_file = folder / f"{cell_id}_{organelle}_Volume.csv"
            sphericity_file = folder / f"{cell_id}_{organelle}_Sphericity.csv"

            # Skip if files are metadata files
            if (volume_file.exists() and volume_file.name.startswith('._')) or \
               (sphericity_file.exists() and sphericity_file.name.startswith('._')):
                continue

            cell_metrics = {}

            # Load and calculate Volume metrics
            if volume_file.exists():
                try:
                    volumes = self.load_metric_file(volume_file, "Volume")
                    cell_metrics['Mean_Volume'] = volumes.mean()
                    cell_metrics['Count_Volume'] = len(volumes)
                    cell_metrics['Total_Volume'] = volumes.sum()
                    cell_metrics['Max_Volume'] = volumes.max()
                except Exception as e:
                    logger.error(f"Failed to process {volume_file.name}: {e}")
                    cell_metrics['Mean_Volume'] = np.nan
                    cell_metrics['Count_Volume'] = 0
                    cell_metrics['Total_Volume'] = np.nan
                    cell_metrics['Max_Volume'] = np.nan
            else:
                logger.warning(f"Missing volume file for {cell_id} ({organelle})")
                cell_metrics['Mean_Volume'] = np.nan
                cell_metrics['Count_Volume'] = 0
                cell_metrics['Total_Volume'] = np.nan
                cell_metrics['Max_Volume'] = np.nan

            # Load and calculate Sphericity metrics
            if sphericity_file.exists():
                try:
                    sphericity = self.load_metric_file(sphericity_file, "Sphericity")
                    cell_metrics['Mean_Sphericity'] = sphericity.mean()
                    cell_metrics['Count_Sphericity'] = len(sphericity)
                except Exception as e:
                    logger.error(f"Failed to process {sphericity_file.name}: {e}")
                    cell_metrics['Mean_Sphericity'] = np.nan
                    cell_metrics['Count_Sphericity'] = 0
            else:
                logger.warning(f"Missing sphericity file for {cell_id} ({organelle})")
                cell_metrics['Mean_Sphericity'] = np.nan
                cell_metrics['Count_Sphericity'] = 0

            results_dict[cell_id] = cell_metrics

        # Create DataFrame
        df = pd.DataFrame(results_dict)

        # Sort columns naturally (1h LPS 1, 1h LPS 2, ..., 1h LPS 10)
        if not df.empty:
            sorted_cells = sort_cell_ids(list(df.columns))
            df = df[sorted_cells]

        # Reorder rows for consistent output
        if not df.empty:
            row_order = [
                'Mean_Sphericity',
                'Count_Sphericity',
                'Mean_Volume',
                'Count_Volume',
                'Total_Volume',
                'Max_Volume'
            ]
            df = df.reindex(row_order)

        return df

    def run(self, output_path: str, file_format: str = 'excel'):
        """
        Run the analysis for all organelles.

        Parameters:
        -----------
        output_path : str
            Path to output file
        file_format : str
            'excel' or 'csv'

        Raises:
        -------
        ValueError : If no organelles are found
        """
        logger.info("Starting Vol/Spher Metrics Analysis")
        logger.info(f"Input directory: {self.input_dir}")

        # Discover organelles by finding all Statistics folders
        stat_folders = filter_metadata_files(
            d for d in self.input_dir.iterdir()
            if d.is_dir() and d.name.endswith('_Statistics')
        )

        if not stat_folders:
            raise ValueError(f"No Statistics folders found in {self.input_dir}")

        # Extract unique organelles
        organelles = set()
        for folder in stat_folders:
            # Pattern: {cell_id}_{organelle}_Statistics
            parts = folder.name.split('_')
            if len(parts) >= 2 and parts[-1] == 'Statistics':
                organelle = parts[-2]
                organelles.add(organelle)

        organelles = sorted(organelles)
        logger.info(f"Found {len(organelles)} organelles: {', '.join(organelles)}")

        if not organelles:
            raise ValueError("No organelles detected in folder names")

        # Analyze each organelle
        for organelle in organelles:
            logger.info(f"Analyzing organelle: {organelle}")
            df = self.analyze_organelle(organelle)

            if not df.empty:
                self.results[organelle] = df
                logger.info(f"  Processed {df.shape[1]} cells")
            else:
                logger.warning(f"  No data for {organelle}")

        # Save results
        if not self.results:
            raise ValueError("No data was successfully processed")

        if file_format == 'excel':
            self._save_excel(output_path)
        else:
            self._save_csv(output_path)

        logger.info(f"Results saved to: {output_path}")
        logger.info("Analysis Complete")

    def _generate_metadata(self) -> Dict[str, str]:
        """
        Generate metadata for data provenance.

        Returns:
        --------
        dict : Metadata dictionary
        """
        metadata = {
            'Software': 'Orgaplex-Analyzer',
            'Version': __version__,
            'Analysis_Type': 'Vol/Spher Metrics',
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Python_Version': sys.version.split()[0],
            'Pandas_Version': pd.__version__,
            'NumPy_Version': np.__version__,
            'Input_Directory': str(self.input_dir),
            'Organelles_Analyzed': ', '.join(sorted(self.results.keys())),
            'Total_Cells': str(max(df.shape[1] for df in self.results.values()) if self.results else 0)
        }

        self.metadata = metadata
        return metadata

    def _save_excel(self, output_path: str):
        """
        Save results to Excel with one sheet per organelle.

        Parameters:
        -----------
        output_path : str
            Path to Excel file
        """
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Save each organelle to a separate sheet
            for organelle, df in self.results.items():
                df.to_excel(writer, sheet_name=organelle, index=True)

            # Add metadata sheet
            metadata = self._generate_metadata()
            metadata_df = pd.DataFrame(
                list(metadata.items()),
                columns=['Parameter', 'Value']
            )
            metadata_df.to_excel(writer, sheet_name='Metadata', index=False)

        logger.info(f"Saved {len(self.results)} organelle sheets to Excel")

    def _save_csv(self, output_dir: str):
        """
        Save results to CSV files (one per organelle).

        Parameters:
        -----------
        output_dir : str
            Path to output directory
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save each organelle to a separate CSV
        for organelle, df in self.results.items():
            csv_path = output_path / f"vol_spher_metrics_{organelle}.csv"
            df.to_csv(csv_path, index=True)

        # Save metadata
        metadata = self._generate_metadata()
        metadata_df = pd.DataFrame(
            list(metadata.items()),
            columns=['Parameter', 'Value']
        )
        metadata_path = output_path / "vol_spher_metrics_metadata.csv"
        metadata_df.to_csv(metadata_path, index=False)

        logger.info(f"Saved {len(self.results)} organelle CSVs to {output_dir}")

    def get_results_summary(self) -> str:
        """
        Get a text summary of analysis results.

        Returns:
        --------
        str : Summary text
        """
        if not self.results:
            return "No results available"

        summary = ["Vol/Spher Metrics Analysis Summary", "=" * 40]

        for organelle, df in self.results.items():
            summary.append(f"\n{organelle}:")
            summary.append(f"  Cells analyzed: {df.shape[1]}")
            summary.append(f"  Metrics: {', '.join(df.index.tolist())}")

        return "\n".join(summary)
