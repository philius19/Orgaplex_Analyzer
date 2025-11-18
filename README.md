# Orgaplex-Analyzer v2.2

Scientific software for quantitative analysis of organelle interactions from Imaris segmentation data.

## Overview

This software processes 3D microscopy data segmented in Imaris and calculates spatial relationships between cellular organelles. The analysis pipeline extracts shortest-distance measurements and generates statistical summaries suitable for publication.

**Key capabilities:**
- One-way interaction analysis (mean distances between organelle populations)
- Volume and sphericity metrics (morphological analysis per organelle)
- Automatic organelle detection from folder structure
- Batch processing of multiple cells
- Excel and CSV export with metadata tracking

**Current version**: 2.2.0 (Released November 2025)
**Original R implementation**: Chahat Badhan
**Python rewrite**: Philipp Kaintoch

---

## Installation

### Prerequisites
- macOS, Linux, or Windows
- 4 GB RAM minimum (8 GB recommended for large datasets)
- 500 MB disk space

### For Non-Programmers (Conda Method - Recommended)

1. **Install Miniconda** (if not already installed):
   - Download from https://docs.conda.io/en/latest/miniconda.html
   - Follow installation wizard
   - Open "Anaconda Prompt" (Windows) or Terminal (Mac/Linux)

2. **Download this software**:
   - Click green "Code" button on GitHub
   - Select "Download ZIP"
   - Extract to a folder (e.g., `Documents/Orgaplex-Analyzer`)

3. **Install dependencies**:
   ```bash
   cd Documents/Orgaplex-Analyzer
   conda env create -f environment.yml
   ```
   This creates an environment named "orgaplex" with all required packages.

4. **Activate the environment**:
   ```bash
   conda activate orgaplex
   ```
   You must activate this environment each time before running the software.

### For Programmers (pip Method)

```bash
git clone https://github.com/your-repo/orgaplex-analyzer.git
cd orgaplex-analyzer
pip install -r requirements.txt
```

Tested on Python 3.11 and 3.12.

---

## Quick Start

### GUI Interface (Recommended for First-Time Users)

1. Activate environment:
   ```bash
   conda activate orgaplex
   ```

2. Launch GUI:
   ```bash
   python run_gui.py
   ```

3. Select directories:
   - Input: Folder containing `*_Statistics` subdirectories from Imaris
   - Output: Where to save results

4. Configure options:
   - Analysis type: One-Way Interactions
   - Format: Excel (.xlsx) or CSV

5. Click "Run Analysis" and monitor progress

### Command-Line Interface

```bash
conda activate orgaplex

python standalone_scripts/run_one_way_interaction.py \
  --input "/path/to/imaris/export" \
  --output "results.xlsx" \
  --format excel
```

For CSV output (creates multiple files):
```bash
python standalone_scripts/run_one_way_interaction.py \
  --input "/path/to/data" \
  --output "output_directory" \
  --format csv
```

---

## Input Data Requirements

### Expected Directory Structure

The software auto-detects two structure types:

**Type 1: With Lipid Droplets (LD)**
```
Input_Directory/
├── cell_01_ER_Statistics/
│   └── cell_01_ER_Shortest_Distance_to_Surfaces_Surfaces=LD.csv
├── cell_01_LD_Statistics/
├── cell_01_Ly_Statistics/
├── cell_02_ER_Statistics/
└── ...
```

**Type 2: Without LD**
```
Input_Directory/
├── Control/
│   ├── cell_01_ER_Statistics/
│   ├── cell_01_Ly_Statistics/
│   └── ...
└── Treatment/
    └── ...
```

### File Naming Convention

Distance files must follow Imaris export format:
```
{CellID}_{SourceOrganelle}_Shortest_Distance_to_Surfaces_Surfaces={TargetOrganelle}.csv
```

Examples:
- `control_1_ER_Shortest_Distance_to_Surfaces_Surfaces=LD.csv`
- `treated_5_M_Shortest_Distance_to_Surfaces_Surfaces=P.csv`

### CSV File Format

Files must contain numerical distance values (in micrometers or nanometers) starting from row 5 (Imaris exports include 4-line header).

---

## Output Format

### Data Organization

Results are organized as **rows = interactions, columns = cells**:

| Interaction | cell_01 | cell_02 | cell_03 |
|-------------|---------|---------|---------|
| ER-to-LD    | 5.87    | 6.12    | 7.33    |
| ER-to-Ly    | 0.27    | 0.31    | 0.09    |
| M-to-ER     | 0.001   | 0.013   | 0.000   |

This format is compatible with:
- GraphPad Prism
- R statistical packages (tidyverse)
- Python data science tools (pandas, seaborn)
- Excel pivot tables

### Excel Output (4 Sheets)

1. **Mean_Distance**: Mean shortest distances per interaction
2. **Count**: Number of measurements (sample size per interaction)
3. **Data_Completeness**: "Present" or "Missing" for quality control
4. **Metadata**: Analysis provenance (software version, timestamp, parameters)

### CSV Output (4 Files)

When using `--format csv`, four files are generated in the output directory:
- `one_way_interactions_mean_distance.csv`
- `one_way_interactions_count.csv`
- `one_way_interactions_data_completeness.csv`
- `one_way_interactions_metadata.csv`

### Interpreting Results

