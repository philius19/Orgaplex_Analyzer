"""
GUI Module for Organelle Analysis Software

This module provides a graphical user interface for running organelle analyses.
It serves as a thin wrapper around the core analysis modules.

The GUI allows users to:
- Select input and output directories
- Choose analysis type (currently: One-Way Interactions)
- Set output format (Excel or CSV)
- Monitor progress in real-time

AUTHOR: Philipp Kaintoch
DATE: 2025-11-02
VERSION: 2.0.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
from datetime import datetime
import sys

# Import core analysis modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.core.one_way_interaction import OneWayInteractionAnalyzer


class OrganelleAnalysisGUI:
    """
    Main GUI window for organelle analysis software.

    This is a thin wrapper around core analysis modules, providing
    a user-friendly interface for non-technical users.
    """

    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Organelle Analysis Software v2.0")
        self.root.geometry("700x650")
        self.root.resizable(True, True)

        # Variables
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.file_format = tk.StringVar(value='excel')
        self.analysis_type = tk.StringVar(value='one_way')

        # Set default output directory to user's home
        self.output_dir.set(str(Path.home()))

        self.setup_ui()

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

        # =====================================================================
        # INPUT/OUTPUT SECTION
        # =====================================================================

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

        ttk.Button(
            main_frame,
            text="Browse...",
            command=self.browse_input_dir
        ).grid(row=row, column=2, padx=(5, 0), pady=(0, 5))

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

        ttk.Button(
            main_frame,
            text="Browse...",
            command=self.browse_output_dir
        ).grid(row=row, column=2, padx=(5, 0), pady=(0, 5))

        # Separator
        row += 1
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20
        )

        # =====================================================================
        # ANALYSIS OPTIONS
        # =====================================================================

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
        ttk.Radiobutton(
            analysis_frame,
            text="One-Way Interactions",
            variable=self.analysis_type,
            value='one_way'
        ).pack(side=tk.LEFT, padx=5)

        # Output Format
        row += 1
        format_frame = ttk.Frame(main_frame)
        format_frame.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=5)

        ttk.Label(format_frame, text="Output Format:").pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(
            format_frame,
            text="Excel (.xlsx)",
            variable=self.file_format,
            value='excel'
        ).pack(side=tk.LEFT, padx=5)

        ttk.Radiobutton(
            format_frame,
            text="CSV (.csv)",
            variable=self.file_format,
            value='csv'
        ).pack(side=tk.LEFT, padx=5)

        # Separator
        row += 1
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20
        )

        # =====================================================================
        # EXECUTION CONTROLS
        # =====================================================================

        # Run Button
        row += 1
        self.run_button = ttk.Button(
            main_frame,
            text="Run Analysis",
            command=self.run_analysis
        )
        self.run_button.grid(row=row, column=0, columnspan=3, pady=(0, 20))

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
        """Update the status text box."""
        self.status_text.config(state='normal')
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
        try:
            # Clear status
            self.status_text.config(state='normal')
            self.status_text.delete(1.0, tk.END)
            self.status_text.config(state='disabled')

            # Start progress bar
            self.progress_bar.start(10)

            # ===================================================================
            # GUI INTEGRATION: Redirect print statements to GUI
            # ===================================================================
            import io
            import contextlib

            # Capture stdout
            captured_output = io.StringIO()

            with contextlib.redirect_stdout(captured_output):
                # Get analysis parameters
                input_dir = self.input_dir.get()
                output_dir = Path(self.output_dir.get())
                file_format = self.file_format.get()
                analysis_type = self.analysis_type.get()

                # ===================================================================
                # CORE ANALYSIS EXECUTION
                # This section calls the core analysis modules
                # ===================================================================

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

                else:
                    raise ValueError(f"Unknown analysis type: {analysis_type}")

            # ===================================================================
            # END CORE ANALYSIS EXECUTION
            # ===================================================================

            # Display captured output in GUI
            output = captured_output.getvalue()
            for line in output.split('\n'):
                if line.strip():
                    self.update_status(line)

            # Stop progress bar
            self.progress_bar.stop()

            # Show success message
            self.update_status("\n✓ Analysis completed successfully!")
            messagebox.showinfo("Success", "Analysis completed successfully!")

        except Exception as e:
            # Stop progress bar
            self.progress_bar.stop()

            # Show error
            error_msg = f"ERROR: {str(e)}"
            self.update_status(f"\n{error_msg}")
            messagebox.showerror("Error", f"Analysis failed:\n{str(e)}")

            # Print traceback for debugging
            import traceback
            traceback.print_exc()

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
        thread = threading.Thread(target=self.run_analysis_thread, daemon=True)
        thread.start()


def launch_gui():
    """Launch the GUI application."""
    root = tk.Tk()
    app = OrganelleAnalysisGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
