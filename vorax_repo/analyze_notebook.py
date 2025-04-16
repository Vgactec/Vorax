import json
import sys
import re

def analyze_notebook(notebook_path):
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)
    
    writefile_cells = []
    for i, cell in enumerate(notebook['cells']):
        if 'source' in cell:
            source_text = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            if '%%writefile' in source_text:
                writefile_cells.append((i, source_text))
                # Extract the filename
                match = re.search(r'%%writefile\s+(\S+)', source_text)
                filename = match.group(1) if match else "unknown"
                print(f"Cell {i} writes to file: {filename}")
                print(source_text[:200])
                print('-' * 50)
    
    return writefile_cells

def create_notebook_fix(notebook_path, output_path):
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)
    
    # List to store new cells that will replace writefile cells
    cells_to_modify = []
    
    for i, cell in enumerate(notebook['cells']):
        if 'source' in cell:
            source_text = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            if '%%writefile' in source_text:
                # Extract the filename and code
                match = re.search(r'%%writefile\s+(\S+)([\s\S]*)', source_text)
                if match:
                    filename = match.group(1)
                    code = match.group(2).strip()
                    
                    # Create a modified version that creates directories and writes the file inline
                    new_code = f'''
# Code from {filename}
import os

# Create directory if it doesn't exist
os.makedirs(os.path.dirname("{filename}"), exist_ok=True)

# Write the file
with open("{filename}", "w") as f:
    f.write("""{code}""")

# Import the module directly
{code}
'''
                    cells_to_modify.append((i, new_code))
    
    # Apply modifications
    for i, new_code in cells_to_modify:
        notebook['cells'][i]['source'] = new_code
    
    # Save the modified notebook
    with open(output_path, 'w') as f:
        json.dump(notebook, f)
    
    print(f"Modified notebook saved to {output_path}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        notebook_path = sys.argv[1]
        cells = analyze_notebook(notebook_path)
        
        if len(sys.argv) > 2:
            output_path = sys.argv[2]
            create_notebook_fix(notebook_path, output_path)
    else:
        print("Usage: python analyze_notebook.py <notebook_path> [output_path]")