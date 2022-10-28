class Node():

    def __init__(self, x, y) -> None:
        self.id = f"{x}:{y}" 
        self.x = x
        self.y = y
        self.connected_nodes = []
        self.has_beacon = False
        self.sptb = {} # shortest path to beacons

    def connect_node(self, node) -> None:
        if node not in self.connected_nodes:
            self.connected_nodes.append(node)

    def is_connected(self, node) -> bool:
        return node in self.connected_nodes

    def __str__(self) -> str:
        return f"{self.id}, {[n.id for n in self.connected_nodes]}"

    def __eq__(self, __o: object) -> bool:
        return self.id == __o.id


class MyGraph():

    def __init__(self) -> None:
        self.nodes = {}

    def add_node(self, x, y):
        if f"{x}:{y}" in self.nodes:
            return
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
        
    def get_beacons(self) -> 'list[Node]':
        beacons = [self.nodes[node] for node in self.nodes if self.nodes[node].has_beacon]
        return beacons

    def __str__(self) -> str:
        string = ""
        for node in self.nodes:
            string += "".join(node) + "\n"
        return string

    def shortest_path(self, node1: Node, node2: Node, visited=[]):
        #print(f"{node1} | {node2} | {[x.id for x in visited]}")
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

    def spbb(self):
        """ Shortest Path Between Beacons"""
        beacons = self.get_beacons()
        for beacon1 in beacons:
            for beacon2 in beacons:
                if beacon1 == beacon2: continue
                beacon1.sptb[beacon2.id] = self.shortest_path(beacon1, beacon2)

if __name__ == "__main__":

    graph = MyGraph()

    """
    """
    nodes = {
        "24:10" : ['26:10', '26:10'],
        "26:10" : ['24:10', '26:8', '26:8', '26:8'],
        "26:8" : ['26:10', '28:8', '28:8', '28:8'],
        "28:10" : ['28:8'],
        "28:8" : ['26:8', '28:10', '28:10'],
        "28:12" : ['28:10', '30:12', '30:12'],
        "30:12" : ['28:12', '30:10', '32:12'],
        "30:10" : ['30:12'],
        "32:12" : ['30:12', '34:12'],
        "34:12" : ['32:12', '36:12'],
        "36:12" : ['34:12', '36:10', '36:10'],
        "36:10" : ['36:12', '34:10', '36:8'],
        "34:10" : ['36:10'],
        "36:8" : ['36:10', '38:8', '38:8', '38:8'],
        "38:8" : ['36:8', '38:6', '38:10', '38:10'],
        "38:6" : ['38:8'],
        "38:10" : ['38:8', '40:10', '40:10'],
        "40:10" : ['38:10', '40:12', '40:12'],
        "40:12" : ['40:10', '42:12', '42:12'],
        "42:12" : ['40:12', '44:12'],
        "44:12" : ['42:12', '46:12'],
        "46:12" : ['44:12', '46:10', '46:10'],
        "46:10" : ['46:12', '44:10', '44:10'],
        "44:10" : ['46:10', '44:8', '44:8'],
        "44:8" : ['44:10', '46:8', '46:8'],
        "46:8" : ['44:8', '46:6', '46:6', '46:6'],
        "46:6" : ['46:8', '44:6', '44:6'],
        "44:6" : ['46:6', '44:4', '44:4'],
        "44:4" : ['44:6', '46:4', '46:4'],
        "46:4" : ['44:4', '46:2', '46:2'],
        "46:2" : ['46:4', '44:2', '44:2'],
        "44:2" : ['46:2', '42:2'],
        "42:2" : ['44:2', '40:2'],
        "40:2" : ['42:2', '40:4'],
        "40:4" : ['40:2', '38:4', '38:4'],
        "38:4" : ['40:4', '38:2', '38:2'],
        "38:2" : ['38:4', '36:2', '36:2'],
        "36:2" : ['38:2', '34:2'],
        "34:2" : ['36:2', '34:4', '34:4'],
        "34:4" : ['34:2', '34:6'],
        "34:6" : ['34:4', '32:6', '32:6'],
        "32:6" : ['34:6', '32:4', '32:4'],
        "32:4" : ['32:6', '30:4', '30:4'],
        "30:4" : ['32:4', '28:4'],
        "28:4" : ['30:4', '26:4'],
        "26:4" : ['28:4', '26:2', '26:2'],
        "26:2" : ['26:4', '24:2', '24:2'],
        "24:2" : ['24:4'],
        "22:2" : ['24:2', '22:4', '22:4'],
        "22:4" : ['22:2', '24:4', '24:4'],
        "24:4" : ['22:4', '24:2', '24:6', '24:6'],
        "24:6" : ['24:4', '26:6', '24:8'],
        "26:6" : ['24:6'],
        "24:8" : ['24:6'],
    }


    for _id in nodes:
        x, y = [int(n) for n in _id.split(":")]
        graph.add_node(x,y)

    for _id in nodes:
        n1 = graph.nodes[_id]
        for node in nodes[_id]:
            n2 = graph.nodes[node]
            n1.connect_node(n2)

    for node in graph.nodes:
        print(graph.nodes[node])

    start = graph.get_node("28:8")
    end = graph.get_node("26:6")

    path = graph.shortest_path(start, end)
    print(path)
    for p in path:
        print(p)

    

