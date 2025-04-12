from file_operations import organize_files

if __name__ == "__main__":
    dir_path = input("Enter the directory path to organize: ").strip()
    
    print("\nSelect organization rule:")
    print("1. By File Type (Default)")
    print("2. By Modified Date (Year/Month/Day)")
    print("3. By File Size (Small/Medium/Large)")
    print("4. By Extension")
    organization_rule = input("Enter your choice: ").strip()
    
    dry_run_choice = input("Do you want to run in dry-run mode? (Y/N): ").strip().lower()
    dry_run = dry_run_choice == 'y'
    
    organize_files(dir_path, organization_rule, dry_run=dry_run)
