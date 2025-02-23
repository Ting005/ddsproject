import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from adjustText import adjust_text

# JSON data
data_json = '''{
  "Fraud": 108,
  "Corporate Scandal": 83,
  "Money Laundering": 75,
  "Regulatory Violation": 46,
  "Bribery & Corruption": 22,
  "Government Scandal": 17,
  "Terrorist Financing": 9,
  "Ponzi & Pyramid Schemes": 9,
  "Insider Trading": 8,
  "Tax Evasion": 8,
  "Market Manipulation": 7,
  "Sanctions Violations": 7,
  "Securities Fraud": 3
}'''

# Load JSON data
data = json.loads(data_json)
labels = np.array(list(data.keys()))
values = np.array(list(data.values()))

# Convert values to bubble sizes (scaled)
bubble_sizes = np.sqrt(values) * 300  # Scaling factor

# Function to calculate overlapping penalty
def overlap_penalty(positions, radii):
    n = len(radii)
    penalty = 0
    for i in range(n):
        for j in range(i + 1, n):
            dist = np.linalg.norm(positions[2*i:2*i+2] - positions[2*j:2*j+2])
            min_dist = radii[i] + radii[j]
            if dist < min_dist:
                penalty += (min_dist - dist) ** 2  # Penalize overlaps
    return penalty

# Initial random positions
num_bubbles = len(labels)
x_init = np.random.rand(num_bubbles) * 20 - 10  # Spread between -10 to 10
y_init = np.random.rand(num_bubbles) * 20 - 10
positions_init = np.column_stack((x_init, y_init)).flatten()

# Optimize positions to minimize overlap
res = minimize(overlap_penalty, positions_init, args=(bubble_sizes / 2,), method='SLSQP')
optimized_positions = res.x.reshape(-1, 2)

# Extract optimized x, y positions
x_positions = optimized_positions[:, 0]
y_positions = optimized_positions[:, 1]

# Create plot
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(-12, 12)
ax.set_ylim(-12, 12)
ax.set_xticks([])
ax.set_yticks([])
ax.set_title("Packed Bubble Chart of Financial Crimes", fontsize=14, weight="bold")

# Plot bubbles
bubbles = [plt.Circle((x_positions[i], y_positions[i]), bubble_sizes[i] / 2, color="dodgerblue", alpha=0.6, edgecolor="black", linewidth=1) for i in range(num_bubbles)]
for bubble in bubbles:
    ax.add_patch(bubble)

# Add labels inside bubbles
texts = [plt.text(x_positions[i], y_positions[i], labels[i], ha='center', va='center', fontsize=8, weight="bold", color="black") for i in range(num_bubbles)]

# Adjust text to avoid overlaps
adjust_text(texts, only_move={'points': 'y', 'text': 'y'}, arrowprops=dict(arrowstyle='-', color='gray', lw=0.5))

# Show plot
plt.axis("equal")
plt.show()
