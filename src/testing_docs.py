import adsk.core, adsk.fusion, traceback

app = adsk.core.Application.get()
ui = app.userInterface

# Get the active product and cast it to a Design object
design = adsk.fusion.Design.cast(app.activeProduct)
if not design:
    ui.messageBox('No active Fusion design found.')
else:
    # Access the rootComponent of the design
    rootComp = design.rootComponent
    sketches = rootComp.sketches
    
    # Specify the index of the sketch you want to access
    # Note: The first sketch has an index of 0
    sketchIndex = 0 # Change this to the index of the sketch you want
    
    # Use the item function to access the sketch by its index
    sketch = sketches.item(sketchIndex)
    
    if sketch is None:
        ui.messageBox('No sketch found at the specified index.')
    else:
        # Perform operations on the sketch
        # For example, print the name of the sketch
        print('Sketch Name: ', sketch.name)
        print(sketch.arePointsShown)