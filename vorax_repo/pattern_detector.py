
class PatternDetector:
    def __init__(self):
        self.known_patterns = {}
        
    def analyze_grid(self, grid):
        """Analyse une grille pour détecter des motifs."""
        h, w = grid.shape
        patterns = {}
        
        # Analyse horizontale et verticale
        for i in range(h):
            for j in range(w):
                self._analyze_surrounding(grid, i, j, patterns)
                
        return patterns
        
    def _analyze_surrounding(self, grid, i, j, patterns):
        """Analyse l'environnement d'une cellule."""
        h, w = grid.shape
        if i > 0 and j > 0 and i < h-1 and j < w-1:
            pattern = grid[i-1:i+2, j-1:j+2]
            pattern_key = pattern.tobytes()
            patterns[pattern_key] = patterns.get(pattern_key, 0) + 1
