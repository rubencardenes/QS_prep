# Ejemplo de BFS 
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple
from collections import deque

def neighbors8(point, width, height):
    neighbors = []
    for x in range(-1,2):
        for y in range(-1,2):
            if x==0 and y==0:
                continue
            xn = point[0]+x
            yn = point[1]+y
            if xn < 0 or yn < 0 or xn >= width or yn >= height: 
                continue
            neighbors.append((xn,yn))
    return neighbors
    
def floodfill(point: Tuple, mask: np.array, fillvalue: int = 128):
    # Using BFS 
    # We use FIFO queue
    height, width = mask.shape[:2]
    visited = np.zeros((height, width), dtype="uint8")
    q = deque()
    q.append(point)
    while q:
        point = q.popleft()
        for neigh in neighbors8(point, width, height):
            if visited[neigh[1], neigh[0]] or mask[neigh[1], neigh[0]] == 255:
                continue
            mask[neigh[1], neigh[0]] = fillvalue
            visited[neigh[1], neigh[0]] = 1
            q.append((neigh[0], neigh[1]))

    return mask

if __name__ == "__main__":
    # Floodfill en una imagen
    mask = np.zeros((10, 10), dtype='uint8')
    mask[5,:] = 255
    point = (0, 0)
    mask = floodfill(point, mask, fillvalue=128)

    plt.figure()
    plt.imshow(mask)
    plt.show()

    print("done")