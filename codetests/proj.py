import numpy as np
import matplotlib.pyplot as plt
import customtkinter as ctk
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image
import matplotlib.image as mpimg

# Constants
g = 9.81  # Gravity (m/s^2)

class ProjectileMotionApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Projectile Motion - Man Throwing Ball")
        self.geometry("800x600")

        # Create UI Controls
        self.speed_label = ctk.CTkLabel(self, text="Initial Speed (m/s):")
        self.speed_label.pack()
        self.speed_entry = ctk.CTkEntry(self)
        self.speed_entry.insert(0, "20")
        self.speed_entry.pack()

        self.angle_label = ctk.CTkLabel(self, text="Launch Angle (degrees):")
        self.angle_label.pack()
        self.angle_entry = ctk.CTkEntry(self)
        self.angle_entry.insert(0, "45")
        self.angle_entry.pack()

        self.start_button = ctk.CTkButton(self, text="Start Simulation", command=self.start_animation)
        self.start_button.pack(pady=10)

        # Set up Figure
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)


    def projectile_trajectory(self, v0, theta):
        """ Computes the projectile motion path. """
        theta_rad = np.radians(theta)
        t_flight = (2 * v0 * np.sin(theta_rad)) / g  # Total flight time
        t = np.linspace(0, t_flight, num=100)  # Time intervals

        x = v0 * np.cos(theta_rad) * t  # X position
        y = v0 * np.sin(theta_rad) * t - (0.5 * g * t ** 2)  # Y position

        return x, y

    def update(self, frame):
        """ Updates the projectile position for animation. """
        self.projectile.set_data(self.x[:frame], self.y[:frame])
        return self.projectile,

    def start_animation(self):
        """ Starts the animation. """
        try:
            v0 = float(self.speed_entry.get())
            theta = float(self.angle_entry.get())
        except ValueError:
            return

        self.x, self.y = self.projectile_trajectory(v0, theta)

        self.ax.clear()
        self.ax.set_xlim(0, max(self.x) + 2)
        self.ax.set_ylim(0, max(self.y) + 2)
        self.ax.set_xlabel("Distance (m)")
        self.ax.set_ylabel("Height (m)")
        self.ax.set_title("Projectile Motion - Man Throwing Ball")
        self.ax.grid(True)

    

        # Initialize Projectile
        self.projectile, = self.ax.plot([], [], 'ro', markersize=6)

        # Animate
        self.ani = FuncAnimation(self.fig, self.update, frames=len(self.x), interval=30, blit=True)
        self.canvas.draw()

# Run App
app = ProjectileMotionApp()
app.mainloop()
