
class Node():

    def __init__(self, x, y) -> None:
        self.id = f"{x}:{y}" 
        self.x = x
        self.y = y
        self.connected_nodes = []


    def connect_node(self, node) -> None:
        self.connected_nodes.append(node)

    def __str__(self) -> str:
        return f"{self.id}, {[n.id for n in self.connected_nodes]}"


class Graph():

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


if __name__ == "__main__":

    graph = Graph()

    graph.add_node(0,0)
    graph.add_node(0,1)    
    graph.add_node(1,1)
    graph.add_node(1,0)
    graph.add_node(0,2)

    for node in graph.nodes.values():
        print(node)

    

