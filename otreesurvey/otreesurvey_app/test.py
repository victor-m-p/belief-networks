# Example list
import numpy as np 
lst = [3, 7, 3, 2, 9, 3]

# Convert to NumPy array
arr = np.array(lst)

# Target value
target = 3

# Create boolean array (0, 1)
bool_arr = (arr == target).astype(int)
bool_arr