# BFS tree
from queue import deque
from dataclasses import dataclass

@dataclass
class Node:
    left = None
    right = None
    value: int = 0

def BFS_tree(root):
    result = []
    q = deque()
    q.append(root)
    while q:
        node = q.popleft()
        result.append(node.value)
        if node.left:
            q.append(node.left)
        if node.right:
            q.append(node.right)
        
    return result 

def DFS_tree(root):
    result = []
    q = deque()
    q.append(root)
    while q:
        node = q.pop()
        result.append(node.value)
        if node.right:
            q.append(node.right)
        if node.left:
            q.append(node.left)
        
    return result 

def DFS_recursive(root):
    def traverse_right(node, result):
        if node is None:
            return
        result.append(node.value)
        traverse_right(node.left, result)
        traverse_right(node.right, result)
    result = []
    traverse_right(root, result)
    return result


if __name__ == "__main__":
    """
    Example tree
           1 
        2.     6
      3   5       7
     4               8  
    """
    
    # Tree construction 
    root = Node()
    root.value = 1

    root.left = Node()
    l = root.left
    l.value = 2
    root.right = Node()
    r = root.right
    r.value = 6

    r.right = Node()
    r = r.right
    r.value = 7

    r.right = Node()
    r.right.value = 8
    
    l.left = Node()
    l2 = l.left
    l2.value = 3
    l.right = Node()
    r = l.right
    r.value = 5

    l2.left = Node()
    l2.left.value = 4
    
    result = BFS_tree(root)
    print("BFS: ", result)

    result = DFS_tree(root)
    print("DFS: ", result)

    result = DFS_recursive(root)
    print("DFS: ", result)