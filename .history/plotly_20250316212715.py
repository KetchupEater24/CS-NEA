import pygal
from pygal.style import CleanStyle

# Create a line chart with a clean style and some customization
line_chart = pygal.Line(
    style=CleanStyle,
    x_label_rotation=20,
    show_minor_x_labels=False,
    width=800,
    height=400
)

line_chart.title = 'Monthly Data Overview'
line_chart.x_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Add data series
line_chart.add('Series 1', [10, 20, 15, 25, 30, 35, 40, 38, 33, 28, 22, 18])
line_chart.add('Series 2', [8, 15, 12, 20, 27, 32, 36, 34, 30, 26, 20, 16])

# Render the chart to an SVG file
line_chart.render_to_file('line_chart.svg')
