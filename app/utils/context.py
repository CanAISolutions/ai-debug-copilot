"""
Utilities for extracting contextual code snippets from uploaded files based on
references found in error logs.

The functions here help minimise the amount of code sent to the language model by
only including the relevant parts of files where errors occurred. A simple
regex parser identifies filenames and line numbers in error messages, and then
those lines (plus a configurable number of surrounding lines) are extracted
from the decoded file contents.
"""

import os
import re
from typing import List, Tuple, Dict, Any


def parse_error_log(error_log: str) -> List[Tuple[str, int]]:
    """Parse an error log for file and line number references.

    Supports common patterns such as:
      - File "/path/to/file.py", line 42
      - some/module/file.py:123

    Returns a list of tuples (filename, line_number). The filename returned
    is the basename of the path (e.g. 'file.py') so it can be matched
    against decoded file names provided by the client. Line numbers are
    returned as integers. If no line number is found, the reference is
    omitted.
    """
    references: List[Tuple[str, int]] = []
    if not error_log:
        return references
    # Pattern 1: File "...", line X
    pattern_file_line = re.compile(r'File "([^"]+?)",\s*line\s*(\d+)', re.MULTILINE)
    # Pattern 2: path/to/file.py:X (colon separated)
    pattern_colon = re.compile(r'([\w\.\-/]+\.py):(\d+)', re.MULTILINE)
    for match in pattern_file_line.finditer(error_log):
        file_path, line_str = match.groups()
        filename = os.path.basename(file_path)
        try:
            line_no = int(line_str)
            references.append((filename, line_no))
        except ValueError:
            continue
    for match in pattern_colon.finditer(error_log):
        file_path, line_str = match.groups()
        filename = os.path.basename(file_path)
        try:
            line_no = int(line_str)
            references.append((filename, line_no))
        except ValueError:
            continue
    return references


def extract_context(decoded_files: List[Dict[str, Any]], references: List[Tuple[str, int]], context_lines: int = 30) -> List[Dict[str, Any]]:
    """Extract surrounding code for each (filename, line_number) reference.

    Parameters:
      decoded_files: list of dicts with keys 'filename' and 'content' where
        content is the plain text of the file.
      references: list of tuples (filename, line_number) as returned by
        parse_error_log().
      context_lines: number of lines of context to include before and after
        the target line.

    Returns a list of dictionaries containing:
      - filename: the name of the file
      - start: starting line number of the snippet (1-indexed)
      - end: ending line number of the snippet (1-indexed)
      - snippet: the extracted text snippet

    Only the first match for each reference is returned. If a file cannot be
    found in decoded_files, that reference is skipped.
    """
    snippets: List[Dict[str, Any]] = []
    for ref_filename, line_no in references:
        # Find the first file whose basename matches the reference (case sensitive)
        for file in decoded_files:
            # file['filename'] may contain directories; match basename and full path
            file_basename = os.path.basename(file.get('filename', ''))
            if file_basename == ref_filename or file.get('filename') == ref_filename:
                content = file.get('content', '')
                if not content:
                    break  # no content to extract
                lines = content.splitlines()
                # Calculate 0-based indices
                start_idx = max(0, line_no - context_lines - 1)
                end_idx = min(len(lines), line_no + context_lines)
                snippet_lines = lines[start_idx:end_idx]
                snippet_text = "\n".join(snippet_lines)
                snippets.append({
                    'filename': file['filename'],
                    'start': start_idx + 1,
                    'end': end_idx,
                    'snippet': snippet_text,
                })
                break  # stop searching decoded_files for this reference
    return snippets