import os
import re
import json
import subprocess
import tempfile
import shutil
from bs4 import BeautifulSoup
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import glob
import argparse
import bisect
import webbrowser

def find_file_by_extension(directory: str, extension: str) -> Optional[str]:
    """Find the first file with the given extension in the directory."""
    files = glob.glob(os.path.join(directory, f"*.{extension}"))
    return files[0] if files else None

@dataclass
class GradingResult:
    points: float
    comments: List[str]
    max_points: float

class RubricItem(ABC):
    def __init__(self, name: str, max_points: float):
        self.name = name
        self.max_points = max_points
    
    @abstractmethod
    def grade(self, submission_path: str) -> GradingResult:
        pass

def run_tests(js_file: str, test_template_path: str) -> Dict[str, Any]:
    """Run the unit tests and return the results."""
    # Use a fixed directory for testing
    temp_dir = 'temp_test'
    # Clear the directory if it exists, or create it
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    # Install @babel/parser if not already installed
    try:
        subprocess.run(['npm', 'list', '@babel/parser'], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        subprocess.run(['npm', 'install', '@babel/parser', '--no-save'], check=True)

    # Create a temporary Node.js script to parse and extract functions
    parser_script = '''
    const parser = require('@babel/parser');
    const fs = require('fs');

    const code = fs.readFileSync(process.argv[2], 'utf-8');
    const ast = parser.parse(code);

    const functions = {};
    ast.program.body.forEach(node => {
        if (node.type === 'FunctionDeclaration' && 
            ['validateDate', 'validateTime', 'calculatePriority'].includes(node.id.name)) {
            functions[node.id.name] = code.slice(node.start, node.end);
        }
    });

    // Add module.exports
    const exportStr = "module.exports = { validateDate, validateTime, calculatePriority };\\n";
    
    const output = Object.values(functions).join('\\n\\n') + '\\n\\n' + exportStr;
    fs.writeFileSync(process.argv[3], output);
    '''

    # Save the parser script
    parser_script_path = os.path.join(temp_dir, 'parser.js')
    with open(parser_script_path, 'w') as f:
        f.write(parser_script)

    # Extract functions using the parser
    student_solution_path = os.path.join(temp_dir, 'student_solution.js')
    try:
        subprocess.run(['node', parser_script_path, js_file, student_solution_path], check=True)
    except subprocess.CalledProcessError:
        return {
            'success': False,
            'output': '',
            'error': 'Failed to parse student code'
        }

    # Copy the test template
    test_file_path = os.path.join(temp_dir, 'test.js')
    shutil.copy2(test_template_path, test_file_path)

    # Run the tests using Node.js and Mocha
    try:
        result = subprocess.run(
            ['npx', 'mocha', test_file_path],
            capture_output=True,
            text=True,
            timeout=10  # 10 second timeout
        )
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'output': '',
            'error': 'Test execution timed out'
        }
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': str(e)
        }

class ValidateDateGrader(RubricItem):
    def __init__(self):
        super().__init__("validateDate() Function", 6.0)
    
    def grade(self, submission_path: str) -> GradingResult:
        js_file = find_file_by_extension(submission_path, "js")
        if not js_file:
            return GradingResult(0, ["No JavaScript file found in submission"], self.max_points)
        
        test_results = run_tests(js_file, "./test_template.js")
        print(test_results['output'])
        
        if not test_results['success']:
            # Parse test output to identify which specific tests failed
            output = test_results['output']
            points = 6.0
            comments = []
            
            # Check for specific test failures and deduct points accordingly
            if "should accept valid dates" in output and "failing" in output:
                points -= 1
                comments.append("Failed to validate correct date formats")
            
            if "should reject strings without exactly one forward slash" in output and "failing" in output:
                points -= 1
                comments.append("Failed to properly check for single forward slash")
            
            if "should reject parts that are not exactly 2 digits" in output and "failing" in output:
                points -= 1
                comments.append("Failed to verify exactly 2 digits in each part")
            
            if "should reject non-numeric characters" in output and "failing" in output:
                points -= 1
                comments.append("Failed to validate numeric characters")
            
            if "should reject invalid months" in output and "failing" in output:
                points -= 1
                comments.append("Failed to properly validate month range")
            
            if "should reject invalid days for each month" in output and "failing" in output:
                points -= 1
                comments.append("Failed to properly validate days for specific months")
            
            if not comments:
                comments.append("Unknown test failures")
                points = max(1, points - 2)
            
            return GradingResult(max(0, points), comments, self.max_points)
        
        return GradingResult(6.0, ["All validateDate tests passed successfully"], self.max_points)

