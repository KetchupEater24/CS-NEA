import matplotlib.pyplot as plt
import customtkinter as ctk
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DFSAnimationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DFS Animation")
        self.geometry("700x600")

        # Define Graph as an adjacency list
        self.graph = {
            0: [1, 2],
            1: [0, 3, 4],
            2: [0, 5, 6],
            3: [1],
            4: [1],
            5: [2],
            6: [2]
        }

        # Node positions (for visualization)
        self.positions = {
            0: (3, 3), 1: (2, 2), 2: (4, 2), 3: (1, 1),
            4: (3, 1), 5: (4, 1), 6: (5, 1)
        }

        # Figure for Matplotlib
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        # Start DFS Button
        self.start_button = ctk.CTkButton(self, text="Start DFS", command=self.start_dfs)
        self.start_button.pack(pady=10)

        # Draw initial graph
        self.draw_graph()

    def draw_graph(self, visited_nodes=set()):
        """ Draws the graph, highlighting visited nodes. """
        self.ax.clear()
        
        # Draw edges
        for node, neighbors in self.graph.items():
            for neighbor in neighbors:
                x_values = [self.positions[node][0], self.positions[neighbor][0]]
                y_values = [self.positions[node][1], self.positions[neighbor][1]]
                self.ax.plot(x_values, y_values, 'black')
        
        # Draw nodes
        for node, (x, y) in self.positions.items():
            color = 'red' if node in visited_nodes else 'skyblue'
            self.ax.scatter(x, y, color=color, s=300)
            self.ax.text(x, y, str(node), fontsize=12, ha='center', va='center', color='white')

        self.ax.set_xlim(0, 6)
        self.ax.set_ylim(0, 4)
        self.ax.axis('off')
        self.canvas.draw()

    def dfs(self, node, visited):
        """ Depth-First Search with animation delay. """
        if node in visited:
            return
        
        visited.add(node)
        self.draw_graph(visited)
        self.update()
        time.sleep(0.5)  # Animation delay
        
        for neighbor in self.graph[node]:
            self.dfs(neighbor, visited)

    def start_dfs(self):
        """ Starts DFS animation from node 0. """
        visited = set()
        self.dfs(0, visited)

# Run App
app = DFSAnimationApp()
app.mainloop()
