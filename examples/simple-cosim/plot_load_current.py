import matplotlib.pyplot as plt
import pandas as pd

# Load data from CSV
data = pd.read_csv('load_current_data.csv', delimiter=' ', names=['Real', 'Imaginary'])

# Create time steps
time_steps = list(range(len(data)))

# Plot the real part of the load current
plt.figure(figsize=(10, 5))
plt.plot(time_steps, data['Real'], label='Real Part of Load Current', linestyle='-', marker='o')
plt.xlabel('Time Step')
plt.ylabel('Current (A)')
plt.title('Real Part of Load Current Over Time')
plt.legend()
plt.grid(True)
plt.show()

# Plot the imaginary part of the load current
plt.figure(figsize=(10, 5))
plt.plot(time_steps, data['Imaginary'], label='Imaginary Part of Load Current', linestyle='-', marker='o', color='r')
plt.xlabel('Time Step')
plt.ylabel('Current (A)')
plt.title('Imaginary Part of Load Current Over Time')
plt.legend()
plt.grid(True)
plt.show()
