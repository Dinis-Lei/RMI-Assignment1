
class Node():

    def __init__(self, x, y) -> None:
        self.id = f"{x}:{y}" 
        self.x = x
        self.y = y
        self.connected_nodes = []


    def connect_node(self, node) -> None:
        self.connected_nodes.append(node)

    def is_connected(self, node) -> bool:
        return node in self.connected_nodes

    def __str__(self) -> str:
        return f"{self.id}, {[n.id for n in self.connected_nodes]}"


class MyGraph():

    def __init__(self) -> None:
        self.nodes = {}

    def add_node(self, x, y):
        node = Node(x,y)
        self.nodes[node.id] = node

        if f"{x-1}:{y}" in self.nodes:
            self.nodes[node.id].connect_node(self.nodes[f"{x-1}:{y}"])
            self.nodes[f"{x-1}:{y}"].connect_node(self.nodes[node.id])        
        if f"{x+1}:{y}" in self.nodes:
            self.nodes[node.id].connect_node(self.nodes[f"{x+1}:{y}"])
            self.nodes[f"{x+1}:{y}"].connect_node(self.nodes[node.id])
        if f"{x}:{y-1}" in self.nodes:
            self.nodes[node.id].connect_node(self.nodes[f"{x}:{y-1}"])
            self.nodes[f"{x}:{y-1}"].connect_node(self.nodes[node.id])
        if f"{x}:{y+1}" in self.nodes:
            self.nodes[node.id].connect_node(self.nodes[f"{x}:{y+1}"])
            self.nodes[f"{x}:{y+1}"].connect_node(self.nodes[node.id]) 

    def connect_nodes(self, x1, y1, x2, y2):
        node1 = self.nodes[f"{x1}:{y1}"]
        node2 = self.nodes[f"{x2}:{y2}"]
       
        node1.connect_node(node2)
        node2.connect_node(node1)

    def get_node(self, node) -> Node:
        return self.nodes[node]
        

    def __str__(self) -> str:
        string = ""
        for node in self.nodes:
            string += "".join(node) + "\n"
        return string

    def shortest_path(self, node1: Node, node2: Node, visited=[]):
        if node1.is_connected(node2):
            return [node1, node2]
        
        paths = []
        for node in node1.connected_nodes:
            if node in visited:
                continue
            path = self.shortest_path(node, node2, visited=visited+[node1])
            if path:
                paths.append([node1] + path)
        
        paths = [path for path in paths if path]
        if not paths:
            return []
        min_path = min(paths, key=lambda x: len(x))
        return min_path

if __name__ == "__main__":

    graph = MyGraph()

    graph.add_node(0,0)
    graph.add_node(0,1)
    graph.add_node(0,2)
    graph.add_node(0,3)    
    graph.add_node(1,1)
    graph.add_node(1,0)
    graph.add_node(0,4)
    graph.add_node(1,4)

    nodes = []
    for node in graph.nodes.values():
        nodes.append(node)
        #print(node)

    print(nodes[0], nodes[-1])

    path = graph.shortest_path(nodes[0], nodes[-1])
    print(path)
    for p in path:
        print(p)

    

