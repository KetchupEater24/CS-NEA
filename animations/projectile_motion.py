import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import io
from PIL import Image

class ProjectileMotionHandler:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.g = 9.81  # gravity
        self.v0 = 20.0  # initial velocity
        self.theta = 45  # launch angle
        self.current_frame = 0
        self.setup_trajectory()
        
    def setup_trajectory(self):
        """Calculate the full trajectory"""
        theta_rad = np.radians(self.theta)
        self.t_flight = (2 * self.v0 * np.sin(theta_rad)) / self.g
        self.t = np.linspace(0, self.t_flight, 50)
        
        # Calculate full trajectory
        self.x = self.v0 * np.cos(theta_rad) * self.t
        self.y = self.v0 * np.sin(theta_rad) * self.t - (0.5 * self.g * self.t ** 2)
        
    def create_frame(self):
        """Creates a single frame of the animation"""
        if self.current_frame < len(self.t):
            self.ax.clear()
            
            # Set up plot
            self.ax.set_xlim(0, max(self.x) + 2)
            self.ax.set_ylim(0, max(self.y) + 2)
            self.ax.set_xlabel("Distance (m)")
            self.ax.set_ylabel("Height (m)")
            self.ax.grid(True)
            
            # Plot trajectory up to current point
            self.ax.plot(self.x[:self.current_frame], self.y[:self.current_frame], 'b-', alpha=0.5)
            self.ax.plot(self.x[self.current_frame], self.y[self.current_frame], 'ro', markersize=10)
            
            # Add info text
            info_text = f"Time: {self.t[self.current_frame]:.2f}s\n"
            info_text += f"Height: {self.y[self.current_frame]:.2f}m\n"
            info_text += f"Distance: {self.x[self.current_frame]:.2f}m"
            
            self.ax.text(0.02, 0.98, info_text,
                        transform=self.ax.transAxes,
                        verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            # Convert to image
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            
            self.current_frame += 1
            return Image.open(buf)
        return None
    
    def reset_animation(self):
        """Resets the animation state"""
        self.current_frame = 0 