#!/usr/bin/env python3
"""
Standalone Script: One-Way Interaction Analysis

This is a simple, self-contained script for analyzing one-way organelle
interactions. You can copy and modify this script to customize the analysis
without affecting the main software.

USAGE:
    python run_one_way_interaction.py --input /path/to/data --output /path/to/output.xlsx

    Or for CSV format:
    python run_one_way_interaction.py --input /path/to/data --output /path/to/output_dir --format csv

OUTPUT FORMAT:
    Row per interaction, columns for each cell
    Example:
        Interaction  | control_1 | control_2 | control_3 | ...
        ER-to-LD     | 5.87      | 6.12      | 7.33      | ...
        ER-to-Ly     | 0.27      | 0.31      | 0.09      | ...
        M-to-ER      | 0.001     | 0.013     | 0.000     | ...

CUSTOMIZATION TIPS:
    1. To add custom statistics (e.g., median, std), modify the analyze_cell() method
    2. To filter interactions, modify the build_summary_tables() method
    3. To change output format, modify the export methods

AUTHOR: Philipp Kaintoch
DATE: 2025-11-02
VERSION: 2.0.0
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path to import core modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.one_way_interaction import OneWayInteractionAnalyzer


def main():
    """Main entry point for standalone script."""

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Analyze one-way organelle interactions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export to Excel (default)
  python run_one_way_interaction.py --input /path/to/data --output results.xlsx

  # Export to CSV
  python run_one_way_interaction.py --input /path/to/data --output ./output --format csv

  # Specify full paths
  python run_one_way_interaction.py \\
    --input "/Users/user/data/experiment1" \\
    --output "/Users/user/results/experiment1.xlsx"
        """
    )

    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input directory containing Statistics folders'
    )

    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output file path (for Excel) or directory (for CSV)'
    )

    parser.add_argument(
        '--format', '-f',
        choices=['excel', 'csv'],
        default='excel',
        help='Output format: excel or csv (default: excel)'
    )

    args = parser.parse_args()

    # Validate input directory
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input directory does not exist: {args.input}")
        sys.exit(1)

    if not input_path.is_dir():
        print(f"ERROR: Input path is not a directory: {args.input}")
        sys.exit(1)

    # Create analyzer
    print("\nInitializing analyzer...")
    analyzer = OneWayInteractionAnalyzer(str(input_path))

    try:
        # Run analysis
        analyzer.run(args.output, file_format=args.format)

        # Print summary
        print("\n" + analyzer.get_results_summary())

        print("\nAnalysis completed successfully!")
        return 0

    except Exception as e:
        print(f"\nERROR: Analysis failed")
        print(f"Reason: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
