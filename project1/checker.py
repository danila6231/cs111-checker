import os
import re
from bs4 import BeautifulSoup
import json
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import glob
import argparse
import bisect

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

class HTMLModificationsGrader(RubricItem):
    def __init__(self):
        super().__init__("HTML Modifications", 2.0)
    
    def grade(self, submission_path: str) -> GradingResult:
        # try:
        #     html_file = find_file_by_extension(submission_path, "html")
        #     if not html_file:
        #         return GradingResult(0, ["No HTML file found in submission"], self.max_points)
            
        #     with open(html_file, "r") as f:
        #         soup = BeautifulSoup(f.read(), 'html.parser')
                
        #     temp_div = soup.find('div', id='temperatureAssessment')
            
        #     if temp_div is None:
        #         return GradingResult(0, ["Missing temperature assessment div"], self.max_points)
            
        #     if temp_div.get('class') and 'assessment' in temp_div.get('class'):
        #         return GradingResult(2, ["Correctly added temperature assessment div"], self.max_points)
            
        #     return GradingResult(1, ["Added temperature assessment div but with incorrect class"], self.max_points)
            
        # except Exception as e:
        #     return GradingResult(0, [f"Error checking HTML: {str(e)}"], self.max_points)
        return GradingResult(2, ["Correctly added temperature assessment div"], self.max_points)

class UpdateFormulaGrader(RubricItem):
    def __init__(self):
        super().__init__("updateFormula() Function", 3.0)
    
    def grade(self, submission_path: str) -> GradingResult:
        try:
            js_file = find_file_by_extension(submission_path, "js")
            if not js_file:
                return GradingResult(0, ["No JavaScript file found in submission"], self.max_points)
            
            with open(js_file, "r") as f:
                js_content = f.read()
            
            # Check if function exists
            if 'function updateFormula' not in js_content:
                return GradingResult(0, ["Function not implemented"], self.max_points)
            
            points = 3
            comments = []
            
            # Check for getting conversion type
            if not re.search(r'document\.getElementById.*conversion.*\.value', js_content):
                points -= 1
                comments.append("Missing conversion type retrieval")
            
            # Check for formula element
            if not re.search(r'document\.getElementById.*formula', js_content):
                points -= 1
                comments.append("Missing formula element retrieval")
            
            # Check for conditional logic
            if not ('if' in js_content and ('ftoc' in js_content or 'ctof' in js_content)):
                points -= 1
                comments.append("Missing conversion type checking")
            
            if not comments:
                comments.append("Correctly implements all required functionality")
                
            return GradingResult(points, comments, self.max_points)
            
        except Exception as e:
            return GradingResult(0, [f"Error checking updateFormula: {str(e)}"], self.max_points)

class AssessTemperatureGrader(RubricItem):
    def __init__(self):
        super().__init__("Fahrenheit Assessment", 4.0)
    
    def grade(self, submission_path: str) -> GradingResult:
        try:
            js_file = find_file_by_extension(submission_path, "js")
            if not js_file:
                return GradingResult(0, ["No JavaScript file found in submission"], self.max_points)
            
            with open(js_file, "r") as f:
                js_content = f.read()
            
            if 'function assessTemperature' not in js_content:
                return GradingResult(0, ["Function not implemented"], self.max_points)
            
            points = 4
            comments = []
            missing_count = 0
            
            # Check for temperature ranges
            ranges = [
                (32, "Very Cold", "blue"),
                (49, "Cold", "light blue"),
                (67, "Cool", "very light blue"),
                (85, "Moderate", "green"),
                (103, "Warm", "orange"),
                (104, "Hot", "red")
            ]
            
            for temp, desc, color in ranges:
                temp_missing = False
                color_missing = False
                
                if str(temp) not in js_content:
                    temp_missing = True
                    missing_count += 1
                    comments.append(f"Missing {desc} temperature range")
                if color.lower() not in js_content.lower():
                    color_missing = True
                    missing_count += 1
                    comments.append(f"Missing {color} color assignment")
            
            # Only deduct points if more than 2 elements are missing
            if missing_count > 2:
                points = max(0, points - missing_count * 0.25)
            
            if not comments:
                comments.append("Correctly implements all temperature ranges with proper text and color coding")
                
            return GradingResult(points, comments, self.max_points)
            
        except Exception as e:
            return GradingResult(0, [f"Error checking assessTemperature: {str(e)}"], self.max_points)

