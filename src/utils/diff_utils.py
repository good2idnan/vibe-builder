"""
VibeBuilder V2 - Diff Utilities
For showing visual differences between code versions
"""

import difflib
from typing import List, Dict


def generate_diff(old_code: str, new_code: str) -> Dict:
    """
    Generate a visual diff between two code versions
    
    Returns:
        Dict with 'html_diff', 'added_lines', 'removed_lines', 'summary'
    """
    old_lines = old_code.splitlines(keepends=True)
    new_lines = new_code.splitlines(keepends=True)
    
    # Create unified diff
    diff = list(difflib.unified_diff(
        old_lines, 
        new_lines,
        fromfile='Previous Version',
        tofile='New Version',
        lineterm=''
    ))
    
    # Count changes
    added = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
    removed = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
    
    # Generate HTML diff
    html_diff = generate_html_diff(old_lines, new_lines)
    
    return {
        "unified_diff": ''.join(diff),
        "html_diff": html_diff,
        "added_lines": added,
        "removed_lines": removed,
        "summary": f"+{added} -{removed} lines"
    }


def generate_html_diff(old_lines: List[str], new_lines: List[str]) -> str:
    """
    Generate colored HTML diff for display
    """
    differ = difflib.HtmlDiff()
    
    try:
        html = differ.make_table(
            old_lines, 
            new_lines,
            fromdesc='Before',
            todesc='After',
            context=True,
            numlines=3
        )
        return html
    except:
        return "<p>Diff generation failed</p>"


def generate_side_by_side_diff(old_code: str, new_code: str) -> List[Dict]:
    """
    Generate side-by-side diff data
    
    Returns list of dicts with 'left', 'right', 'type'
    """
    old_lines = old_code.splitlines()
    new_lines = new_code.splitlines()
    
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
    result = []
    
    for op, old_start, old_end, new_start, new_end in matcher.get_opcodes():
        if op == 'equal':
            for i, j in zip(range(old_start, old_end), range(new_start, new_end)):
                result.append({
                    'left': old_lines[i],
                    'right': new_lines[j],
                    'type': 'equal'
                })
        elif op == 'replace':
            for i in range(old_start, old_end):
                left = old_lines[i] if i < len(old_lines) else ''
                right = new_lines[new_start + (i - old_start)] if (new_start + (i - old_start)) < new_end else ''
                result.append({
                    'left': left,
                    'right': right,
                    'type': 'change'
                })
        elif op == 'insert':
            for j in range(new_start, new_end):
                result.append({
                    'left': '',
                    'right': new_lines[j],
                    'type': 'add'
                })
        elif op == 'delete':
            for i in range(old_start, old_end):
                result.append({
                    'left': old_lines[i],
                    'right': '',
                    'type': 'remove'
                })
    
    return result


def summarize_changes(old_code: str, new_code: str) -> str:
    """
    Generate a human-readable summary of changes
    """
    diff = generate_diff(old_code, new_code)
    
    added = diff['added_lines']
    removed = diff['removed_lines']
    
    if added == 0 and removed == 0:
        return "No changes"
    elif added > 0 and removed == 0:
        return f"Added {added} lines"
    elif removed > 0 and added == 0:
        return f"Removed {removed} lines"
    else:
        return f"Modified: +{added} / -{removed} lines"