- **NaN values**: No data file found for this interaction/cell combination
- **Zero counts**: Distance file was empty or contained no valid measurements
- **Negative distances**: Overlapping organelles (normal in Imaris)
- **Missing entries**: Logged automatically with warnings during analysis

---

## Methods Summary

### Analysis Algorithm

One-way interaction analysis calculates the mean shortest distance from each object in the source organelle population to the nearest object in the target population.

**Mathematical definition**:
```
For source organelle S and target organelle T:
  d_i = min(distance from object i in S to all objects in T)
  Mean distance = (1/n) * Σ d_i
```

where n = number of objects in source population.

**Statistical notes**:
- Distance units: Preserved from Imaris (typically micrometers or nanometers)
- Outlier handling: No automated filtering (preserve raw measurements)
- Missing data: Reported explicitly in Data_Completeness sheet

### Data Validation

The software performs these validation checks:

1. **File integrity**: Non-empty, readable CSV files
2. **Numeric validation**: All distance values are finite numbers
3. **Range checks**: Warning if distances exceed 100 micrometers
4. **Completeness tracking**: Missing interaction/cell combinations logged

Validation failures halt analysis with detailed error messages.

### Performance Characteristics

- Processing time: ~0.8 seconds per cell (tested on 2020 MacBook Pro)
- Memory usage: ~100 MB for 200 cells
- Optimization: O(1) dictionary lookups for large datasets

---

## Project Architecture

```
Orgaplex-Analyzer/
├── src/                    # Core modules
│   ├── core/
│   │   ├── data_loader.py        # Data extraction & validation
│   │   └── one_way_interaction.py # Statistical analysis
│   ├── gui/
│   │   └── main_window.py        # Tkinter interface
│   └── utils/
│       └── logging_config.py     # Logging framework
├── standalone_scripts/     # Customizable analysis scripts
├── run_gui.py             # GUI launcher
├── environment.yml        # Conda environment specification
├── requirements.txt       # pip dependencies
└── setup.py               # Package configuration
```

### Design Principles

- **Modularity**: Core logic separated from interfaces (GUI/CLI)
- **Data provenance**: Every output includes metadata for reproducibility
- **Robustness**: Comprehensive validation prevents silent data corruption
- **Performance**: O(1) lookups for large datasets (200+ cells)

---

## Customization

See `standalone_scripts/README.md` for examples of:
- Computing additional statistics (median, standard deviation)
- Filtering specific organelles
- Applying distance thresholds
- Custom output formats

Quick example:
```bash
cp standalone_scripts/run_one_way_interaction.py my_custom_script.py
# Edit my_custom_script.py to add custom logic
python my_custom_script.py --input data/ --output results.xlsx
```

---

## Troubleshooting

**Error**: "No folders ending with '_Statistics' found"
**Solution**: Verify input directory contains Imaris export folders. Check folder naming matches `*_Statistics` pattern.

**Error**: "No module named 'src'"
**Solution**: Run scripts from project root directory, not from subdirectories.

**Problem**: GUI freezes during analysis
**Solution**: Normal for large datasets. Monitor status window for progress. Analysis runs in background thread.

**Problem**: Missing data warnings
**Solution**: Check Data_Completeness sheet. Missing data may indicate incomplete Imaris export or analysis failures for specific cells.

**Error**: "No valid distance values found"
**Solution**: Verify CSV files contain numeric data starting at row 5. Check files are not empty.

---

## Development Roadmap

### Completed (v2.0 - v2.1)
- Modular architecture
- One-way interaction analysis
- Data validation framework
- Professional logging
- Missing data tracking
- Performance optimization (11x speedup)

### Planned (v2.2+)
- Six-way interaction analysis (bidirectional comparisons)
- Volume calculations per organelle
- Surface area quantification
- Radial distribution functions
- Batch processing automation
- Unit test coverage (pytest)

---

## Citation

If you use this software in publications, please cite:

```
Kaintoch, P. (2025). Orgaplex-Analyzer v2.1: Python software for
quantitative organelle interaction analysis.
https://github.com/your-repo/orgaplex-analyzer
```

Original R implementation by Chahat Badhan.

---

## License

[Specify license - MIT, GPL, etc.]

---

## Changelog

### v2.2.0 (November 2025)
- Added Vol/Spher-Metrics analysis module (volume and sphericity statistics per organelle)
- Implemented natural sorting for cell columns (fixes: 1h LPS 1, 1h LPS 2, ..., 1h LPS 10)
- Fixed macOS metadata file errors (eliminates ~7,000 false errors from `._` files)
- Centralized file filtering utilities for consistent data processing
- GUI now supports both One-Way Interactions and Vol/Spher-Metrics analysis types

### v2.1.0 (November 2025)
- Added comprehensive data validation
- Implemented professional logging framework
- Added metadata tracking for reproducibility
- Implemented missing data warnings and completeness reports
- Performance optimization (O(1) dictionary lookups)
- Removed unused code and imports
- Centralized version management
- Added conda environment specification

### v2.0.0 (November 2025)
- Complete rewrite from R to Python
- Modular architecture
- New output format (rows = interactions, columns = cells)
- GUI and command-line interfaces
- Standalone customizable scripts

---

## Contact

For bugs, feature requests, or questions:
- GitHub Issues: [p.kaintoch@uni-muenster.de]
- Email: [p.kaintoch@uni-muenster.de]

---

**Scientific data processing with confidence.**
