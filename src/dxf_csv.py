import ezdxf

# Load the DXF document
doc = ezdxf.readfile("C:/Users/tyler/Documents/PPA_ws/Aero Test.dxf")

# Get the modelspace which contains the entities
modelspace = doc.modelspace()

# Open the output file
with open("output_file.csv", "w") as file:
    # Write the headers to the file
    file.write("X,Y,Z\n")
    
    # Iterate over each entity in the modelspace
    for entity in modelspace:
        # Check if the entity is a line
        if entity.dxftype() == 'LINE':
            # Write the start and end points of the line to the file
            file.write(f"{entity.dxf.start.x},{entity.dxf.start.y},{entity.dxf.start.z}\n")
            file.write(f"{entity.dxf.end.x},{entity.dxf.end.y},{entity.dxf.end.z}\n")