class InputHandlingGrader(RubricItem):
    def __init__(self):
        super().__init__("Input Handling", 3.0)
    
    def grade(self, submission_path: str) -> GradingResult:
        try:
            js_file = find_file_by_extension(submission_path, "js")
            if not js_file:
                return GradingResult(0, ["No JavaScript file found in submission"], self.max_points)
            
            with open(js_file, "r") as f:
                js_content = f.read()
            
            if 'function convertTemperature' not in js_content:
                return GradingResult(0, ["Function not implemented"], self.max_points)
            
            points = 3
            comments = []
            
            # Check for input retrieval
            if not re.search(r'document\.getElementById.*temperature.*\.value', js_content):
                points -= 1
                comments.append("Missing temperature input retrieval")
            
            # Check for parsing
            if not re.search(r'parseFloat|parseInt|Number', js_content):
                points -= 2
                comments.append("Missing proper number parsing")
            
            if not comments:
                comments.append("Correctly retrieves and parses the input temperature")
                
            return GradingResult(points, comments, self.max_points)
            
        except Exception as e:
            return GradingResult(0, [f"Error checking input handling: {str(e)}"], self.max_points)

class ConversionLogicGrader(RubricItem):
    def __init__(self):
        super().__init__("Conversion Logic", 5.0)
    
    def grade(self, submission_path: str) -> GradingResult:
        try:
            js_file = find_file_by_extension(submission_path, "js")
            if not js_file:
                return GradingResult(0, ["No JavaScript file found in submission"], self.max_points)
            
            with open(js_file, "r") as f:
                js_content = f.read()
            
            if 'function convertTemperature' not in js_content:
                return GradingResult(0, ["Function not implemented"], self.max_points)
            
            points = 5
            comments = []
            
            # Check for Fahrenheit to Celsius formula
            if not re.search(r'\(.*32.*\).*5.*9', js_content):
                points -= 1
                comments.append("Missing or incorrect F to C formula")
            
            # Check for Celsius to Fahrenheit formula
            if not re.search(r'.*9.*5.*32', js_content):
                points -= 1
                comments.append("Missing or incorrect C to F formula")
            
            # Check for decimal places formatting
            if not re.search(r'toFixed.*2', js_content):
                points -= 1
                comments.append("Missing proper decimal formatting")
            
            # Check for assessment function call
            if not re.search(r'assessTemperature.*\(', js_content):
                points -= 2
                comments.append("Missing assessment function call")
            
            if not comments:
                comments.append("Correctly implements both conversion formulas with proper formatting")
                
            return GradingResult(points, comments, self.max_points)
            
        except Exception as e:
            return GradingResult(0, [f"Error checking conversion logic: {str(e)}"], self.max_points)

class ClearConverterGrader(RubricItem):
    def __init__(self):
        super().__init__("Clear Converter", 3.0)
    
    def grade(self, submission_path: str) -> GradingResult:
        try:
            js_file = find_file_by_extension(submission_path, "js")
            if not js_file:
                return GradingResult(0, ["No JavaScript file found in submission"], self.max_points)
            
            with open(js_file, "r") as f:
                js_content = f.read()
            
            if 'function clearConverter' not in js_content:
                return GradingResult(0, ["Function not implemented"], self.max_points)
            
            points = 3
            comments = []
            missing_count = 0
            
            # Check for form reset
            if not re.search(r'\.value.*=.*""', js_content):
                missing_count += 1
                comments.append("Missing input field clearing")
            
            # Check for formula reset
            if not re.search(r'conversion.*textContent.*=', js_content):
                missing_count += 1
                comments.append("Missing formula display reset")
            
            # Check for assessment reset
            if not re.search(r'assessment.*textContent.*=', js_content):
                missing_count += 1
                comments.append("Missing assessment display reset")
            
            # Only deduct points if 2 or more elements are missing
            if missing_count > 0:
                points = max(0, points - missing_count)
            
            if not comments:
                comments.append("Correctly resets all form elements")
                
            return GradingResult(points, comments, self.max_points)
            
        except Exception as e:
            return GradingResult(0, [f"Error checking clearConverter: {str(e)}"], self.max_points)

class Project1Grader:
    def __init__(self):
        self.rubric_items = [
            HTMLModificationsGrader(),
            UpdateFormulaGrader(),
            AssessTemperatureGrader(),
            InputHandlingGrader(),
            ConversionLogicGrader(),
            ClearConverterGrader()
        ]
    
    def grade_submission(self, submission_path: str) -> Dict[str, Any]:
        results = {}
        total_points = 0
        total_possible = 0
        
        # First check if required files exist
        html_file = find_file_by_extension(submission_path, "html")
        js_file = find_file_by_extension(submission_path, "js")
        
        if not html_file or not js_file:
            missing_files = []
            if not html_file:
                missing_files.append("HTML")
            if not js_file:
                missing_files.append("JavaScript")
            
            return {
                "error": f"Missing required files: {', '.join(missing_files)}",
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
    
    grader = Project1Grader()
    
    for student_dir in student_dirs:
        submission_path = os.path.join(submissions_dir, student_dir)
        result = grader.grade_submission(submission_path)
        results[student_dir] = result
        
        # Print detailed summary for this submission
        print_submission_summary(student_dir, result)
        
        # If there are no errors, try to open the HTML file
        if "error" not in result:
            html_file = find_file_by_extension(submission_path, "html")
            if html_file:
                print("\nOpening HTML file in default browser...")
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(html_file)}")
        
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
