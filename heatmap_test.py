import csv
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

# Load the map image
map_image_path = "public/images/LABmap2.jpg" 
map_image = Image.open(map_image_path)
map_width, map_height = map_image.size

# Read data from the CSV file
csv_file_path = "position_history/history_4.csv"  
data = []

with open(csv_file_path, "r") as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)
    for row in csv_reader:
        groundtruth, estimated, rssi1, rssi2, rssi3, rssi4, rssi5, rssi6 = map(int, row)
        data.append((int(groundtruth/10), int(groundtruth%10)))

# Create a 2D array to store the heatmap data
heatmap_data = np.zeros((map_height, map_width), dtype=int)
for x, y in data:
    if 0 <= x < map_width and 0 <= y < map_height:
        heatmap_data[y, x] += 1

# Create the heatmap using Matplotlib
fig, ax = plt.subplots(figsize=(10, 10))
cax = ax.matshow(heatmap_data, cmap="viridis", origin="upper")
plt.colorbar(cax, label="Occurrences")
ax.imshow(map_image, extent=(0, map_width, 0, map_height), alpha=0.7)

# Annotate cells with occurrence counts
for y in range(map_height):
    for x in range(map_width):
        count = heatmap_data[y, x]
        if count > 0:
            ax.text(x, y, str(count), va='center', ha='center', color='black', fontsize=8)

plt.title("Occurrences Heatmap on Map")
plt.xlabel("X Coordinate")
plt.ylabel("Y Coordinate")
plt.tight_layout()

# Save the plot as an image
plt.savefig("heatmap.png", dpi=300)  # Save with high resolution
plt.show()