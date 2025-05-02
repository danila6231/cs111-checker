import os
import zipfile
import shutil

# Specify the directory containing the files
directory = "./submissions"
target_directory = "./processed_submissions"

# Function to find the directory containing an HTML file
def find_html_root(folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".html"):
                return root  # Return the directory where the first HTML file is found
    return None

# Function to move files and directories to the student root folder
def move_contents_to_root(source_folder, student_folder):
    for item in os.listdir(source_folder):
        source_path = os.path.join(source_folder, item)
        target_path = os.path.join(student_folder, item)

        if os.path.exists(target_path):
            if os.path.isdir(target_path):
                # Merge directories if they already exist
                for sub_item in os.listdir(source_path):
                    shutil.move(os.path.join(source_path, sub_item), target_path)
                os.rmdir(source_path)  # Remove empty source directory
            else:
                # Handle duplicate files (rename or skip)
                base, ext = os.path.splitext(item)
                counter = 1
                while os.path.exists(target_path):
                    target_path = os.path.join(student_folder, f"{base}_{counter}{ext}")
                    counter += 1
                shutil.move(source_path, target_path)
        else:
            shutil.move(source_path, target_path)

# Iterate over each file in the directory
for file_name in os.listdir(directory):
    file_path = os.path.join(directory, file_name)

    if file_name[0] == '.':
        continue  # Skip hidden files

    if not os.path.isfile(file_path):
        continue  # Skip if it's not a file

    # Parse the student name from the file name
    student_name = file_name.split("_")[0]

    # Create a folder for the student if it doesn't already exist
    student_folder = os.path.join(target_directory, student_name)
    os.makedirs(student_folder, exist_ok=True)

    # Check if the file is a zip archive
    if zipfile.is_zipfile(file_path):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            temp_extract_path = os.path.join(student_folder, "temp")
            zip_ref.extractall(temp_extract_path)

            # Find the root directory where an HTML file exists
            html_root = find_html_root(temp_extract_path)

            if html_root:
                move_contents_to_root(html_root, student_folder)
            else:
                print(f"No HTML file found in {file_name}, keeping extracted files as is.")

            # Remove the temporary extracted folder
            shutil.rmtree(temp_extract_path, ignore_errors=True)

    else:
        # Extract the base file name (filename.extension)
        base_name = "_".join(file_name.split("_")[3:])
        new_file_path = os.path.join(student_folder, base_name)
        os.rename(file_path, new_file_path)

print("Files organized successfully.")
