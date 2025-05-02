# CS111 Submission Extractor

This script helps process and organize student submissions by extracting files from various submission formats into a structured directory.

## Usage

```bash
python extract_submissions.py <submissions_dir> <target_dir>
```

### Arguments:
- `submissions_dir`: Directory containing the original student submissions
- `target_dir`: Directory where processed submissions will be stored

### Example:
```bash
python extract_submissions.py ./raw_submissions ./processed_submissions
```

## What it does

1. Takes submissions from the source directory
2. For each submission:
   - If it's a ZIP file, extracts its contents
   - If it's a regular file, copies it directly
   - Organizes files by student login (extracted from filename)
3. Handles special cases like:
   - LATE submissions
   - __MACOSX directories
   - Nested directory structures

## Output

The script will create a directory structure in the target directory where:
- Each student gets their own folder (named by their login)
- Files are extracted and organized within student folders
- Temporary processing files are automatically cleaned up

## Requirements

- Python 3.x
- No additional packages required (uses standard library only) 