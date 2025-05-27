import os
import glob
import shutil
import webbrowser
import argparse
import bisect

HTML_FILE = "countdown-timer.html"
CSS_FILE = "styles.css"
EXPECTED_JS_FILE = "countdown-timer.js"

def find_file_by_extension(directory: str, extension: str) -> str:
    """Find the first file with the given extension in the directory."""
    files = glob.glob(os.path.join(directory, f"*.{extension}"))
    return files[0] if files else None

def setup_and_run_submission(submission_path: str, template_dir: str) -> None:
    """Copy template files and run the submission with student's JS."""
    
    # Find student's JS file
    js_file = find_file_by_extension(submission_path, "js")
    if not js_file:
        print(f"No JavaScript file found in {submission_path}")
        return
    
    # Create a temporary directory in current directory
    temp_dir = os.path.join(".", "temp_run")
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Clean up any existing files in temp_dir
        for file in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, file))
            
        # Copy template files
        for template_file in [HTML_FILE, CSS_FILE]:
            shutil.copy2(
                os.path.join(template_dir, template_file),
                os.path.join(temp_dir, template_file)
            )
        
        # Copy student's JS file with original name
        js_filename = os.path.basename(js_file)
        shutil.copy2(js_file, os.path.join(temp_dir, EXPECTED_JS_FILE))
        if js_filename != EXPECTED_JS_FILE:
            print(f"Expected '{EXPECTED_JS_FILE}' but found '{js_filename}'\nMake sure to name your JS file {EXPECTED_JS_FILE}, otherwise it doesn't connect to the HTML file")
        else:
            print("JS FILE NAMED CORRECTLY")
        
        # Open the HTML file in browser
        html_path = os.path.join(temp_dir, HTML_FILE)
        print(f"\nOpening {html_path} in browser...")
        webbrowser.open(f"file://{os.path.abspath(html_path)}")
        
    except Exception as e:
        print(f"Error setting up submission: {str(e)}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Run student submissions')
    parser.add_argument('--student', type=str, help='Student login to start from', default=None)
    args = parser.parse_args()

    submissions_dir = "./processed_submissions"
    template_dir = "./website_template"
    
    # Get list of student directories and sort alphabetically
    student_dirs = sorted([d for d in os.listdir(submissions_dir) 
                         if os.path.isdir(os.path.join(submissions_dir, d))])
    
    # Find starting index based on provided student login
    start_index = 0
    if args.student:
        start_index = bisect.bisect_left(student_dirs, args.student)
        if start_index == len(student_dirs) or student_dirs[start_index] != args.student:
            print(f"Student {args.student} not found. Starting with next student alphabetically.")
        if start_index == len(student_dirs):
            start_index = 0
            print("Wrapping around to the beginning of the list.")
    
    # Reorder the list to start from the selected student
    student_dirs = student_dirs[start_index:] + student_dirs[:start_index]
    
    for student_dir in student_dirs:
        print("\n" + "=" * 60)
        print(f"Student: {student_dir}")
        print("=" * 60)
        
        submission_path = os.path.join(submissions_dir, student_dir)
        setup_and_run_submission(submission_path, template_dir)
        
        print("\nPress Enter to continue to next submission (or 'q' to quit)...")
        if input().lower() == 'q':
            break

if __name__ == "__main__":
    main()
