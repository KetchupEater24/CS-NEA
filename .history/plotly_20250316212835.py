import matplotlib.pyplot as plt

# Sample data
years = [2009, 2010, 2011, 2012, 2013, 2014, 2015]
org_a = [130, 135, 128, 140, 145, 150, 189]
org_b = [40, 50, 80, 90, 84, 70, 94]

# Use the "seaborn" style for a clean look
plt.style.use("Solarize_Light2")

# Create the figure and axes
fig, ax = plt.subplots(figsize=(8, 5))

# Plot Organization A
ax.plot(
    years,
    org_a,
    marker="o",
    color="#8B1A1A",
    linewidth=2,
    markersize=6,
    label="Organization A"
)

# Plot Organization B
ax.plot(
    years,
    org_b,
    marker="o",
    color="#E67E22",
    linewidth=2,
    markersize=6,
    label="Organization B"
)

# Set title and axis labels
ax.set_title("Comparison of Two Organizations Over Time", fontsize=14, pad=15)
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Value", fontsize=12)

# Customize tick parameters
ax.tick_params(axis='both', which='major', labelsize=10)

# Display legend
ax.legend()

# Adjust layout for neatness
plt.tight_layout()

# Show the plot
plt.show()
