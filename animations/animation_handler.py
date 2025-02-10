import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import io
from PIL import Image

class AnimationHandler:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.G = nx.Graph()
        self.pos = None
        self.visited = set()
        self.current_node = 0
        self.algorithm = None  # Initialize algorithm attribute
        self.queue = []  # for BFS
        self.stack = []  # for DFS

    def setup_graph(self):
        # Create a more interesting graph for visualization
        self.G = nx.Graph()
        edges = [(0,1), (0,2), (1,3), (1,4), (2,5), (2,6), (3,7), (4,7), (5,8), (6,8)]
        self.G.add_edges_from(edges)
        self.pos = nx.spring_layout(self.G)
        self.visited = set()
        self.current_node = 0
        
        if self.algorithm == "bfs":
            self.queue = [0]
        else:
            self.stack = [0]

    def animate_bfs(self, frame):
        plt.clf()
        if frame == 0:
            self.visited = set()
            self.queue = [0]
        
        if self.queue:
            node = self.queue.pop(0)
            if node not in self.visited:
                self.visited.add(node)
                self.queue.extend([n for n in self.G[node] if n not in self.visited])
        
        # Draw the graph
        nx.draw_networkx_edges(self.G, self.pos)
        nx.draw_networkx_nodes(self.G, self.pos, node_color='lightblue')
        nx.draw_networkx_nodes(self.G, self.pos, nodelist=self.visited, node_color='green')
        if self.queue:
            nx.draw_networkx_nodes(self.G, self.pos, nodelist=self.queue, node_color='yellow')

    def animate_dfs(self, frame):
        plt.clf()
        if frame == 0:
            self.visited = set()
            self.stack = [0]
        
        if self.stack:
            node = self.stack.pop()
            if node not in self.visited:
                self.visited.add(node)
                self.stack.extend([n for n in self.G[node] if n not in self.visited])
        
        # Draw the graph
        nx.draw_networkx_edges(self.G, self.pos)
        nx.draw_networkx_nodes(self.G, self.pos, node_color='lightblue')
        nx.draw_networkx_nodes(self.G, self.pos, nodelist=self.visited, node_color='green')
        if self.stack:
            nx.draw_networkx_nodes(self.G, self.pos, nodelist=self.stack, node_color='yellow')

    def start_animation(self, algorithm):
        self.algorithm = algorithm
        self.running = True
        self.visited.clear()
        
        if algorithm == "bfs":
            self.queue = [0]
        else:  # DFS
            self.stack = [0]
            
    def stop_animation(self):
        self.running = False
        
    def step_algorithm(self, algorithm):
        if algorithm == "bfs":
            if not self.queue:
                return None
            current = self.queue.pop(0)
        else:  # DFS
            if not self.stack:
                return None
            current = self.stack.pop()
            
        self.visited.add(current)
        self.current_node = current
        
        # Add unvisited neighbors
        for neighbor in sorted(self.G[current]):
            if neighbor not in self.visited:
                if algorithm == "bfs" and neighbor not in self.queue:
                    self.queue.append(neighbor)
                elif algorithm == "dfs" and neighbor not in self.stack:
                    self.stack.append(neighbor)
                    
        return self.create_frame()
        
    def create_frame(self):
        if self.algorithm == "bfs":
            if self.queue:
                self.step_algorithm("bfs")
        else:
            if self.stack:
                self.step_algorithm("dfs")
                
        return self.draw_current_state()

    def draw_current_state(self):
        plt.clf()
        
        # Draw nodes with different colors based on state
        node_colors = ['#4F46E5' if node == self.current_node else 
                      '#22C55E' if node in self.visited else 
                      '#D1D5DB' for node in self.G.nodes()]
        
        # Draw edges with different colors for visited paths
        edge_colors = ['#22C55E' if u in self.visited and v in self.visited else '#9CA3AF' 
                      for u, v in self.G.edges()]
        
        nx.draw(self.G, self.pos, 
                node_color=node_colors,
                edge_color=edge_colors,
                node_size=1000,
                font_size=16,
                font_weight='bold',
                font_color='white',
                width=2,
                with_labels=True)
        
        # Convert to image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', transparent=True)
        buf.seek(0)
        return Image.open(buf)

    def generate_animations(self):
        self.setup_graph()
        # Generate BFS animation
        bfs_anim = FuncAnimation(self.fig, self.animate_bfs, frames=10, 
                               interval=500, repeat=False)
        bfs_anim.save('animations/bfs_animation.gif', writer='pillow')
        
        # Generate DFS animation
        dfs_anim = FuncAnimation(self.fig, self.animate_dfs, frames=10, 
                               interval=500, repeat=False)
        dfs_anim.save('animations/dfs_animation.gif', writer='pillow')  