# Organelle Analysis Software v2.0

Modern Python software for analyzing organelle interactions from Imaris-generated segmentation data. This is a complete rewrite with modular architecture, improved output format, and both GUI and command-line interfaces.

## Key Features

### Analysis Capabilities
- **One-Way Interactions**: Analyze shortest distances between organelles (e.g., ER-to-LD, M-to-P)
- **Pattern-Based Detection**: Automatically discovers all organelles in your data (no hardcoded organelle list)
- **Flexible Data Structures**: Handles both LD and non-LD datasets automatically

### Output Format (NEW!)
**Row per interaction, column per cell** - Perfect for statistical analysis!

```
Interaction  | control_1 | control_2 | control_3 | ...
ER-to-LD     | 5.87      | 6.12      | 7.33      | ...
ER-to-Ly     | 0.27      | 0.31      | 0.09      | ...
M-to-ER      | 0.001     | 0.013     | 0.000     | ...
```

Two sheets/files are generated:
- `Mean_Distance`: Mean shortest distances
- `Count`: Number of measurements

### Modular Architecture
- **Core Modules**: Robust, well-tested analysis engine
- **Standalone Scripts**: Simple scripts you can copy and customize
- **GUI Application**: User-friendly interface for non-programmers
- **Command-Line Interface**: For automation and scripting

---

## Installation

### 1. Activate Conda Environment

```bash
conda activate orgaplex
```

The environment is already created at `/Users/philippkaintoch/anaconda3/envs/orgaplex` with all required packages:
- pandas (2.3.3+)
- openpyxl (3.1.5+)
- numpy (2.3.4+)
- Python 3.11

---

## Quick Start

### Option 1: GUI (Recommended for Beginners)

```bash
conda activate orgaplex
python run_gui.py
```

1. Click "Browse..." to select your input directory
2. Click "Browse..." to select output directory
3. Choose analysis type and format
4. Click "Run Analysis"
5. Monitor progress in the status window

### Option 2: Command Line (For Automation)

```bash
conda activate orgaplex

python standalone_scripts/run_one_way_interaction.py \
  --input /path/to/data \
  --output results.xlsx \
  --format excel
```

---

## Project Structure

```
07_R-Scripts_Chahat/
├── src/                          # Core software modules
│   ├── core/                     # Analysis logic
│   │   ├── data_loader.py        # Data extraction & validation
│   │   └── one_way_interaction.py # One-way interaction analysis
│   ├── gui/                      # GUI application
│   │   └── main_window.py        # Main GUI window
│   └── utils/                    # Utility functions
│
├── standalone_scripts/           # Simple, customizable scripts
│   ├── run_one_way_interaction.py
│   └── README.md                 # Customization guide
│
├── Old R_Scripts/                # Original R scripts (reference)
├── tests/                        # Unit tests (future)
├── output/                       # Analysis results
│
├── run_gui.py                    # Launch GUI
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## Usage Examples

### Example 1: Analyze Sample Data (Excel Output)

```bash
conda activate orgaplex

python standalone_scripts/run_one_way_interaction.py \
  --input "Raw_data_for_Orgaplex_Test/Cells without N but with LD" \
  --output "output/my_results.xlsx"
```

### Example 2: CSV Output

```bash
python standalone_scripts/run_one_way_interaction.py \
  --input "/path/to/your/data" \
  --output "output/my_analysis" \
  --format csv
```

This creates:
- `output/my_analysis/one_way_interactions_mean_distance.csv`
- `output/my_analysis/one_way_interactions_count.csv`

---

## Data Structure Requirements

Your input directory should follow one of these structures:

**Structure 1: With LD (Direct)**
```
Input_Directory/
  ├── control_1_ER_Statistics/
  ├── control_1_LD_Statistics/
  ├── control_1_Ly_Statistics/
  └── ...
```

**Structure 2: Without LD (Nested)**
```
Input_Directory/
  ├── Control/
  │   ├── control_1_ER_Statistics/
  │   ├── control_1_Ly_Statistics/
  │   └── ...
  └── ...
```

Each `*_Statistics` folder should contain CSV files named:
```
{cell_id}_{source_organelle}_Shortest_Distance_to_Surfaces_Surfaces={target_organelle}.csv
```

---

## Understanding the Output

### Output Format

**NEW FORMAT (v2.0)**: Row per interaction, column per cell

This format is ideal for:
- Importing into GraphPad Prism
- Statistical analysis in R/Python
- Creating pivot tables in Excel
- Machine learning applications

### Excel Sheets

1. **Mean_Distance**: Mean shortest distances (micrometers)
2. **Count**: Number of measurements per interaction

### Missing Data

- `NaN` in Mean_Distance = No interaction found
- `0` in Count = No measurements available

---

## Customizing the Analysis

See `standalone_scripts/README.md` for detailed examples of:
- Adding custom statistics (median, std, etc.)
- Filtering specific organelles
- Changing distance thresholds
- Custom output formats

**Quick example**: Copy and modify a standalone script

```bash
cp standalone_scripts/run_one_way_interaction.py my_custom_analysis.py
# Edit my_custom_analysis.py to add your customizations
python my_custom_analysis.py --input /path/to/data --output results.xlsx
```

---

## Differences from R Scripts

| Feature | Old R Scripts | New Python Software |
|---------|---------------|---------------------|
| **Output Format** | Separate files per cell | Single table (row per cell) |
| **Organelle Detection** | Hardcoded list | Pattern-based (automatic) |
| **Interface** | Edit script manually | GUI or command-line |
| **Modularity** | Monolithic scripts | Modular architecture |
| **Extensibility** | Difficult | Easy (copy & customize) |
| **Documentation** | Minimal | Comprehensive |

---

## Troubleshooting

### "No module named 'src'"

Run from project root:
```bash
cd /path/to/07_R-Scripts_Chahat
python standalone_scripts/run_one_way_interaction.py ...
```

### "No folders ending with '_Statistics' found"

Check:
1. Input path points to correct directory
2. Folders follow pattern: `{cell_id}_{organelle}_Statistics`
3. You have read permissions

### GUI Not Responding

Large datasets may take several minutes. Watch progress bar and status messages.

---

## Development Roadmap

### Phase 1 (COMPLETED) ✓
- [x] Modular architecture
- [x] Data loader module
- [x] One-way interaction analysis
- [x] New output format (row per cell)
- [x] Standalone scripts
- [x] Refactored GUI

### Phase 2 (Future)
- [ ] 6-way interaction analysis
- [ ] Volume calculations
- [ ] Surface counting
- [ ] Radial distribution analysis
- [ ] Migrate GUI to wxPython
- [ ] Batch processing

---

## Credits

**Original R Scripts**: Chahat Badhan
**Python Software**: Philipp Kaintoch
**Version**: 2.0.0
**Date**: 2025-11-02

---

**Scientific data processing with confidence and ease.**
