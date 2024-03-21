import pandas as pd

import matplotlib.pyplot as plt

# Read the CSV file
data = pd.read_csv('C:/Users/tyler/Documents/PPA_ws/output_file.csv')

print(data)

# Get the 'X' and 'Y' columns
x = data['X']
y = data['Y']

# Plot the data on a 2D XY plane
plt.plot(x, y)
plt.xlabel('X')
plt.ylabel('Y')
plt.title('CSV Data Plot')
plt.show()