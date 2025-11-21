"""
GUI Module for Organelle Analysis Software

This module provides a graphical user interface for running organelle analyses.
It serves as a thin wrapper around the core analysis modules.

The GUI allows users to:
- Select input and output directories
- Choose analysis type (currently: One-Way Interactions)
- Set output format (Excel or CSV)
- Monitor progress in real-time

Author: Philipp Kaintoch
Date: 2025-11-18
Version: 2.2.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
from datetime import datetime

# Import core analysis modules
from ..core.one_way_interaction import OneWayInteractionAnalyzer
from ..core.vol_spher_metrics import VolSpherMetricsAnalyzer
from ..__version__ import __version__


class ToolTip:
    """
    Simple tooltip class for displaying hover help text.
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        """Display the tooltip."""
        if self.tooltip_window or not self.text:
            return

        # Position tooltip near the widget
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background="#FFFFDD",
            relief="solid",
            borderwidth=1,
            font=("Arial", 9),
            wraplength=300
        )
        label.pack()

    def hide_tooltip(self, event=None):
        """Hide the tooltip."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class OrganelleAnalysisGUI:
    """
    Main GUI window for organelle analysis software.

    This is a thin wrapper around core analysis modules, providing
    an accessible graphical interface for experimental researchers.
    """

    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title(f"Organelle Analysis Software v{__version__}")
        self.root.geometry("850x720")
        self.root.resizable(True, True)

        # Variables
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.file_format = tk.StringVar(value='excel')
        self.analysis_type = tk.StringVar(value='one_way')

        # Set default output directory to user's home
        self.output_dir.set(str(Path.home()))

        self.setup_ui()

        # Register close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        """Create and layout all UI elements."""

        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Organelle Analysis Software",
            font=('Arial', 14, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        
        # INPUT/OUTPUT SECTION
        

        row = 1

        # Input Directory
        ttk.Label(
            main_frame,
            text="Input Directory:",
            font=('Arial', 10, 'bold')
        ).grid(row=row, column=0, sticky=tk.W, pady=(0, 5))

        row += 1
        ttk.Entry(
            main_frame,
            textvariable=self.input_dir,
            width=50
        ).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))

        input_browse_btn = ttk.Button(
            main_frame,
            text="Browse...",
            command=self.browse_input_dir
        )
        input_browse_btn.grid(row=row, column=2, padx=(5, 0), pady=(0, 5))
        ToolTip(input_browse_btn, "Select folder containing *_Statistics directories from Imaris")

        # Output Directory
        row += 1
        ttk.Label(
            main_frame,
            text="Output Directory:",
            font=('Arial', 10, 'bold')
        ).grid(row=row, column=0, sticky=tk.W, pady=(15, 5))

        row += 1
        ttk.Entry(
            main_frame,
            textvariable=self.output_dir,
            width=50
        ).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))

        output_browse_btn = ttk.Button(
            main_frame,
            text="Browse...",
            command=self.browse_output_dir
        )
        output_browse_btn.grid(row=row, column=2, padx=(5, 0), pady=(0, 5))
        ToolTip(output_browse_btn, "Select folder where results will be saved")

        # Separator
        row += 1
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20
        )

        
        # ANALYSIS OPTIONS
        

        row += 1
        ttk.Label(
            main_frame,
            text="Analysis Options",
            font=('Arial', 10, 'bold')
        ).grid(row=row, column=0, sticky=tk.W, pady=(0, 10))

        # Analysis Type
        row += 1
        analysis_frame = ttk.Frame(main_frame)
        analysis_frame.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=5)

        ttk.Label(analysis_frame, text="Analysis Type:").pack(side=tk.LEFT, padx=(0, 20))

        oneway_radio = ttk.Radiobutton(
            analysis_frame,
            text="One-Way Interactions",
            variable=self.analysis_type,
            value='one_way'
        )
        oneway_radio.pack(side=tk.LEFT, padx=5)
        ToolTip(oneway_radio, "Calculate mean shortest distances between organelle populations")

        volspher_radio = ttk.Radiobutton(
            analysis_frame,
            text="Vol/Spher-Metrics",
            variable=self.analysis_type,
            value='vol_spher'
        )
        volspher_radio.pack(side=tk.LEFT, padx=5)
        ToolTip(volspher_radio, "Calculate volume and sphericity statistics per organelle")

        # Output Format
        row += 1
        format_frame = ttk.Frame(main_frame)
        format_frame.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=5)

        ttk.Label(format_frame, text="Output Format:").pack(side=tk.LEFT, padx=(0, 20))

        excel_radio = ttk.Radiobutton(
            format_frame,
            text="Excel (.xlsx)",
            variable=self.file_format,
            value='excel'
        )
        excel_radio.pack(side=tk.LEFT, padx=5)
        ToolTip(excel_radio, "Single Excel file with multiple sheets (recommended for most users)")

        csv_radio = ttk.Radiobutton(
            format_frame,
            text="CSV (.csv)",
            variable=self.file_format,
            value='csv'
        )
        csv_radio.pack(side=tk.LEFT, padx=5)
        ToolTip(csv_radio, "Multiple CSV files in output directory (for R/Python analysis)")

        # Separator
        row += 1
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20
        )

        
        # EXECUTION CONTROLS
        

        # Run Button
        row += 1
        self.run_button = ttk.Button(
            main_frame,
            text="Run Analysis",
            command=self.run_analysis
        )
        self.run_button.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        ToolTip(self.run_button, "Start processing the selected analysis with current settings")

        # Progress Bar
        row += 1
        ttk.Label(
            main_frame,
            text="Progress:",
            font=('Arial', 10)
        ).grid(row=row, column=0, sticky=tk.W, pady=(0, 5))

        row += 1
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate', length=400)
        self.progress_bar.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # Status Text
        row += 1
        ttk.Label(
            main_frame,
            text="Status:",
            font=('Arial', 10)
        ).grid(row=row, column=0, sticky=tk.W, pady=(0, 5))

        row += 1
        self.status_text = tk.Text(
            main_frame,
            height=12,
            width=75,
            wrap=tk.WORD,
            state='disabled',
            font=('Courier', 9)
        )
        self.status_text.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E))

        # Configure color tags for different log levels
        self.status_text.tag_config('INFO', foreground='#0066CC')      # Blue
        self.status_text.tag_config('WARNING', foreground='#FF8C00')   # Orange
        self.status_text.tag_config('ERROR', foreground='#CC0000')     # Red
        self.status_text.tag_config('SUCCESS', foreground='#008000')   # Green
        self.status_text.tag_config('DEBUG', foreground='#808080')     # Gray

        # Scrollbar for status text
        scrollbar = ttk.Scrollbar(
            main_frame,
            orient='vertical',
            command=self.status_text.yview
        )
        scrollbar.grid(row=row, column=3, sticky=(tk.N, tk.S))
        self.status_text['yscrollcommand'] = scrollbar.set

    def browse_input_dir(self):
        """Open dialog to select input directory."""
        directory = filedialog.askdirectory(title="Select Input Directory")
        if directory:
            self.input_dir.set(directory)

    def browse_output_dir(self):
        """Open dialog to select output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)

    def update_status(self, message: str):
        """Update the status text box with color-coded formatting."""
        import re

        self.status_text.config(state='normal')

        # Parse log level from message format: [LEVEL] message
        match = re.match(r'\[(\w+)\]', message)
        if match:
            level = match.group(1)
            # Apply color tag if level is recognized
            if level in ['INFO', 'WARNING', 'ERROR', 'DEBUG']:
                self.status_text.insert(tk.END, message + '\n', level)
            elif 'SUCCESS' in message:
                self.status_text.insert(tk.END, message + '\n', 'SUCCESS')
            else:
                self.status_text.insert(tk.END, message + '\n')
        else:
            self.status_text.insert(tk.END, message + '\n')

        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')
        self.root.update_idletasks()

    def validate_inputs(self) -> bool:
        """Validate user inputs before running analysis."""
        if not self.input_dir.get():
            messagebox.showerror("Error", "Please select an input directory")
            return False

        if not Path(self.input_dir.get()).exists():
            messagebox.showerror("Error", "Input directory does not exist")
            return False

        if not self.output_dir.get():
            messagebox.showerror("Error", "Please select an output directory")
            return False

        if not Path(self.output_dir.get()).exists():
            messagebox.showerror("Error", "Output directory does not exist")
            return False

        return True

    def run_analysis_thread(self):
        """
        Run the analysis in a separate thread.

        This method is called by run_analysis() and executes in a background thread
        to keep the GUI responsive.
        """
        import logging

        # Custom handler to redirect logs to GUI
        class GUILogHandler(logging.Handler):
            def __init__(self, callback):
                super().__init__()
                self.callback = callback

            def emit(self, record):
                log_message = self.format(record)
                self.callback(log_message)

        try:
            # Clear status
            self.status_text.config(state='normal')
            self.status_text.delete(1.0, tk.END)
            self.status_text.config(state='disabled')

            # Start progress bar
            self.progress_bar.start(10)

            # Set up GUI logging handler
            gui_handler = GUILogHandler(self.update_status)
            gui_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('[%(levelname)s] %(message)s')
            gui_handler.setFormatter(formatter)

            # Get root logger and add our handler
            root_logger = logging.getLogger()
            root_logger.addHandler(gui_handler)

            try:
                # Get analysis parameters
                input_dir = self.input_dir.get()
                output_dir = Path(self.output_dir.get())
                file_format = self.file_format.get()
                analysis_type = self.analysis_type.get()

                # CORE ANALYSIS EXECUTION
                if analysis_type == 'one_way':
                    # Create output path
                    if file_format == 'excel':
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        output_path = output_dir / f"One_Way_Interactions_{timestamp}.xlsx"
                    else:  # csv
                        output_path = output_dir / "One_Way_Interactions"

                    # Run analysis
                    analyzer = OneWayInteractionAnalyzer(input_dir)
                    analyzer.run(str(output_path), file_format=file_format)

                elif analysis_type == 'vol_spher':
                    # Create output path
                    if file_format == 'excel':
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        output_path = output_dir / f"Vol_Spher_Metrics_{timestamp}.xlsx"
                    else:  # csv
                        output_path = output_dir / "Vol_Spher_Metrics"

                    # Run analysis
                    analyzer = VolSpherMetricsAnalyzer(input_dir)
                    analyzer.run(str(output_path), file_format=file_format)

                else:
                    raise ValueError(f"Unknown analysis type: {analysis_type}")

            finally:
                # Remove GUI handler
                root_logger.removeHandler(gui_handler)

            # Stop progress bar
            self.progress_bar.stop()

            # Show success message
            self.update_status("\n[SUCCESS] Analysis completed successfully!")
            messagebox.showinfo("Success", "Analysis completed successfully!")

        except Exception as e:
            # Stop progress bar
            self.progress_bar.stop()

            # Show error
            error_msg = f"ERROR: {str(e)}"
            self.update_status(f"\n{error_msg}")
            messagebox.showerror("Error", f"Analysis failed:\n{str(e)}")

            # Log exception with traceback
            logging.exception("Analysis failed with exception:")

        finally:
            # Re-enable run button
            self.run_button.config(state='normal')

    def run_analysis(self):
        """Start the analysis (validates inputs and launches thread)."""
        if not self.validate_inputs():
            return

        # Disable run button during analysis
        self.run_button.config(state='disabled')

        # Run in separate thread to keep GUI responsive
        self.analysis_thread = threading.Thread(target=self.run_analysis_thread, daemon=False)
        self.analysis_thread.start()

    def on_closing(self):
        """Handle window close event."""
        if hasattr(self, 'analysis_thread') and self.analysis_thread.is_alive():
            response = messagebox.askyesno(
                "Analysis Running",
                "Analysis is still running. Do you want to wait for it to complete?"
            )
            if response:
                # Wait for thread to finish
                self.analysis_thread.join(timeout=30)
            else:
                # User chose to force quit
                messagebox.showwarning(
                    "Warning",
                    "Forcing quit may result in incomplete output files."
                )
        self.root.destroy()


def launch_gui():
    """Launch the GUI application."""
    root = tk.Tk()
    app = OrganelleAnalysisGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
