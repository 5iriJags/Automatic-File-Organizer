#gui.py
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import threading
import sys
from pathlib import Path

# Import necessary functions from other modules
try:
    # Pass a logging function to organize_files
    from file_operations import organize_files
    from pdf_report import open_report
except ImportError as e:
    messagebox.showerror("Import Error", f"Could not import required functions: {e}")
    sys.exit(1)

# --- GUI Setup ---
root = tk.Tk()
root.title("File Organizer")
root.geometry("600x500") # Adjusted size for new buttons and logs

# --- State Variables ---
dir_path_var = tk.StringVar()
organization_rule_var = tk.StringVar(value="1") # Default to File Type
dry_run_var = tk.BooleanVar(value=True) # Default to dry run enabled
last_dry_run_pdf_path = None # Store the path to the last dry run report
last_dry_run_params = None # Store params used for the last dry run

# --- Logging Function ---
def log_message(message):
    """Appends a message to the log text area in a thread-safe way."""
    log_text.insert(tk.END, message + "")
    log_text.see(tk.END) # Scroll to the end

# --- GUI Functions ---
def browse_directory():
    directory = filedialog.askdirectory()
    if directory:
        dir_path_var.set(directory)
        reset_dry_run_state() # Reset if directory changes

def reset_dry_run_state(*args):
    """Resets buttons related to the dry run state."""
    global last_dry_run_pdf_path, last_dry_run_params
    last_dry_run_pdf_path = None
    last_dry_run_params = None
    view_report_button.config(state=tk.DISABLED)
    apply_changes_button.config(state=tk.DISABLED)
    start_button.config(state=tk.NORMAL) # Re-enable start button if it was disabled
    # No need to re-enable browse_button here, it's handled in the run functions

def view_report_command():
    if last_dry_run_pdf_path and os.path.exists(last_dry_run_pdf_path):
        log_message(f"Attempting to open report: {last_dry_run_pdf_path}")
        if open_report(last_dry_run_pdf_path):
            log_message("Report opened successfully.")
        else:
            log_message("Failed to open report using system viewer.")
            messagebox.showerror("Error", f"Could not open the report.Please find it manually at:{last_dry_run_pdf_path}")
    else:
        log_message("Error: Report path not found or file does not exist.")
        messagebox.showerror("Error", "Could not find the report file.")
        reset_dry_run_state()

def run_organization_thread(dir_path, organization_rule, dry_run):
    """The actual function run in a separate thread."""
    global last_dry_run_pdf_path, last_dry_run_params

    # Disable buttons during operation
    root.after(0, lambda: start_button.config(state=tk.DISABLED))
    root.after(0, lambda: browse_button.config(state=tk.DISABLED))
    root.after(0, lambda: view_report_button.config(state=tk.DISABLED))
    root.after(0, lambda: apply_changes_button.config(state=tk.DISABLED))
    root.after(0, log_message, f"---") # Separator
    root.after(0, log_message, f"Starting {'Dry Run' if dry_run else 'Organization'}...")
    root.after(0, log_message, f"Directory: {dir_path}")
    root.after(0, log_message, f"Rule: {organization_rule}")

    try:
        # Pass the GUI logging function if organize_files accepts it (requires modification)
        # For now, organize_files prints to console, we log basic steps here.
        report_path_or_none = organize_files(Path(dir_path), organization_rule, dry_run=dry_run)

        if dry_run:
            if report_path_or_none:
                last_dry_run_pdf_path = str(report_path_or_none)
                last_dry_run_params = {"dir_path": dir_path, "rule": organization_rule}
                root.after(0, log_message, f"Dry run complete. Report: {last_dry_run_pdf_path}")
                root.after(0, log_message, "Review the report, then click 'Apply Changes' to proceed.")
                root.after(0, lambda: view_report_button.config(state=tk.NORMAL))
                root.after(0, lambda: apply_changes_button.config(state=tk.NORMAL))
                # Keep start_button disabled until reset
            else:
                root.after(0, log_message, "Dry run complete. No changes proposed.")
                reset_dry_run_state() # Reset state, enable Start button
        else:
            # This was an actual run (either initial or after dry run confirmation)
            root.after(0, log_message, "Organization complete.")
            messagebox.showinfo("Success", "Files organized successfully!")
            reset_dry_run_state() # Reset state

    except Exception as e:
        error_msg = f"Error during organization: {e}"
        root.after(0, log_message, error_msg)
        messagebox.showerror("Error", error_msg)
        reset_dry_run_state() # Reset state on error
    finally:
        # Re-enable browse button; start button remains disabled if dry run succeeded
        # It gets re-enabled via reset_dry_run_state when appropriate
        root.after(0, lambda: browse_button.config(state=tk.NORMAL))
        root.after(0, log_message, "Operation finished.")

