import matplotlib.pyplot as plt
import customtkinter as ctk
import time
import random
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class MergeSortAnimationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Merge Sort Animation")
        self.geometry("700x600")

        # Create UI Controls
        self.start_button = ctk.CTkButton(self, text="Start Merge Sort", command=self.start_sort)
        self.start_button.pack(pady=10)

        # Generate Random Array
        self.array = [random.randint(10, 100) for _ in range(10)]

        # Set up Figure
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        self.draw_array()

    def draw_array(self, highlight=[]):
        """ Draws the array as bars, highlighting specific indices. """
        self.ax.clear()
        colors = ['red' if i in highlight else 'skyblue' for i in range(len(self.array))]
        self.ax.bar(range(len(self.array)), self.array, color=colors)
        self.ax.set_ylim(0, max(self.array) + 10)
        self.canvas.draw()

    def merge_sort(self, array, left, right):
        """ Recursive merge sort with animation. """
        if left < right:
            mid = (left + right) // 2
            self.merge_sort(array, left, mid)
            self.merge_sort(array, mid + 1, right)
            self.merge(array, left, mid, right)

    def merge(self, array, left, mid, right):
        """ Merges two sorted subarrays and updates visualization. """
        left_part = array[left:mid + 1]
        right_part = array[mid + 1:right + 1]

        i = j = 0
        k = left

        while i < len(left_part) and j < len(right_part):
            if left_part[i] < right_part[j]:
                array[k] = left_part[i]
                i += 1
            else:
                array[k] = right_part[j]
                j += 1
            k += 1
            self.draw_array(highlight=[k])
            self.update()
            time.sleep(0.5)

        while i < len(left_part):
            array[k] = left_part[i]
            i += 1
            k += 1
            self.draw_array(highlight=[k])
            self.update()
            time.sleep(0.5)

        while j < len(right_part):
            array[k] = right_part[j]
            j += 1
            k += 1
            self.draw_array(highlight=[k])
            self.update()
            time.sleep(0.5)

    def start_sort(self):
        """ Starts merge sort animation. """
        self.merge_sort(self.array, 0, len(self.array) - 1)
        self.draw_array()

# Run App
app = MergeSortAnimationApp()
app.mainloop()
