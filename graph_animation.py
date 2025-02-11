import customtkinter as ctk
import tkinter as tk

class GraphVisualizer(ctk.CTkFrame):
    def __init__(self, master, algorithm="bfs"):

        super().__init__(master)
        self.algorithm = algorithm
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill="both", expand=True)
        
        self.nodes = []
        self.edges = []
        self.visited = set()
        self.queue = []
        self.current_step = 0
        
        self.setup_graph()
        self.start_animation()
    
    def setup_graph(self):
        # Create sample graph structure
        positions = [
            (100, 100), (200, 100), (300, 100),
            (150, 200), (250, 200),
            (200, 300)
        ]
        
        # Add nodes
        for x, y in positions:
            self.nodes.append((x, y))
            
        # Add edges
        self.edges = [(0,1), (1,2), (0,3), (1,4), (3,5), (4,5)] 