# Dijkstra 
# Find shortest path from vertex v to all the other vertices in a graph
# Graph is defined as list(node)
# node has edges to other nodes node = list((nodeid, weight))
from typing import List
import math 
import heapq
INF = math.inf

def dijkstra(graph: List, start: int):
    dist = [INF for x in range(len(graph))]
    visited = [False for x in range(len(graph))]
    dist[start] = 0
    h = []
    heapq.heappush(h, (0, 0))
    while h:
        vertex_id, d = heapq.heappop(h)
        if visited[vertex_id]:
            continue
        visited[vertex_id] = True
        for neigh, w in graph[vertex_id]:
            new_dist = d + w
            if new_dist < dist[neigh] and not visited[neigh]:
                # Update the distance and the heap
                heapq.heappush(h, (neigh, new_dist))
                dist[neigh] = new_dist 
    return dist


if __name__ == "__main__": 
    # Create graph
    node0 = [(1,4), (6,15), (5, 10)]
    node1 = [(0,4), (6,8), (2,3)]
    node2 = [(1,3), (6,1), (3,4)]
    node3 = [(2,4), (4,3)]
    node4 = [(6,7), (3, 3)]
    node5 = [(6,3), (0, 10)]
    node6 = [(0,15), (1,8), (2,1), (4,7), (5,3)]

    graph = [node0, node1, node2, node3, node4, node5, node6]

    dist2 = dijkstra(graph, 0)
    for node_id, d in enumerate(dist2):
        print(f"Node {node_id} dist {d}")


