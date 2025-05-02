import os
import webbrowser
from bs4 import BeautifulSoup
import cssutils
import re
import requests
import sys

# Path to the directory containing student folders
directory = "./processed_submissions"

def validate_html_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    headers = {
        'Content-Type': 'text/html; charset=utf-8'
    }

    params = {
        'out': 'json'  # Use JSON output for easy parsing
    }

    response = requests.post(
        'https://validator.nu?out=json',
        headers=headers,
        data=html_content.encode('utf-8'),
        allow_redirects=False
    )

    print(response.status_code)
    if response.status_code != 200:
        print(f"Validator error: {response.status_code}")
        return

    print(response.text)
    
    results = response.json()

    messages = results.get('messages', [])
    if not messages:
        feedback = "✅ No issues found. HTML is valid."
    else:
        feedback = "⚠️ Issues found:"
        for msg in messages:
            line = msg.get('lastLine', '?')
            msg_text = msg.get('message', '')
            msg_type = msg.get('type', 'info')
            feedback += f"\n[{msg_type.upper()}] Line {line}: {msg_text}"
    return feedback

# Main script
final_scores = {}

start_name = ""
if len(sys.argv) > 1:
    start_name = sys.argv[1]
    
for folder_name in sorted(os.listdir(directory)):
    if start_name:
        if folder_name < start_name:
            continue
    folder_path = os.path.join(directory, folder_name)

    if not os.path.isdir(folder_path):
        continue

    print(f"\nAnalyzing folder: {folder_name}")

    # Locate HTML and CSS files
    html_file = None
    css_file = None

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".html"):
            html_file = os.path.join(folder_path, file_name)
        elif file_name.endswith(".css"):
            css_file = os.path.join(folder_path, file_name)

    if not html_file:
        print("No HTML file found.")
        continue

    # Analyze HTML file
    print(os.path.abspath(html_file))
    html_feedback = validate_html_file(os.path.abspath(html_file))
    print("HTML Feedback:")
    print(html_feedback)

    # Open the HTML file in the browser
    absolute_html_path = os.path.abspath(html_file)
    webbrowser.open(f"file://{absolute_html_path}")
    
    # final feedback
    print(f'---------------{folder_name}-----------------')
    # for category in categories: 
    #     print(f'{category}: {grade_by_cat[category]} / 4')
    #     if category in comment_by_cat and comment_by_cat[category]:
    #         print(f'Comment: {comment_by_cat[category]}')
    # print(f"Final grade: {final_grade} / 28")    
    # Wait for user input
    print(f'---------------------------------------------')
    input("\nPress Enter to analyze the next folder...")

print("Analysis complete.")