class ValidateTimeGrader(RubricItem):
    def __init__(self):
        super().__init__("validateTime() Function", 6.0)
    
    def grade(self, submission_path: str) -> GradingResult:
        js_file = find_file_by_extension(submission_path, "js")
        if not js_file:
            return GradingResult(0, ["No JavaScript file found in submission"], self.max_points)
        
        test_results = run_tests(js_file, "./test_template.js")
        
        if not test_results['success']:
            # Parse test output to identify which specific tests failed
            output = test_results['output']
            points = 6.0
            comments = []
            
            # Check for specific test failures and deduct points accordingly
            if "should accept valid times" in output and "failing" in output:
                points -= 1
                comments.append("Failed to validate correct time formats")
            
            if "should reject strings without exactly one colon" in output and "failing" in output:
                points -= 1
                comments.append("Failed to properly check for single colon")
            
            if "should reject parts that are not exactly 2 digits" in output and "failing" in output:
                points -= 1
                comments.append("Failed to verify exactly 2 digits in each part")
            
            if "should reject non-numeric characters" in output and "failing" in output:
                points -= 1
                comments.append("Failed to validate numeric characters")
            
            if "should reject invalid hours" in output and "failing" in output:
                points -= 1
                comments.append("Failed to properly validate hours range (0-23)")
            
            if "should reject invalid minutes" in output and "failing" in output:
                points -= 1
                comments.append("Failed to properly validate minutes range (0-59)")
            
            if not comments:
                comments.append("Unknown test failures")
                points = max(1, points - 2)
            
            return GradingResult(max(0, points), comments, self.max_points)
        
        return GradingResult(6.0, ["All validateTime tests passed successfully"], self.max_points)

class CalculatePriorityGrader(RubricItem):
    def __init__(self):
        super().__init__("calculatePriority() Function", 8.0)
    
    def grade(self, submission_path: str) -> GradingResult:
        js_file = find_file_by_extension(submission_path, "js")
        if not js_file:
            return GradingResult(0, ["No JavaScript file found in submission"], self.max_points)
        
        test_results = run_tests(js_file, "./test_template.js")
        
        if not test_results['success']:
            # Parse test output to identify which specific tests failed
            output = test_results['output']
            points = 8.0
            comments = []
            
            # Check for specific test failures and deduct points accordingly
            if "should correctly calculate priority for valid inputs" in output and "failing" in output:
                points -= 3
                comments.append("Failed to calculate correct priorities for various scenarios")
            
            if "should handle edge cases correctly" in output and "failing" in output:
                points -= 3
                comments.append("Failed to handle edge cases properly")
            
            if "should return 0 for invalid inputs" in output and "failing" in output:
                points -= 2
                comments.append("Failed to handle invalid inputs properly")
            
            if not comments:
                comments.append("Unknown test failures")
                points = max(1, points - 4)
            
            return GradingResult(max(0, points), comments, self.max_points)
        
        return GradingResult(8.0, ["All calculatePriority tests passed successfully"], self.max_points)

class Project2Grader:
    def __init__(self):
        self.rubric_items = [
            ValidateDateGrader(),
            ValidateTimeGrader(),
            CalculatePriorityGrader()
        ]
    
    def grade_submission(self, submission_path: str) -> Dict[str, Any]:
        results = {}
        total_points = 0
        total_possible = 0
        
        # First check if required files exist
        js_file = find_file_by_extension(submission_path, "js")
        
        if not js_file:
            return {
                "error": "Missing required JavaScript file",
                "total": {
                    "points": 0,
                    "max_points": sum(item.max_points for item in self.rubric_items),
                    "percentage": 0
                }
            }
        
        # Check if Node.js and Mocha are available
        try:
            subprocess.run(['node', '--version'], capture_output=True, check=True)
            subprocess.run(['npx', 'mocha', '--version'], capture_output=True, check=True)
        except subprocess.CalledProcessError:
            return {
                "error": "Node.js and/or Mocha are not installed. Please install them to run the tests.",
                "total": {
                    "points": 0,
                    "max_points": sum(item.max_points for item in self.rubric_items),
                    "percentage": 0
                }
            }
        
        for item in self.rubric_items:
            result = item.grade(submission_path)
            results[item.name] = {
                "points": result.points,
                "max_points": result.max_points,
                "comments": result.comments
            }
            total_points += result.points
            total_possible += result.max_points
        
        results["total"] = {
            "points": total_points,
            "max_points": total_possible,
            "percentage": (total_points / total_possible) * 100 if total_possible > 0 else 0
        }
        
        return results

