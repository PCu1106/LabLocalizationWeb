import plotly.graph_objs as go
from PIL import Image
import csv
import numpy as np


def save_figure_to_html(fig, filename):
    fig.write_html(filename)


def visualize_heatmap(value = 12, colorbar_title="colorbar", title=None, show=False):
    fig = go.Figure()
    map_image_path = "public/images/LABmap2.jpg"
    csv_file_path = "position_history/history_4.csv"
    floor_plan_filename = Image.open(map_image_path)
    width_meter, height_meter = floor_plan_filename.size
    data = []
    

    with open(csv_file_path, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip header row
        for row in csv_reader:
            groundtruth, estimated, rssi1, rssi2, rssi3, rssi4, rssi5, rssi6 = map(int, row)
            data.append((int(groundtruth/100), int(groundtruth%100)))


    # Create a 2D array to store the heatmap data
    heatmap_data = np.zeros((height_meter, width_meter), dtype=int)
    for x, y in data:
        if 0 <= x < width_meter and 0 <= y < height_meter:
            heatmap_data[300, 300] += 10
    


    # # add heat map
    # fig.add_trace(
    #     go.Scatter(
    #         x=np.arange(0, width_meter),  # X coordinates of the heatmap cells
    #                y=np.arange(0, height_meter),
    #                mode='markers',
    #                marker=dict(
    #                            color=heatmap_data.flatten(),  # Use the heatmap_data as color values
    #                            colorbar=dict(title=colorbar_title),
    #                            colorscale="Rainbow"),
    #                text=heatmap_data.flatten(),
    #                name=title))
    
    max_marked_value = np.max(heatmap_data[heatmap_data > 0])
    marked_indices = np.argwhere(heatmap_data > 0)
    y_indices, x_indices = np.where(heatmap_data > 0)
    
    for y, x in marked_indices:
        marked_value = heatmap_data[y, x]
        fig.add_trace(
            go.Scatter(
                x=[x],  # X coordinate of the marked point
                y=[y],  # Y coordinate of the marked point
                mode='markers',
                marker=dict(
                    size=7,  # Adjust the size of the marker for visibility
                    color=80,  # Use the value from heatmap_data as the color for the marker
                    colorscale="Rainbow",  # Adjust the colorscale to your preference
                    cmin=0,  # Set the minimum value for the color scale
                    cmax=max_marked_value,  # Set the maximum value for the color scale
                    colorbar=dict(
                        title="Value",  # Add colorbar with title
                        tickvals=[0, max_marked_value],  # Set custom tick values
                        ticktext=["0", str(max_marked_value)]  # Set custom tick labels
                    ),
                    opacity=0.8,
                    showscale=True  # Show the color scale on the side
                ),
                text=str(marked_value),  # Convert the value to a string
                name='Marked Point'
            )
        )

    # add floor plan
    floor_plan = floor_plan_filename
    fig.update_layout(images=[
        go.layout.Image(
            source=floor_plan,
            xref="x",
            yref="y",
            x=0,
            y=height_meter,
            sizex=width_meter,
            sizey=height_meter,
            sizing="contain",
            opacity=1,
            layer="below",
        )
    ])

    # configure
    fig.update_xaxes(autorange=False, range=[0, width_meter])
    fig.update_yaxes(autorange=False, range=[0, height_meter], scaleanchor="x", scaleratio=1)
    fig.update_layout(
        title=go.layout.Title(
            text=title or "No title.",
            xref="paper",
            x=0,
        ),
        autosize=True,
        width=900,
        height=200 + 900 * height_meter / width_meter,
        template="plotly_white",
    )

    
    fig.show()

    

visualize_heatmap()