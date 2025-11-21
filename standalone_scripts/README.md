# Standalone Scripts for Organelle Analysis

This folder contains simple, standalone scripts that can be run independently without the GUI. These scripts are designed to be **easy to copy and customize** for your specific analysis needs.

## Available Scripts

### 1. One-Way Interaction Analysis
**Script:** `run_one_way_interaction.py`

Analyzes one-way organelle interactions (e.g., ER-to-LD, M-to-P) and exports results with **one row per interaction**.

**Usage:**
```bash
# Activate conda environment
conda activate orgaplex

# Run with Excel output (default)
python run_one_way_interaction.py \
  --input /path/to/data \
  --output results.xlsx

# Run with CSV output
python run_one_way_interaction.py \
  --input /path/to/data \
  --output ./output_folder \
  --format csv
```

**Output Format:**
```
Interaction  | control_1 | control_2 | control_3 | ...
ER-to-LD     | 5.87      | 6.12      | 7.33      | ...
ER-to-Ly     | 0.27      | 0.31      | 0.09      | ...
M-to-ER      | 0.001     | 0.013     | 0.000     | ...
```

Two sheets/files are created:
- `Mean_Distance`: Mean shortest distances for each interaction
- `Count`: Number of measurements for each interaction

---

## Customizing the Scripts

These scripts are designed to be **copied and modified** for your specific needs. Here are some common customizations:

### Adding Custom Statistics

To calculate median or standard deviation in addition to mean:

1. Copy the script to a new file (e.g., `my_custom_analysis.py`)
2. Locate the `analyze_cell()` method in `src/core/one_way_interaction.py`
3. Add your custom calculations:

```python
# In analyze_cell() method
interactions[interaction_name] = {
    'mean': distances.mean(),
    'median': distances.median(),    # ADD THIS
    'std': distances.std(),           # ADD THIS
    'count': len(distances)
}
```

4. Update `build_summary_tables()` to create DataFrames for your new metrics

### Filtering Specific Organelles

To analyze only specific organelle pairs (e.g., only ER interactions):

```python
# In analyze_cell() method, add a filter:
if source_org != "ER":
    continue  # Skip non-ER organelles
```

### Changing Distance Thresholds

To count only interactions within a certain distance:

```python
# In analyze_cell() method:
close_distances = distances[distances <= 1.0]  # Only distances <= 1.0
mean_distance = close_distances.mean()
count = len(close_distances)
```

### Exporting Additional Formats

To add JSON export:

```python
def export_to_json(self, output_path: str):
    import json
    data = self.mean_distance_df.to_dict(orient='records')
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
```

---

## Data Structure Requirements

Your input directory should follow one of these structures:

### Structure 1: With LD (Direct)
```
Input_Directory/
  ├── control_1_ER_Statistics/
  ├── control_1_LD_Statistics/
  ├── control_1_Ly_Statistics/
  ├── control_1_M_Statistics/
  └── ...
```

### Structure 2: Without LD (Nested)
```
Input_Directory/
  ├── Control/
  │   ├── control_1_ER_Statistics/
  │   ├── control_1_Ly_Statistics/
  │   └── ...
  ├── Treatment/
  │   ├── treated_1_ER_Statistics/
  │   └── ...
  └── ...
```

---

## Troubleshooting

### Import Error: `No module named 'src'`

Make sure you run the script from the project root directory, or the script will automatically add the parent directory to the Python path.

### Data Not Found

Check that:
1. Input directory contains folders ending with `_Statistics`
2. Folder names follow the pattern: `{cell_id}_{organelle}_Statistics`
3. Distance files exist: `*_Shortest_Distance_to_Surfaces_Surfaces=*.csv`

### Memory Issues with Large Datasets

If processing very large datasets (100+ cells), consider:
1. Processing cells in batches
2. Using CSV output instead of Excel
3. Increasing available RAM

---

## Tips for Beginners

1. **Start simple:** Run the script as-is first to understand the output
2. **Make incremental changes:** Copy the script and change one thing at a time
3. **Test on small data:** Use a subset of cells for testing modifications
4. **Keep backups:** Save copies of working versions before making changes
5. **Read the code:** The scripts are heavily commented to help you understand what each section does

---

## Getting Help

For questions or issues:
1. Read the main `README.md` in the project root
2. Check the code comments in the core modules (`src/core/`)
3. Look at the example data in `Raw_data_for_Orgaplex_Test/`


