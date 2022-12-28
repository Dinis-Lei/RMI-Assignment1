import time


class Node():

    def __init__(self, x, y) -> None:
        self.id = f"{x}:{y}" 
        self.x = x
        self.y = y
        self.connected_nodes = []
        self.beacon = None
        self.sptb = {} # shortest path to beacons

    def connect_node(self, node) -> None:
        if node not in self.connected_nodes:
            self.connected_nodes.append(node)

    def is_connected(self, node) -> bool:
        return node in self.connected_nodes

    def has_beacon(self):
        return self.beacon != None

    def __str__(self) -> str:
        return f"{self.id}, {[n.id for n in self.connected_nodes]}"

    def __repr__(self) -> str:
        return self.id

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Node):
            return False
        return self.id == __o.id

    def __hash__(self) -> int:
        return hash(self.id)


class MyGraph():

    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}

    def add_node(self, x, y):
        if f"{x}:{y}" in self.nodes:
            return
            
        #print(f"Add Node: ({x}, {y})")
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
        node1: Node = self.nodes[f"{x1}:{y1}"]
        node2: Node = self.nodes[f"{x2}:{y2}"]
       
        node1.connect_node(node2)
        node2.connect_node(node1)

    def get_node(self, key: str) -> Node:
        return self.nodes[key] if key in self.nodes else None
        
    def get_beacons(self) -> 'list[Node]':
        beacons = [self.nodes[node] for node in self.nodes if self.nodes[node].has_beacon()]
        return beacons

    def __str__(self) -> str:
        string = ""
        for node in self.nodes:
            string += "".join(node) + "\n"
        return string

    def shortest_path1(self, node1: Node, node2: Node, visited=[]):
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

    def shortest_path(self, start_node: Node, stop_node: Node, visited=[]):

        # g = the movement cost to move from the starting point to a given square on the grid, following the path generated to get there. 
        # h = the estimated movement cost to move from that given square on the grid to the final destination.


        open_list: set[Node] = set([start_node])
        closed_list = set()

        g: dict[Node, int] = {}

        g[start_node] = 0

        parents: dict[Node, Node] = {}
        parents[start_node] = start_node

        while len(open_list) > 0:
            n = None

            # find a node with the lowest value of f() - evaluation function
            for v in open_list:
                if n == None or g[v] + self.distance_manhatan(v, stop_node) < g[n] + self.distance_manhatan(n, stop_node):
                    n = v

            if n == None:
                print('1- Path does not exist!')
                return []

            # if the current node is the stop_node
            # then we begin reconstructin the path from it to the start_node
            # Found Path
            if n == stop_node:
                reconst_path = []

                while parents[n] != n:
                    reconst_path.append(n)
                    n = parents[n]

                reconst_path.append(start_node)

                reconst_path.reverse()

                print('Path found: {}'.format(reconst_path))
                return reconst_path

            # for all neighbors of the current node do
            for son in n.connected_nodes:
                # if the current node isn't in both open_list and closed_list
                # add it to open_list and note n as it's parent
                if son not in open_list and son not in closed_list:
                    open_list.add(son)
                    parents[son] = n
                    g[son] = g[n] + 1

                # otherwise, check if it's quicker to first visit n, then m
                # and if it is, update parent data and g data
                # and if the node was in the closed_list, move it to open_list
                else:
                    if g[son] > g[n] + 1:
                        g[son] = g[n] + 1
                        parents[son] = n

                        if son in closed_list:
                            closed_list.remove(son)
                            open_list.add(son)

            # remove n from the open_list, and add it to closed_list
            # because all of his neighbors were inspected
            open_list.remove(n)
            closed_list.add(n)

        print('2- Path does not exist!')
        return []

    def spbb(self):
        """ Shortest Path Between Beacons"""
        beacons = self.get_beacons()
        for beacon1 in beacons:
            for beacon2 in beacons:
                if beacon1 == beacon2: continue
                beacon1.sptb[beacon2.id] = self.shortest_path(beacon1, beacon2)

    def distance_manhatan(self, node1: Node, node2: Node):
        return abs(node1.x - node2.x) + abs(node1.y - node2.y)

if __name__ == "__main__":

    graph = MyGraph()

    """
    """
    nodes = {
        "24:10" : ['25:10', '24:9'],
        "25:10": ["24:10", "26:10"],
        "26:10" : ['25:10', '26:9', '27:10'],
        '27:10': ['26:10', '28:10'],
        "28:10": ['27:10', '28:9'],
        '28:9': ['28:8', '28:10'],
        "28:8": ['28:9'],
        "24:8": ["24:9"],
        "24:9": ["24:10", "24:8"],
        '26:9': ['26:10', '26:8'],
        '26:8': ['26:9'],
    }


    for _id in nodes:
        x, y = [int(n) for n in _id.split(":")]
        graph.add_node(x,y)

    for _id in nodes:
        n1 = graph.nodes[_id]
        for node in nodes[_id]:
            n2 = graph.nodes[node]
            n1.connect_node(n2)

    # for node in graph.nodes:
    #     print(graph.nodes[node])

    start = graph.get_node("28:8")
    end = graph.get_node("24:10")

    tic = time.perf_counter()
    path1 = graph.shortest_path(start, end)
    toc = time.perf_counter()
    print(toc - tic)
    tic = time.perf_counter()
    path2 = graph.shortest_path1(start, end)
    toc = time.perf_counter()
    print(toc - tic)

    for p1, p2 in zip(path1, path2):
        print(p1.id, p2.id)

    

