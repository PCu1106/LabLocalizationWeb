import plotly.graph_objs as go
from PIL import Image
import csv
import numpy as np


def save_figure_to_html(fig, filename):
    fig.write_html(filename)


def visualize_heatmap(value = 12, colorbar_title="colorbar", title=None, show=False):
    fig = go.Figure()
    map_image_path = "public/images/LABmap2.jpg"
    csv_file_path = "position_history/history_3.csv"
    floor_plan_filename = Image.open(map_image_path)
    width_meter, height_meter = floor_plan_filename.size
    data = []
    

    with open(csv_file_path, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip header row
        for row in csv_reader:
            groundtruth, estimated, rssi1, rssi2, rssi3, rssi4, rssi5, rssi6 = map(float, row)
            data.append((int(groundtruth/100), int(groundtruth%100)))


    # Create a 2D array to store the heatmap data
    heatmap_data = np.zeros((height_meter, width_meter), dtype=int)
    for x, y in data:
        if 0 <= x < width_meter and 0 <= y < height_meter:
            heatmap_data[39*y-3, 117+38*x] += 10
    


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
    
    # Calculate the maximum marked value
    max_marked_value = np.max(heatmap_data[heatmap_data > 0])

    # Get the positions of marked points from heatmap_data
    marked_positions = np.argwhere(heatmap_data > 0)

    # Extract x and y coordinates from the marked positions
    marked_x = marked_positions[:, 1]
    marked_y = marked_positions[:, 0]

    # Create a scatter plot with markers
    fig = go.Figure()

    fig.add_trace(
    go.Scatter(
        x=marked_x,
        y=marked_y,
        mode='markers',
        marker=dict(
            size=10,
            color=heatmap_data[marked_y, marked_x],  # Use values from heatmap_data for color
            colorscale="Rainbow",
            cmin=0,
            cmax=max_marked_value,
            colorbar=dict(
                title="Value",
                tickvals=[0, max_marked_value],
                ticktext=["0", str(max_marked_value)]
            )
        ),
        text=heatmap_data[marked_y, marked_x].astype(str),  # Convert values to string
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
    #fig.show()
    fig.write_image('heatmap.png')

    

visualize_heatmap()
