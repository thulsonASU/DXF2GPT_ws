#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: This class provides the functionality to convert a DXF file to a JSONL file 
for use with fine-tuning a GPT-3.5 model. The model will be trained on dictionary keys that correspond to
a grid space of the build volume. The grid space will be filled with 1's where a line is present and 0's when not.
The JSONL file will contain the dictionary keys that correspond to the grid space of the build volume.
The JSONL will be formatted to the best of the GPT-3.5/GPT-4 model's ability to predict the next key in the sequence.
A CSV file is additionally generated to verify the start and end points of the lines in the DXF file.

Dependencies:
- pandas
- matplotlib
- ezdxf
- imageio
- scipy.spatial distance
- os
- json

Usage:
1. Place the DXF file in the dxf_files directory.
2. The script will ask for user input for debugging, gif generation, and batch processing.
3. yes or no for each option.
4. The script will generate a CSV file with the start and end points of the lines in the DXF file.
5. The script will generate a JSONL file with the dictionary keys that correspond to the grid space of the build volume.
The above will be changed as this class is developed further.

Note: This script is intended to be used in conjunction with AdaOne to import a toolpath for a 3D print cell.
"""

import pandas as pd
import matplotlib.pyplot as plt
import ezdxf
import imageio # gif generation
# from scipy.spatial import distance
import numpy as np
import os
import json

class DXF2GPT:
    def __init__(self, cell_size = 1.75, build_dim = 546.1, file_name='/coordinates.jsonl'):
        '''
        @Description: The constructor initializes the DXF2GPT class with the cell size and build volume dimensions.
        Units are in mm. Default deposition size is 1.75mm and build volume is 546.1mm x 546.1mm x 508mm.
        '''
        
        # === Helper Functions ===
        # https://stackoverflow.com/questions/25585401/travelling-salesman-in-scipy
        # Calculate the euclidian distance in n-space of the route r traversing cities c, ending at the path start.
        self.path_distance = lambda r,c: np.sum([np.linalg.norm(c[r[p]]-c[r[p-1]]) for p in range(len(r))])
        # Reverse the order of all elements from element i to element k in array r.
        self.two_opt_swap = lambda r,i,k: np.concatenate((r[0:i],r[k:-len(r)+i-1:-1],r[k+1:len(r)]))
        
        # Filament Extruder default size 1.75mm
        self.cell_size = cell_size
        # Build volume size 21.5 inch x 21.5 inch x 20 inch
        self.build_dim = build_dim
       
        # Get path to work space with os
        self.dir_path = os.path.realpath('./src')
        # if no folder for csv_files exists, create one
        if not os.path.exists(self.dir_path + '/csv_files'):
            os.makedirs(self.dir_path + '/csv_files')
            
        # if no folder for plots exists, create one
        if not os.path.exists(self.dir_path + '/plots'):
            os.makedirs(self.dir_path + '/plots')
            
        # if no folder for jsonl_files exists, create one
        if not os.path.exists(self.dir_path + '/jsonl_files'):
            os.makedirs(self.dir_path + '/jsonl_files')
            
        self.json_file = self.dir_path + '/jsonl_files' + file_name
        
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

    def bresenham_line(self, x1, y1, x2, y2)->list:
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
        doc = ezdxf.readfile(self.dir_path + '/dxf_files/' + file_path)
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
    
    def csv2gridkeys(self)->list:
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
    
    def grid2plot(self,itr):
        # Plot the grid to scale
        plt.imshow(self.grid, cmap='gray', origin='lower')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.xlim(0, len(self.grid))
        plt.ylim(0, len(self.grid[0]))
        plt.title('Grid Plot')
        # save plot as image
        plt.savefig(self.dir_path + '/plots/grid_plot_{}.png'.format(itr))
        plt.close()
    
    def plot_XY(self,itr,x,y,gif=False):
        # Plot the data on a 2D XY plane (verify data is correct start and end points)
        plt.scatter(x, y, color='blue',s=1)
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.xlim(0, self.build_dim)
        plt.ylim(0, self.build_dim)
        plt.title('Data Plot')
        plt.savefig(self.dir_path + '/plots/data_plot_{}.png'.format(itr))
        plt.close()
        
        # save plot as image
        if gif:
            if not os.path.exists(self.dir_path + '/plots/gif_frames'):
                os.makedirs(self.dir_path + '/plots/gif_frames')
            
            # delete the data_plot_{}.png files if it exists before generating new gif
            for file in os.listdir(self.dir_path + '/plots/gif_frames'):
                os.remove(self.dir_path + '/plots/gif_frames/' + file)
                
            # loop through each x and y coordinate and plot the data
            print('plotting images to create a gif')
            
            # do so for the longest list
            max_len = max(len(x), len(y))
            max_dim = max(max(x), max(y))
            
            for i in range(max_len):
                # add a red dot for the start point
                plt.plot(x[0], y[0], 'go', markersize=10, label='Start')
                # add a green dot for the end point
                plt.plot(x[-1], y[-1], 'ro', markersize=5, label='End')
                
                # plot line up to the ith point
                plt.plot(x[:i], y[:i], color='blue')
                
                plt.xlabel('X')
                plt.ylabel('Y')
                plt.xlim(0, max_dim + 5)
                plt.ylim(0, max_dim + 5)
                plt.legend()
                
                # save the plot as an image
                plt.savefig(self.dir_path + '/plots/gif_frames/data_plot_{}.png'.format(i))
                plt.close()
            
            print('generating gif...')
            # compile the saved images into a gif
            image_files = sorted(os.listdir(self.dir_path + '/plots/gif_frames'), key=lambda x: int(x.split('_')[2].split('.')[0]))
            images = [imageio.v3.imread(self.dir_path + '/plots/gif_frames/' + image_file) for image_file in image_files]
            imageio.mimsave(self.dir_path + '/plots/dataRender_{}.gif'.format(itr), images, fps=30)
        else:
            pass

    def two_opt(self, cities, improvement_threshold): # 2-opt Algorithm adapted from https://en.wikipedia.org/wiki/2-opt
        route = np.arange(cities.shape[0]) # Make an array of row numbers corresponding to cities.
        improvement_factor = 1 # Initialize the improvement factor.
        best_distance = self.path_distance(route,cities) # Calculate the distance of the initial path.
        while improvement_factor > improvement_threshold: # If the route is still improving, keep going!
            distance_to_beat = best_distance # Record the distance at the beginning of the loop.
            for swap_first in range(1,len(route)-2): # From each city except the first and last,
                # print('Swap First:', swap_first)
                for swap_last in range(swap_first+1,len(route)): # to each of the cities following,
                    # print('Swap Last:', swap_last)
                    new_route = self.two_opt_swap(route,swap_first,swap_last) # try reversing the order of these cities
                    new_distance = self.path_distance(new_route,cities) # and check the total distance with this modification.
                    if new_distance < best_distance: # If the path distance is an improvement,
                        route = new_route # make this the accepted best route
                        best_distance = new_distance # and update the distance corresponding to this route.
            improvement_factor = 1 - best_distance/distance_to_beat # Calculate how much the route has improved.
            print('Improvement factor:', improvement_factor) # Print out the improvement factor.
        return route # When the route is no longer improving substantially, stop searching and return the route.

    def decode_grid(self, keys, improvement_threshold=0.01):
        # decoding from grid (keys build the grid)
        # Use the keys to update the grid
        for i in keys:
            x, y = self.dict[i]
            self.grid[x][y] = 1
        
        x_vals = []
        y_vals = []
        # get the x and y coordinates of the grid
        points = [self.dict[key] for key in keys]
        # scale the points to the build volume
        points = [(point[0] * self.cell_size, point[1] * self.cell_size) for point in points]
        
        # === Traveling Salesman Problem ===
        # https://stackoverflow.com/questions/25585401/travelling-salesman-in-scipy
        
        # Convert points to a numpy array
        cities = np.array(points)
        
        print('Calculating the best route... This may take some time...') # future work: look into parallelizing this? Other optimization algorithms?
        # Use the two_opt function to find a better route
        route_indices = self.two_opt(cities, improvement_threshold)
        
        # Get the points in the order given by the route
        route = cities[route_indices]
        
        # put first index of route at the end to close the loop
        route = np.append(route, [route[0]], axis=0)
        
        x_vals = [point[0] for point in route]
        y_vals = [point[1] for point in route]

        return x_vals, y_vals
              
    def cleanJSONL(self):
        # delete the jsonl file if it exists before generating new jsonl file
        if os.path.exists(self.json_file):
            os.remove(self.json_file)
          
    def write_JSONL(self, keys, dxf_name):
        with open(self.json_file, 'a') as f:
            # # create a dictionary for this file
            data = {"messages":  [{"role": "system", "content": "This contains the dictionary keys that correspond to the grid space of the build volume. The grid space will be filled with 1s where a line is present and 0s when not. The output will be formatted in a python list to the best of the model's ability to predict the next key in the sequence."}, 
                                  {"role": "system", "content": "The sketch name is: " + dxf_name},
                                  {"role": "system", "content": "The grid size is: " + str((len(self.grid), len(self.grid[0])))},
                                  {"role": "system", "content": "The grid area and largest possible dictionary key is: " + str(len(self.grid)**2)},
                                  {"role": "system", "content": "The size of each cell in the grid in millimeters is: " + str(self.cell_size)},
                                  {"role": "system", "content": "The build volume is: 546.1mm x 546.1mm x 508mm"},
                                  {"role": "system", "content": "The build area in millimeters is: " + str(self.build_dim**2)},
                                  {"role": "user", "content": "I would like to generate a toolpath for a 3D print cell using dictionary keys."},
                                  {"role": "assistant", "content": "Here are the dictionary keys to generate a toolpath: " + str(keys)}]
                    }
            # write the dictionary to the file as a JSON object
            f.write(json.dumps(data) + '\n')

if __name__ == '__main__':
    # initialize the class object
    d2g = DXF2GPT()
    d2g.cleanJSONL() # uncomment me if you want to delete the jsonl file before running the script (will generate new data each time)
    
    # ======================== Get user Input ========================
    
    debug = False
    gif = False
    while debug not in ['y', 'n']:
        try:
            debug = str(input('Would you like to debug? (y/n): '))
            if debug.lower() not in ['y', 'n']:
                raise ValueError('Please enter y or n.')
            
            # convert to boolean
            if debug == 'y':
                debug = True
                break
            elif debug == 'n':
                debug = False
                break
            else:
                raise ValueError('Please enter y or n. idk how you got here.')
        except ValueError as e:
            print(e)
            debug = str(input('Would you like to debug? (y/n): '))
    
    if debug == True:
        while gif not in ['y', 'n']:
            try:
                gif = str(input('Would you like to generate a gif? (y/n): '))
                if gif.lower() not in ['y', 'n']:
                    raise ValueError('Please enter y or n.')
                
                # convert to boolean
                if gif == 'y':
                    gif = True
                    break
                elif gif == 'n':
                    gif = False
                    break
                else:
                    raise ValueError('Please enter y or n. idk how you got here.')
            except ValueError as e:
                print(e)
                gif = str(input('Would you like to generate a gif? (y/n): '))
    
    # get user input for batch dxf file processing
    batch = False
    while batch not in ['y', 'n']:
        try:
            batch = str(input('Would you like to process all DXF Files in dxf_files? (y/n): '))
            if batch.lower() not in ['y', 'n']:
                raise ValueError('Please enter y or n.')
            
            # convert to boolean
            if batch == 'y':
                batch = True
                break
            elif batch == 'n':
                batch = False
                break
            else:
                raise ValueError('Please enter y or n. idk how you got here.')
        except ValueError as e:
            print(e)
            batch = str(input('Would you like to process all DXF Files in dxf_files? (y/n): '))
    
    # ======================== Run the script :) ========================
    
    if batch == True:
        # get all dxf files in the dxf_files directory
        dxf_files = os.listdir(d2g.dir_path + '/dxf_files/')
        print(dxf_files)
        for dxf_file in dxf_files:
            print('Processing:', dxf_file)
            d2g = DXF2GPT()
            d2g.read_dxf2csv(file_path=dxf_file)
            print('CSV file generated.')
            keys = d2g.csv2gridkeys()
            print('Keys generated.')
            x, y = d2g.decode_grid(keys)
            print('Grid decoded.')
            
            if debug == True:
                print('Max X:', max(x))
                print('Max Y:', max(y))
                itr = dxf_file.split('/')[-1].split('.')[0]
                d2g.grid2plot(itr=itr)
                d2g.plot_XY(itr, x, y, gif=gif)
            
            d2g.write_JSONL(keys, dxf_name=dxf_file.split('/')[-1].split('.')[0])
            
    elif batch == False:
        dxf_file = '/Complex_II.dxf' # Edit me to change the dxf file you want to process
        d2g.read_dxf2csv(file_path=dxf_file)
        keys = d2g.csv2gridkeys()
        x, y = d2g.decode_grid(keys)
        
        if debug == True:
            print('Max X:', max(x))
            print('Max Y:', max(y))
            itr = dxf_file.split('/')[-1].split('.')[0]
            d2g.grid2plot(itr=itr)
            d2g.plot_XY(itr, x, y, gif=gif)
        
        d2g.write_JSONL(keys, dxf_name=dxf_file.split('/')[-1].split('.')[0])