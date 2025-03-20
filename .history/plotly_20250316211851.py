import plotly.express as px
import pandas as pd

# Sample data (similar structure to the image)
data = {
    "Year": [2009, 2010, 2011, 2012, 2013, 2014, 2015] * 2,
    "Organization": ["Organization A"] * 7 + ["Organization B"] * 7,
    "Value": [130, 135, 128, 140, 145, 150, 189, 40, 50, 80, 90, 84, 70, 94]
}

df = pd.DataFrame(data)

# Create the line plot
fig = px.line(
    df,
    x="Year",
    y="Value",
    color="Organization",
    markers=True,                 # Show data points
    template="simple_white",      # Clean, minimalist background
    color_discrete_map={
        "Organization A": "#8B1A1A",  # Deep red
        "Organization B": "#E67E22"   # Vibrant orange
    }
)

# Update marker size and line widths
fig.update_traces(marker=dict(size=8), line=dict(width=2))

# Customize layout (titles, axes, legend, etc.)
fig.update_layout(
    title="Comparison of Two Organizations Over Time",
    xaxis_title="Year",
    yaxis_title="Value",
    legend_title_text="",
    font=dict(family="Arial", size=14),
    title_x=0.5,  # Center the title
    margin=dict(l=40, r=40, t=60, b=40)
)

fig.show()
