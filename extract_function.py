#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('SConstruct', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the generate_link_command function
start_line = -1
for i, line in enumerate(lines):
    if 'def generate_link_command' in line:
        start_line = i
        break

if start_line != -1:
    # Find the end of the function by looking for the next function definition or end of file
    end_line = len(lines)
    for i in range(start_line + 1, len(lines)):
        # Check if this line starts a new function or is at the same indentation level as the function
        if lines[i].startswith('def ') or (lines[i].strip() and not lines[i].startswith(' ') and not lines[i].startswith('\t') and i > start_line + 10):
            end_line = i
            break
    
    # Print the complete function with line numbers
    print("=== START OF FUNCTION ===")
    for i in range(start_line, min(end_line, len(lines))):
        # Only print lines that are part of the function
        if i == start_line or lines[i].startswith(' ') or lines[i].startswith('\t') or lines[i].strip() == '':
            print(f"{i+1:3d}: {lines[i]}", end='')
        else:
            # We've reached the end of the function
            break
    print("=== END OF FUNCTION ===")
else:
    print("Function not found")