def start_organization_command():
    dir_path = dir_path_var.get()
    organization_rule = organization_rule_var.get()
    dry_run = dry_run_var.get()

    if not os.path.isdir(dir_path):
        messagebox.showerror("Error", "Please select a valid directory.")
        log_message("Error: Invalid directory selected.")
        return

    # Run the potentially long-running task in a separate thread
    thread = threading.Thread(target=run_organization_thread, args=(dir_path, organization_rule, dry_run), daemon=True)
    thread.start()

def apply_changes_command():
    if not last_dry_run_params:
        messagebox.showerror("Error", "No previous dry run data found to apply.")
        reset_dry_run_state()
        return

    dir_path = last_dry_run_params["dir_path"]
    organization_rule = last_dry_run_params["rule"]

    log_message("Applying changes from last dry run...")

    # Run the organization with dry_run=False using stored parameters
    thread = threading.Thread(target=run_organization_thread, args=(dir_path, organization_rule, False), daemon=True)
    thread.start()

# --- Widgets ---
# Frame for directory selection
dir_frame = tk.Frame(root)
dir_frame.pack(pady=5, padx=10, fill=tk.X)
tk.Label(dir_frame, text="Directory:").pack(side=tk.LEFT, padx=(0, 5))
dir_entry = tk.Entry(dir_frame, textvariable=dir_path_var, width=50)
dir_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
browse_button = tk.Button(dir_frame, text="Browse...", command=browse_directory)
browse_button.pack(side=tk.LEFT, padx=(5, 0))

# Frame for rules and options
controls_frame = tk.Frame(root)
controls_frame.pack(pady=5, padx=10, fill=tk.X)

# Organization Rule (within controls_frame)
rule_frame = tk.LabelFrame(controls_frame, text="Organization Rule", padx=10, pady=5)
rule_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True, padx=(0, 10))
rules = [
    ("By File Type", "1"),
    ("By Modified Date", "2"),
    ("By File Size", "3"),
    ("By Extension", "4")
]
for text, value in rules:
    tk.Radiobutton(rule_frame, text=text, variable=organization_rule_var, value=value, command=reset_dry_run_state).pack(anchor=tk.W)

# Options (within controls_frame)
options_frame = tk.Frame(controls_frame)
options_frame.pack(side=tk.LEFT, padx=10)
tk.Checkbutton(options_frame, text="Dry Run (Preview first)", variable=dry_run_var, command=reset_dry_run_state).pack(anchor=tk.W)

# Action Buttons Frame
action_frame = tk.Frame(root)
action_frame.pack(pady=10, padx=10, fill=tk.X)

start_button = tk.Button(action_frame, text="Start Organizing", command=start_organization_command, width=15)
start_button.pack(side=tk.LEFT, padx=5)

view_report_button = tk.Button(action_frame, text="View Report", command=view_report_command, width=15, state=tk.DISABLED)
view_report_button.pack(side=tk.LEFT, padx=5)

apply_changes_button = tk.Button(action_frame, text="Apply Changes", command=apply_changes_command, width=15, state=tk.DISABLED)
apply_changes_button.pack(side=tk.LEFT, padx=5)


# Log Area
log_frame = tk.LabelFrame(root, text="Logs", padx=10, pady=5)
log_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD, state=tk.NORMAL) # Start enabled
log_text.pack(fill=tk.BOTH, expand=True)
log_message("Ready. Select a directory and options, then click 'Start Organizing'.")

# --- Bindings for Reset ---
# Reset if parameters change after a dry run
dir_path_var.trace_add("write", reset_dry_run_state)
organization_rule_var.trace_add("write", reset_dry_run_state)
# dry_run_var is handled by its command, but tracing doesn't hurt
# dry_run_var.trace_add("write", reset_dry_run_state)

# --- Run GUI ---
root.mainloop()
