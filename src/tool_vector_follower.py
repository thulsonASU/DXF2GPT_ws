# The goal of this script is to follow a vector path
# The path is defined by a list of points
# The TCP will follow the path at a dynamic orientation in quarternion space
# the orientation will be defined by a new frame that is fixed to the TCP with a unit vector pointing in the direction of the path
# A new vector will be defined angled upwards from the unit vector to define the new orientation of the tool relative to the origin of the new frame

import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def circle_unit_vectors(radius,increments=0.19625):
    # generate a circle of vectors
    prev_circle = [None,None,None]
    unit_vectors = []
    for i in np.arange(0, 2*np.pi, increments): # 0 to 2pi in 0.1 increments
        # generate circle
        x = radius*math.cos(i)
        y = radius*math.sin(i)
        z = 0
        circle = [x,y,z]
        unit_vector = get_unit_vector(prev_circle,circle)
        print("unit_vector: ",unit_vector)
        prev_circle = circle
        unit_vectors.append(unit_vector)
    return unit_vectors

def get_unit_vector(A,B):
    
    # if none then return none otherwise get unit vector
    if A == [None,None,None] or B == [None,None,None]:
        return [0,0,1]
    
    # get the vector between the two points
    vector = [B[0]-A[0],B[1]-A[1],B[2]-A[2]]

    # get unit vector
    vector_length = math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
    print("vector_length: ",vector_length)
    if vector_length != 0:
        vectorX = vector[0]/vector_length
        vectorY = vector[1]/vector_length
        vectorZ = vector[2]/vector_length
    else:
        print("vector length is zero")
        print("vector: ",vector)

    unit_vector = [vectorX,vectorY,vectorZ]

    return unit_vector

def rotation_matrix(unit_vector, theta):

    # get the quaternion components
    n = math.cos(theta/2)
    i = unit_vector[0]*math.sin(theta/2)
    j = unit_vector[1]*math.sin(theta/2)
    k = unit_vector[2]*math.sin(theta/2)

    # Left off here. Need to figure out how to apply this rotation correctly to adjust the angle of each unit vector. Try one vector first and then apply to all vectors in the path.
    R = np.array([[2*(n**2+i**2)-1,2*(i*j-n*k),2*(i*k+n*j)],[2*(i*j+n*k),2*(n**2+j**2)-1,2*(j*k-n*i)],[2*(i*k-n*j),2*(j*k+n*i),2*(n**2+k**2)-1]])

    return R

def plot_figure(unit_vectors):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # draw a red line through the origin along the x axios
    # ax.plot([0, 1], [0, 0], [0, 0], color='red')
    # Get the x, y, and z values
    x_vals = [vector[0] for vector in unit_vectors]
    y_vals = [vector[1] for vector in unit_vectors]
    z_vals = [vector[2] for vector in unit_vectors]
    # Plot the vectors
    ax.quiver(0, 0, 0, x_vals, y_vals, z_vals)
    # Set the limits
    ax.set_xlim([-2, 2])
    ax.set_ylim([-2, 2])
    ax.set_zlim([-2, 2])

if __name__ == "__main__":
    
    # generate a circle of unit vectors
    unit_vectors = circle_unit_vectors(1,0.19625)
    
    rotated_unit_vectors = []
    for unit_vector in unit_vectors:
        # Create a rotation matrix for this vector
        R = rotation_matrix(unit_vector, math.radians(20))
        # Apply the rotation
        rotated_unit_vector = R @ unit_vector
        rotated_unit_vectors.append(rotated_unit_vector)

    plot_figure(unit_vectors)
    plot_figure(rotated_unit_vectors)
    # Show the plot
    plt.show()



    
