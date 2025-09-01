#!/usr/bin/env python3
"""
Script to detect and remove duplicate content from enhanced_dashboard.py
"""

def remove_duplicates():
    file_path = "enhanced_dashboard.py"
    
    # Read all lines
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Original file has {len(lines)} lines")
    
    # Track line numbers where we have duplicates
    seen_lines = {}
    duplicates = []
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if line_stripped:  # Only check non-empty lines
            if line_stripped in seen_lines:
                duplicates.append((i, seen_lines[line_stripped], line_stripped))
            else:
                seen_lines[line_stripped] = i
    
    print(f"Found {len(duplicates)} duplicate lines")
    
    # Look for patterns of consecutive duplicates
    consecutive_duplicates = []
    current_block_start = None
    current_block_size = 0
    
    for i in range(len(duplicates) - 1):
        curr_dup_line, _, _ = duplicates[i]
        next_dup_line, _, _ = duplicates[i + 1]
        
        if next_dup_line == curr_dup_line + 1:  # Consecutive duplicates
            if current_block_start is None:
                current_block_start = curr_dup_line
                current_block_size = 1
            current_block_size += 1
        else:
            if current_block_start is not None:
                consecutive_duplicates.append((current_block_start, current_block_size))
                current_block_start = None
                current_block_size = 0
    
    # Add the last block if it exists
    if current_block_start is not None:
        consecutive_duplicates.append((current_block_start, current_block_size))
    
    print("Consecutive duplicate blocks:")
    for start, size in consecutive_duplicates:
        print(f"  Lines {start}-{start+size}: {size} lines")
    
    # Show the largest duplicate block
    if consecutive_duplicates:
        largest_block = max(consecutive_duplicates, key=lambda x: x[1])
        start, size = largest_block
        print(f"\nLargest duplicate block: lines {start} to {start+size} ({size} lines)")
        
        # Show what the duplicate content is
        print("Sample from duplicate block:")
        for i in range(min(10, size)):
            line_num = start + i
            if line_num < len(lines):
                print(f"  {line_num}: {lines[line_num].rstrip()}")

if __name__ == "__main__":
    remove_duplicates()
