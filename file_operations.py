import shutil
from pathlib import Path
from datetime import datetime
from file_categorization import categorize_file
from pdf_report import generate_pdf_report

def organize_files(directory, organization_rule, dry_run=False):
    directory = Path(directory)
    if not directory.exists():
        print(f"Error: The directory '{directory}' does not exist.")
        return

    organized_dir = directory / "Organized"
    organized_dir.mkdir(exist_ok=True)

    changes = []
    errors = []

    for file_path in directory.rglob("*"):
        if file_path.is_file():
            if organization_rule == "1":
                category = categorize_file(file_path.name)
                category_dir = organized_dir / category
            elif organization_rule == "2":
                modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                category_dir = organized_dir / f"{modified_time.year}-{modified_time.month:02d}-{modified_time.day:02d}"
            elif organization_rule == "3":
                size = file_path.stat().st_size
                if size < 1_000_000:
                    category_dir = organized_dir / "Small"
                elif size < 10_000_000:
                    category_dir = organized_dir / "Medium"
                else:
                    category_dir = organized_dir / "Large"
            elif organization_rule == "4":
                category_dir = organized_dir / file_path.suffix.lstrip(".")
            else:
                print("Invalid choice. Defaulting to File Type organization.")
                category = categorize_file(file_path.name)
                category_dir = organized_dir / category
            
            category_dir.mkdir(exist_ok=True)
            destination = category_dir / file_path.name
            counter = 1
            while destination.exists():
                destination = category_dir / f"{file_path.stem}_{counter}{file_path.suffix}"
                counter += 1

            relative_destination = destination.relative_to(directory)
            
            if dry_run:
                changes.append(f"{file_path.relative_to(directory)} → {relative_destination}")
            else:
                try:
                    shutil.move(str(file_path), str(destination))
                except Exception as e:
                    errors.append(f"Error moving {file_path.name}: {str(e)}")
    
    if dry_run:
        generate_pdf_report(directory, changes)
        print("\nNo files were moved. Review the report and choose whether to apply changes.")
        proceed = input("Do you want to apply these changes? (Y/N): ").strip().lower()
        if proceed == 'y':
            organize_files(directory, organization_rule, dry_run=False)
        else:
            print("Operation canceled. No files were moved.")
    else:
        if errors:
            print("\nErrors encountered during execution:")
            for error in errors:
                print(error)
        else:
            print("\nFiles organized successfully.")
