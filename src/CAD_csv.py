import adsk.core, adsk.fusion

def export_sketch_coordinates(sketch, output_file):
    # Open the sketch for reading
    # sketch_context = adsk.fusion.SketchContext.cast(sketch)
    # sketch = sketch_context.sketch

    # Get the sketch points
    sketch_points = sketch.sketchPoints
    print(sketch_points.count)

    # Open the output file for writing
    with open(output_file, 'w') as file:
        # Write the header
        file.write('X,Y,Z\n')

        # Write the coordinates of each sketch point
        for point in sketch_points:
            x = point.geometry.x
            y = point.geometry.y
            z = point.geometry.z
            file.write(f'{x},{y},{z}\n')

    print(f'Successfully exported sketch coordinates to {output_file}')

# Get the active Fusion 360 application
app = adsk.core.Application.get()

# Get the active document
doc = app.activeDocument

# Get the active design
design = adsk.fusion.Design.cast(doc)

# Get the active root component
root_comp = design.rootComponent

# Get the active sketch
active_sketch = root_comp.sketches.item(0)

# Specify the output file path
output_file = 'C:/Users/tyler/Documents/PPA_ws/csv_files/coordinates.csv'

# Export the sketch coordinates to the CSV file
export_sketch_coordinates(active_sketch, output_file)