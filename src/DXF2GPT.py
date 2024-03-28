#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: This class provides the functionality to convert a DXF file to a JSONL file 
for use with fine-tuning a GPT-4 model. The model will be trained on dictionary keys that correspond to
a grid space of the build volume. The grid space will be filled with 1's where a line is present and 0's when not.
The JSONL file will contain the dictionary keys that correspond to the grid space of the build volume.
The JSONL will be formatted to the best of the GPT-4 model's ability to predict the next key in the sequence.
A CSV file is additionally generated to verify the start and end points of the lines in the DXF file.

Dependencies:
- pandas
- matplotlib
- ezdxf
- os

Usage:
1. Run the read_dxf() method to generate a CSV file of the start and end points of the lines in the DXF file.
2. Run the csv_to_grid() method to convert the CSV file to a grid of cells.
3. Run the grid_to_plot() method to plot the grid to scale.
4. Run the grid_to_XYplot() method to plot the grid to the build space.
5. Run the write_JSONL() method to write the JSONL file.
The above will be changed as this class is developed further.

Note: This script is intended to be used in conjunction with AdaOne to import a toolpath for a 3D print cell.
"""

import pandas as pd
import matplotlib.pyplot as plt
import ezdxf
import os

class DXF2GPT:
    def __init__(self, cell_size = 1.75, build_dim = 546.1):
        '''
        @Description: The constructor initializes the DXF2GPT class with the cell size and build volume dimensions.
        Units are in mm. Default deposition size is 1.75mm and build volume is 546.1mm x 546.1mm x 508mm.
        '''
        
        # Filament Extruder default size 1.75mm
        self.cell_size = cell_size
        # Build volume size 21.5 inch x 21.5 inch x 20 inch
        self.build_dim = build_dim
        # Get path to work space with os
        self.dir_path = os.path.realpath('./src')
        
        # Initalize grid list
        self.grid = []
        # Generate initial grid
        for i in range(int(self.build_dim / self.cell_size)):
            row = []
            for j in range(int(self.build_dim / self.cell_size)):
                row.append(0)
            self.grid.append(row)
        
        # Initalize dict 
        self.dict = {}
        # Generate initial dictionary of grid coordinates
        count = 1
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                self.dict[count] = (j, i)
                count += 1
        
        # print(self.dict)

    def bresenham_line(self, x1, y1, x2, y2):
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        sx = -1 if x1 > x2 else 1
        sy = -1 if y1 > y2 else 1
        if dx > dy:
            err = dx / 2.0
            while x != x2:
                points.append((x, y))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y2:
                points.append((x, y))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy        
        points.append((x, y))
        return points

    def read_dxf2csv(self, file_path):
        # Load the DXF document
        doc = ezdxf.readfile(self.dir_path + file_path)
        # Get the modelspace which contains the entities
        modelspace = doc.modelspace()

        # Open the output file
        with open(self.dir_path + '/csv_files/coordinates.csv', "w") as file:
            # Write the headers to the file
            file.write("X,Y,Z\n")
            
            # Iterate over each entity in the modelspace
            for entity in modelspace:
                # Check if the entity is a line
                if entity.dxftype() == 'LINE':
                    # Lets actually just record the start and end points
                    file.write(f"{entity.dxf.start.x},{entity.dxf.start.y},{entity.dxf.start.z}\n")
                    file.write(f"{entity.dxf.end.x},{entity.dxf.end.y},{entity.dxf.end.z}\n")
    
    def cleanGrid(self):
        # Create a fresh grid of cells (grid is generated to the size of the build volume)
        for i in range(int(self.build_dim / self.cell_size)):
            row = []
            for j in range(int(self.build_dim / self.cell_size)):
                row.append(0)
            self.grid.append(row)
    
    def csv2gridkeys(self):
        # Read the CSV file
        data = pd.read_csv(self.dir_path + "/csv_files/coordinates.csv")
        
        # Fill in grid with lines from the data
        for i in range(1, len(data), 2):
            x1 = int(data['X'][i-1] / self.cell_size)
            y1 = int(data['Y'][i-1] / self.cell_size)
            x2 = int(data['X'][i] / self.cell_size)
            y2 = int(data['Y'][i] / self.cell_size)
            # update grid with line
            for point in self.bresenham_line(x1, y1, x2, y2):
                self.grid[point[0]][point[1]] = 1
                
        # get dictionary keys from grid
        keys = []
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j] == 1:
                    for key, value in self.dict.items():
                        if value == (i, j):
                            keys.append(key)
        return keys
    
    def grid2plot(self):
        # Plot the grid to scale
        plt.imshow(self.grid, cmap='gray', origin='lower')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.xlim(0, len(self.grid))
        plt.ylim(0, len(self.grid[0]))
        plt.title('Grid Plot')
        # save plot as image
        plt.savefig(self.dir_path + '/plots/grid_plot.png')
        plt.close()
    
    def plot_XY(self,x,y):
        # Plot the data on a 2D XY plane (verify data is correct start and end points)
        plt.scatter(x, y, color='blue',s=1)
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.xlim(0, self.build_dim)
        plt.ylim(0, self.build_dim)
        plt.title('Data Plot')
        # save plot as image
        plt.savefig(self.dir_path + '/plots/data_plot.png')
        plt.close()
    
    def decode_grid(self, keys):
        # decoding from grid (keys build the grid)
        
        # Use the keys to update the grid
        for i in keys:
            x, y = self.dict[i]
            self.grid[x][y] = 1
            
        # get the x and y coordinates of the grid
        x_vals = []
        y_vals = []
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j] == 1:
                    x_vals.append(i)
                    y_vals.append(j)
        return x_vals, y_vals
                    
    def write_JSONL(self):
        pass
    
if __name__ == '__main__':
    # dxf_file = '/dxf_files/Complex_Sketch.dxf'
    dxf_file = '/dxf_files/Points_Test.dxf'
    d2g = DXF2GPT()
    d2g.read_dxf2csv(file_path=dxf_file)
    keys = d2g.csv2gridkeys()
    x, y = d2g.decode_grid(keys)
    d2g.grid2plot()
    d2g.plot_XY(x, y)
    print('Completed. This is not needd but makes me feel better when it prints. :)')