def print_submission_summary(student: str, result: Dict[str, Any]) -> None:
    """Print a detailed summary for a single submission."""
    print("\n" + "=" * 60)
    print(f"Student: {student}")
    print("=" * 60)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    print("\nDetailed Grading Breakdown:")
    print("-" * 30)
    
    for item_name, item_result in result.items():
        if item_name != "total":
            print(f"\n{item_name}:")
            print(f"Score: {item_result['points']}/{item_result['max_points']}")
            # Only show comments if points are less than max_points
            if item_result['points'] < item_result['max_points'] and item_result['comments']:
                print("Comments:")
                for comment in item_result['comments']:
                    print(f"  - {comment}")
    
    print("\nTotal Results:")
    print(f"Total Score: {result['total']['points']}/{result['total']['max_points']}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Grade student submissions')
    parser.add_argument('--student', type=str, help='Student login to start grading from', default=None)
    args = parser.parse_args()

    submissions_dir = "./processed_submissions"  # Directory containing student submissions
    results = {}
    
    # Get list of student directories and sort alphabetically
    student_dirs = sorted([d for d in os.listdir(submissions_dir) 
                         if os.path.isdir(os.path.join(submissions_dir, d))])
    
    # Find starting index based on provided student login
    start_index = 0
    if args.student:
        # Find the insertion point for the student login
        start_index = bisect.bisect_left(student_dirs, args.student)
        # If the exact student wasn't found, use the next student alphabetically
        if start_index == len(student_dirs) or student_dirs[start_index] != args.student:
            print(f"Student {args.student} not found. Starting with the next student alphabetically.")
        if start_index == len(student_dirs):
            start_index = 0
            print("Wrapping around to the beginning of the list.")
    
    # Reorder the list to start from the selected student
    student_dirs = student_dirs[start_index:] + student_dirs[:start_index]
    
    grader = Project2Grader()
    
    for student_dir in student_dirs:
        submission_path = os.path.join(submissions_dir, student_dir)
        result = grader.grade_submission(submission_path)
        results[student_dir] = result
        
        # Print detailed summary for this submission
        print_submission_summary(student_dir, result)
        
        # If there are no errors, try to open the JavaScript file
        if "error" not in result:
            js_file = find_file_by_extension(submission_path, "js")
            if js_file:
                # Use a constant temp_run directory
                temp_web_dir = './temp_run'
                # Clear the directory if it exists, or create it
                if os.path.exists(temp_web_dir):
                    shutil.rmtree(temp_web_dir)
                os.makedirs(temp_web_dir, exist_ok=True)
                # Copy HTML and CSS from website_template
                shutil.copy2("./website_template/tasklist-modified.html", os.path.join(temp_web_dir, "tasklist-modified.html"))
                shutil.copy2("./website_template/tasklist-modified.css", os.path.join(temp_web_dir, "tasklist-modified.css"))
                # Copy and rename student's JS file
                shutil.copy2(js_file, os.path.join(temp_web_dir, "tasklist-modified.js"))
                # Open the HTML file in the default browser
                webbrowser.open(f"file://{os.path.abspath(os.path.join(temp_web_dir, 'tasklist-modified.html'))}")
        
        print("\nPress Enter to continue to next submission (or 'q' to quit)...")
        if input().lower() == 'q':
            break
    
    # Save results to a JSON file
    with open("grading_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Print final summary
    print("\nFinal Grading Summary:")
    print("=" * 60)
    for student, result in results.items():
        print(f"\nStudent: {student}")
        if "error" in result:
            print(f"Error: {result['error']}")
        print(f"Total Score: {result['total']['points']}/{result['total']['max_points']}")
        print(f"Percentage: {result['total']['percentage']:.2f}%")

if __name__ == "__main__":
    main()
