import os
import zipfile
import shutil
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Process student submissions from a directory.')
    parser.add_argument('submissions_dir', help='Directory containing the student submissions')
    parser.add_argument('target_dir', help='Directory where processed submissions will be stored')
    return parser.parse_args()

# Specify the directory containing the files
def find_content_directory(folder_path):
    """Find the directory level that contains actual files."""
    contents = os.listdir(folder_path)
    # Filter out __MACOSX directory
    contents = [item for item in contents if item != '__MACOSX']
    
    dirs = [item for item in contents if os.path.isdir(os.path.join(folder_path, item))]
    files = [item for item in contents if os.path.isfile(os.path.join(folder_path, item))]
    
    # If we have files at this level, this is our target
    if files:
        return folder_path
    
    # If we have more than one directory and no files, that's an error case
    if len(dirs) > 1:
        return None
    
    # If we have exactly one directory, go deeper
    if len(dirs) == 1:
        return find_content_directory(os.path.join(folder_path, dirs[0]))
    
    # If we have no files and no directories, return None
    return None

def process_submission(file_path, student_folder, temp_directory):
    """Process a single submission file."""
    file_name = os.path.basename(file_path)
    
    # Create student folder if it doesn't exist
    os.makedirs(student_folder, exist_ok=True)
    
    # Handle zip archives
    if zipfile.is_zipfile(file_path):
        temp_extract_path = os.path.join(temp_directory, os.path.splitext(file_name)[0])
        os.makedirs(temp_extract_path, exist_ok=True)
        
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            # Filter out __MACOSX directory during extraction
            members = [m for m in zip_ref.namelist() if not m.startswith('__MACOSX/')]
            zip_ref.extractall(temp_extract_path, members=members)
        
        # Find the directory containing actual content
        content_dir = find_content_directory(temp_extract_path)
        
        if content_dir is None:
            print(f"Error processing {file_name}: Multiple subdirectories found at same level or no files found")
            return False
        
        # Copy all contents to student folder
        for item in os.listdir(content_dir):
            source_path = os.path.join(content_dir, item)
            target_path = os.path.join(student_folder, item)
            
            if os.path.exists(target_path):
                print(f"Warning: {item} already exists in {student_folder}")
                continue
                
            if os.path.isfile(source_path):
                shutil.copy2(source_path, target_path)
            else:
                shutil.copytree(source_path, target_path)
    
    # Handle raw files
    else:
        # Extract the actual filename (after the last underscore)
        parts = file_name.split("_")
        # Check if the fourth element (index 3) is an integer - case of a LATE submission when there is one extra field
        try:
            int(parts[3])  # Try to convert to integer
            base_name = "_".join(parts[4:])  # If successful, start from fifth element
        except (IndexError, ValueError):
            base_name = "_".join(parts[3:])  # If not an integer or doesn't exist, start from fourth element
            
        target_path = os.path.join(student_folder, base_name)
        
        if os.path.exists(target_path):
            print(f"Warning: {base_name} already exists in {student_folder}")
            return False
            
        shutil.copy2(file_path, target_path)
    
    return True

def main():
    args = parse_args()
    
    # Use command line arguments instead of hardcoded paths
    directory = args.submissions_dir
    target_directory = args.target_dir
    temp_directory = "./temp_processing"
    
    # Validate directories
    if not os.path.exists(directory):
        print(f"Error: Submissions directory '{directory}' does not exist")
        return
    
    # Clear target directory if it exists
    if os.path.exists(target_directory):
        print(f"Clearing target directory: {target_directory}")
        shutil.rmtree(target_directory)
    
    # Create necessary directories
    os.makedirs(target_directory, exist_ok=True)
    os.makedirs(temp_directory, exist_ok=True)
    
    # Process each file in the submissions directory
    for file_name in os.listdir(directory):
        if file_name.startswith('.'):
            continue
            
        file_path = os.path.join(directory, file_name)
        if not os.path.isfile(file_path):
            continue
            
        # Get student login (first part before underscore)
        student_login = file_name.split("_")[0]
        student_folder = os.path.join(target_directory, student_login)
        
        success = process_submission(file_path, student_folder, temp_directory)
        if not success:
            print(f"Failed to process {file_name}")
    
    # Clean up temporary directory
    shutil.rmtree(temp_directory, ignore_errors=True)
    print("Processing complete. Temporary files cleaned up.")

if __name__ == "__main__":
    main()
