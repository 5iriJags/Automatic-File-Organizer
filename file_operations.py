#file_operations.py
import shutil
from pathlib import Path
from datetime import datetime
from file_categorization import categorize_file
# Import both functions from pdf_report
from pdf_report import generate_pdf_report, open_report

def organize_files(directory, organization_rule, dry_run=False):
    directory = Path(directory)
    if not directory.exists():
        print(f"Error: The directory '{directory}' does not exist.")
        return None # Return None on error

    organized_dir = directory / "Organized"
    # No need to create this in dry run, but doesn't hurt
    # organized_dir.mkdir(exist_ok=True)

    changes = []
    errors = []
    pdf_report_path = None # Initialize report path

    for file_path in directory.rglob("*"):
        # Ensure we are not processing files within the future 'Organized' directory
        if file_path.is_file() and organized_dir.resolve() not in file_path.resolve().parents:
            target_category_dir_name = ""
            if organization_rule == "1":
                category = categorize_file(file_path.name)
                target_category_dir_name = category
            elif organization_rule == "2":
                modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                target_category_dir_name = f"{modified_time.year}-{modified_time.month:02d}-{modified_time.day:02d}"
            elif organization_rule == "3":
                size = file_path.stat().st_size
                if size < 1_000_000: # Example: < 1MB
                    target_category_dir_name = "Small"
                elif size < 100_000_000: # Example: < 100MB
                    target_category_dir_name = "Medium"
                else:
                    target_category_dir_name = "Large"
            elif organization_rule == "4":
                ext = file_path.suffix.lstrip(".").lower()
                target_category_dir_name = ext if ext else "NoExtension"
            else:
                print("Invalid choice. Defaulting to File Type organization.")
                category = categorize_file(file_path.name)
                target_category_dir_name = category

            destination_dir = organized_dir / target_category_dir_name
            destination_path = destination_dir / file_path.name

            # Handle potential name collisions
            counter = 1
            original_stem = file_path.stem
            while destination_path.exists() and not dry_run:
                # Only check existence if not in dry run, as files haven't moved yet.
                # Or, better, always plan for the final state even in dry run
                destination_path = destination_dir / f"{original_stem}_{counter}{file_path.suffix}"
                counter += 1

            relative_destination = destination_path.relative_to(directory)

            if dry_run:
                # Record the planned change
                changes.append(f"{file_path.relative_to(directory)} \u2192 {relative_destination}") # Using Unicode arrow
            else:
                try:
                    # Ensure destination directory exists before moving
                    destination_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(file_path), str(destination_path))
                    # Optional: Log successful move if needed
                    # print(f"Moved: {file_path.name} -> {relative_destination}")
                except Exception as e:
                    error_msg = f"Error moving {file_path.name}: {str(e)}"
                    print(error_msg)
                    errors.append(error_msg)

    if dry_run:
        if changes:
            pdf_report_path = generate_pdf_report(directory, changes)
            print(f"Dry run complete. Report generated at: {pdf_report_path}")
        else:
            print("Dry run complete. No files need organizing based on the selected rule.")
        # Removed the input prompt and subsequent call
        return pdf_report_path # Return the path
    else:
        if errors:
            print("Organization complete with errors:")
            for error in errors:
                print(error)
        elif not changes and not errors:
             # If not dry_run, 'changes' list wasn't populated. Need a way to know if work was done.
             # We could count successful moves or check if errors list is empty.
             # Assuming if no errors, it was successful.
             print("Files organized successfully.")
        else:
            # This case might be reached if no files were found initially
            print("Organization process finished.")
        return None # Return None when not in dry run
