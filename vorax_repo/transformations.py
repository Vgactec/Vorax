import numpy as np

def color_mapping(grid):
    """Applique une transformation de couleurs."""
    unique_values = np.unique(grid)
    mapping = {v: i for i, v in enumerate(unique_values)}
    return np.vectorize(mapping.get)(grid)

def pattern_extraction(grid):
    """Extrait les motifs récurrents."""
    h, w = grid.shape
    patterns = {}
    for i in range(h-1):
        for j in range(w-1):
            pattern = grid[i:i+2, j:j+2].tobytes()
            patterns[pattern] = patterns.get(pattern, 0) + 1
    return patterns

def transform_grid(grid, transform_type="identity"):
    """Transformation robuste des grilles avec validation."""
    if not isinstance(grid, np.ndarray):
        grid = np.array(grid)

    if transform_type == "rotate":
        return np.rot90(grid)
    elif transform_type == "flip":
        return np.fliplr(grid)
    elif transform_type == "invert":
        return 1 - grid
    else:
        return grid.copy()