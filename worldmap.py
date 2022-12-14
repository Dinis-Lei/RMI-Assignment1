from copy import deepcopy
from itertools import permutations
from math import sqrt, sin, cos, pi, atan2
import time
from graph import MyGraph, Node

class WorldMap():

    def __init__(self, name) -> None:
        self.grid = [[' ' for i in range(49) ] for j in range(21)]
        self.curr_pos = (24,10)
        self.grid[self.curr_pos[1]][self.curr_pos[0]] = '*'
        self.graph = MyGraph()
        self.graph.add_node(24, 10)
        self.sort = self.sort1
        self.queue = Queue(5)
        self.name = name
        

    def add_pos(self, x, y) -> bool:
        ret = False # returns whether or not the bot is walking territory that's already been explored
        
        if self.grid[y][x] == ' ':
            self.grid[y][x] = '*'
            self.graph.add_node(x, y)

            directions = [(0,1), (0,-1), (1,0), (-1,0)]
            coords = [(x+dir_x, y+dir_y) for dir_x, dir_y in directions if 0 <= x+dir_x < 49 and 0 <= y+dir_y < 21]
            # for coor_x, coor_y in coords:
            #     # print("COORS: ", coor_x, coor_y)
            #     if self.grid[coor_y][coor_x] == ' ':
            #         self.grid[coor_y][coor_x] = 'x'
        else: 
            ret = True
        # print(f"1 ADD NODE: ({x}, {y})")

        diff_x = x - self.curr_pos[0]
        diff_y = y - self.curr_pos[1]
 
        # if diff_x > 0: 
        #     self.grid[y][x-1] = '-'   # left
        #     self.graph.connect_nodes(x,y, x-2,y)
        # elif diff_x < 0: 
        #     self.grid[y][x+1] = '-' # right
        #     self.graph.connect_nodes(x,y, x+2,y)
        # elif diff_y > 0: 
        #     self.grid[y-1][x] = '|' # up
        #     self.graph.connect_nodes(x,y, x,y-2)
        # elif diff_y < 0: 
        #     self.grid[y+1][x] = '|' # down
        #     self.graph.connect_nodes(x,y, x,y+2)

        self.curr_pos = (x, y)
        return ret 

    def remove_intersect(self, x, y):
        x = round(x)
        y = round(y)


    def add_intersect2(self, abs_or, int_or, x, y):
        x = round(x)
        y = round(y)
        diff = (abs_or - int_or)*pi/180 # angle difference in radians

        off_x, off_y = int(cos(diff)), int(sin(diff)) # 
        char = '-' if (y + off_y) % 2 == 0 else '|' # orientation of the intersection (vertical or horizontal)

        if (y + off_y) % 2 == 0 and (x + off_x) % 2 == 0: # Not an intersection, but a node
            print(f"Not an intersection but a node! ({x+off_x},{y+off_y})")
            return False
        
        if (y + off_y) % 2 != 0 and (x + off_x) % 2 != 0: # Not an intersection, path can't exist here
            print(f"Not an intersection! ({x+off_x},{y+off_y})")
            return False

        print(f"Add Intersection: {x + off_x}, {y + off_y} : {char}")

        self.grid[y+off_y][x+off_x] = char # Update grid
        for i in range(1,3): 
            self.graph.add_node(x + off_x*i, y + off_y*i) # Add both following nodes
            self.graph.connect_nodes(x + off_x*(i-1),y + off_y*(i-1), x + off_x*i, y + off_y*i) # Connect all nodes
        return True
        

    def add_intersect(self, abs_orientation, intersect_orientation, offset=0): #substituir if else por dict
        x, y = self.curr_pos

        #print(abs_orientation, intersect_orientation, x, y)

        if intersect_orientation == 's':
            mode_x = 0
            mode_y = 0
            if abs_orientation == 'r':
                mode_x = 1
            elif abs_orientation == 'l':
                mode_x = -1
            elif abs_orientation == 'u':
                mode_y = 1
            elif abs_orientation == 'd':
                mode_y = -1
            char = "-" if abs_orientation in ['l','r'] else "|"
            self.grid[y+mode_y][x+mode_x] = char
            self.graph.add_node(x+(mode_x*2), y+(mode_y*2))
            self.graph.connect_nodes(x,y, x+(mode_x*2),y+(mode_y*2))
            # print("FORWARD!!!!!")
            # print("Adding path to position (", x+mode_x, ",", y+mode_y, ")")
            # print(f"ADD NODE: ({x+mode_x*2}, {y+mode_y*2})")

        elif abs_orientation == intersect_orientation: # down
            self.grid[y-1][x] = '|'
            self.graph.add_node(x, y-2)
            self.graph.connect_nodes(x,y, x,y-2)
            # print("Adding path to position (", x, ",", y-1, ")")
            # print(f"ADD NODE: ({x}, {y-2})")
        elif abs_orientation in ['r','l']: # up
            self.grid[y+1][x] = '|'
            self.graph.add_node(x, y+2)
            self.graph.connect_nodes(x,y, x,y+2)
            # print("Adding path to position (", x, ",", y+1, ")")
            # print(f"ADD NODE: ({x}, {y+2})")
        elif abs_orientation == 'u':
            if intersect_orientation == 'l': # left
                self.grid[y][x-1] = '-'
                self.graph.add_node(x-2, y)
                self.graph.connect_nodes(x,y, x-2,y)
                # print("Adding path to position (", x-1, ",", y, ")")
                # print(f"ADD NODE: ({x-2}, {y})")
            else: # right
                self.grid[y][x+1] = '-'
                self.graph.add_node(x+2, y)
                self.graph.connect_nodes(x,y, x+2,y)
                # print("Adding path to position (", x+1, ",", y, ")")
                # print(f"ADD NODE: ({x+2}, {y})")
        elif abs_orientation == 'd':
            if intersect_orientation == 'l': # right
                self.grid[y][x+1] = '-'
                self.graph.add_node(x+2, y)
                self.graph.connect_nodes(x,y, x+2,y)
                # print("Adding path to position (", x+1, ",", y, ")")
                # print(f"ADD NODE: ({x+2}, {y})")
            else: # left
                self.grid[y][x-1] = '-'
                self.graph.add_node(x-2, y)
                self.graph.connect_nodes(x,y, x-2,y)
                # print("Adding path to position (", x-1, ",", y, ")")
                # print(f"ADD NODE: ({x-2}, {y})")
        else:
            print("Nothing happens...")

    def get_stubs(self, ang=0) -> list:
        stubs = []
        directions = [(0,1), (0,-1), (1,0), (-1,0)]
        for y in range(0,len(self.grid)):
            for x in range(0,len(self.grid[y])):
                if self.grid[y][x] == '-':
                    if self.grid[y][x-1] != '*': 
                        coords = [(x-1+dir_x, y+dir_y) for dir_x, dir_y in directions if 0 <= x-1+dir_x < 49 and 0 <= y+dir_y < 21]
                        around = [self.grid[c_y][c_x] == ' ' for c_x, c_y in coords]
                        if any(around):
                            stubs.append((x-1,y))
                        else:
                            self.grid[y][x-1] = '*'
                    if self.grid[y][x+1] != '*':
                        coords = [(x+1+dir_x, y+dir_y) for dir_x, dir_y in directions if 0 <= x+1+dir_x < 49 and 0 <= y+dir_y < 21]
                        around = [self.grid[c_y][c_x] == ' ' for c_x, c_y in coords]
                        if any(around):
                            stubs.append((x+1,y))
                        else:
                            self.grid[y][x+1] = '*'
                elif self.grid[y][x] == '|':
                    if self.grid[y-1][x] != '*':
                        coords = [(x+dir_x, y-1+dir_y) for dir_x, dir_y in directions if 0 <= x+dir_x < 49 and 0 <= y-1+dir_y < 21]
                        around = [self.grid[c_y][c_x] == ' ' for c_x, c_y in coords]
                        if any(around):
                            stubs.append((x,y-1))
                        else:
                            self.grid[y-1][x] = '*'
                    if self.grid[y+1][x] != '*':
                        coords = [(x+dir_x, y+1+dir_y) for dir_x, dir_y in directions if 0 <= x+dir_x < 49 and 0 <= y+1+dir_y < 21]
                        around = [self.grid[c_y][c_x] == ' ' for c_x, c_y in coords]
                        if any(around):
                            stubs.append((x,y+1))
                        else:
                            self.grid[y+1][x] = '*' 
        self.dir = ang
        stubs.sort(key=self.sort) 
        return stubs

    def filter_subs(self, stubs):
        beacons = self.graph.get_beacons()
        idx = []
        # print("FILTER")
        for i in range(len(stubs)):
            stub = self.graph.get_node(f"{stubs[i][0]}:{stubs[i][1]}")
            # print(stub.id)
            #beacon = sorted([b for b in beacons], key=lambda node : self.distance_manhatan((node.x, node.y), (stub.x, stub.y))).pop(0)
            for beacon in beacons:
                for b2 in beacon.sptb:
                    beacon2 = self.graph.get_node(b2)
                    # print(b2, len(beacon.sptb[b2]), len(self.graph.shortest_path(beacon, stub)) + self.distance_manhatan((beacon2.x, beacon2.y), (stub.x, stub.y)))
                    if len(beacon.sptb[b2]) > len(self.graph.shortest_path(beacon, stub)) + self.distance_manhatan((beacon2.x, beacon2.y), (stub.x, stub.y)):
                        idx.append(i)
                        break

        new_stubs = [stubs[i] for i in idx]
        return new_stubs

    def get_angle(self, pos1, pos2):
        return atan2(pos2[1] - pos1[1], pos2[0] - pos1[0])*180/pi

    def sort1(self, x):

        cur_node = self.graph.get_node(f"{self.curr_pos[0]}:{self.curr_pos[1]}")
        x_node = self.graph.get_node(f"{x[0]}:{x[1]}")
        begin_pos = (24, 10)

        res = (
            0.6*(len(self.graph.shortest_path(cur_node, x_node)))
             + 0.4*(-abs(self.distance_manhatan(x, begin_pos)))
        )

        return (
                res,
                abs(self.get_angle(self.curr_pos, x) - self.dir)%180
        )

    def sort2(self, node):
        beacons = self.graph.get_beacons()
        beacon_dist = self.distance_manhatan(self.curr_pos, node)
        for beacon in beacons:
            x = beacon.x
            y = beacon.y
            beacon_dist += self.distance_manhatan((node[0], node[1]), (x, y))

        return (beacon_dist, self.distance_manhatan(self.curr_pos, node))

    def distance_manhatan(self, pos1, pos2):
        return abs(pos1[0]-pos2[0])+abs(pos1[1]-pos2[1])

    def print_map(self):
        for l in self.grid:
            for c in l:
                print(c, end='')
            print('\n')

    def print_to_file(self):
        file = open(f"{self.name}_map.txt", "w")
        file.write(" ")
        for i in range(49): file.write(str(i)[-1])
        file.write('\n')
        l_count = 20
        for i in range(len(self.grid)-1, -1, -1):
            file.write(str(l_count)[-1])
            for c in self.grid[i]:
                file.write(c)
            file.write('\n')
            l_count -= 1
        file.close()

    def print_output_map(self):
        print("Writing map")
        output_grid = deepcopy(self.grid)
        #output_grid[10][24] = '*'
        file = open(f"{self.name}.map","w")
        for i in range(len(output_grid)-1, -1, -1):
            x = 0
            for c in output_grid[i]:
                if c == "*":
                    if self.graph.get_node(f"{x}:{i}").has_beacon():
                        c = str(self.graph.get_node(f"{x}:{i}").beacon)
                    else:
                        c = ' '
                elif c == "x":
                    c = ' '
                file.write(c)
                x += 1
            file.write('\n')
        file.close()


    def print_beacons(self):
        with open(f"{self.name}_beacon.txt", "w") as file:

            beacons = self.graph.get_beacons()
            perms = permutations(range(1,len(beacons)))

            solutions = []
            for perm in perms: 
                sequence = [beacons[0]] + [beacons[i] for i in perm] + [beacons[0]]
                start = sequence[0]
                paths = []
                size = 0
                for beacon in sequence[1:]:
                    path = self.graph.shortest_path(start, beacon)[:-1:2]
                    size += len(path) 
                    paths.append(path)
                    start = beacon
                solutions.append((size,paths))

            solution = min(solutions, key= lambda x: x[0])[1]
            
            for path in solution:
                for node in path:
                    #node = self.graph.get_node(node_id)
                    file.write(f"{node.x - 24} {node.y - 10}")
                    file.write('\n')
            file.write(f"0 0")
            file.write('\n')


class Queue():

    def __init__(self, size) -> None:
        self.size = size
        self.queue = []

    def put(self, item):
        if len(self.queue) >= self.size:
            self.queue = self.queue[1:] 
        self.queue += [item]

    def pop(self):
        item = self.queue[-1]
        self.queue = self.queue[:-1]
        return item
