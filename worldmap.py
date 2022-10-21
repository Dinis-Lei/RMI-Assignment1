from math import sqrt
from graph import Graph

class WorldMap():

    def __init__(self) -> None:
        self.grid = [[' ' for i in range(49) ] for j in range(21)]
        self.curr_pos = (24,10)
        self.grid[self.curr_pos[1]][self.curr_pos[0]] = '*'
        self.graph = Graph()


    def add_pos(self, x, y) -> bool:
        ret = False # returns whether or not the bot is walking territory that's already been explored
        
        curr_x = self.curr_pos[0] + x
        curr_y = self.curr_pos[1] + y

        if self.grid[curr_y][curr_x] == ' ':
            self.grid[curr_y][curr_x] = '*'
            self.graph.add_node(curr_x, curr_y)
        else: 
            ret = True

        if ret:
            if x > 0: 
                self.grid[curr_y][curr_x-1] = '-'   # left
                #self.graph.add_node(curr_x-1,curr_y)
            elif x < 0: 
                self.grid[curr_y][curr_x+1] = '-' # right
                #self.graph.add_node(curr_x+1,curr_y)
            elif y > 0: 
                self.grid[curr_y-1][curr_x] = '|' # up
                #self.graph.add_node(curr_x,curr_y-1)
            elif y < 0: 
                self.grid[curr_y+1][curr_x] = '|' # down
                #self.graph.add_node(curr_x,curr_y+1)

        self.curr_pos = (curr_x, curr_y)

        return ret 

    def add_intersect(self, abs_orientation, intersect_orientation): #substituir if else por dict
        x = self.curr_pos[0]
        y = self.curr_pos[1]

        print(abs_orientation, intersect_orientation, x, y)

        if abs_orientation == intersect_orientation: # down
            self.grid[y+1][x] = '|'
            self.graph.add_node(x, y+2)
            print("Adding path to position (", x, ",", y+1, ")")
        elif abs_orientation in ['r','l']: # up
            self.grid[y-1][x] = '|'
            self.graph.add_node(x, y-2)
            print("Adding path to position (", x, ",", y-1, ")")
        elif abs_orientation == 'u':
            if intersect_orientation == 'l': # left
                self.grid[y][x-1] = '-'
                self.graph.add_node(x-2, y)
                print("Adding path to position (", x-1, ",", y, ")")
            else: # right
                self.grid[y][x+1] = '-'
                self.graph.add_node(x+2, y)
                print("Adding path to position (", x+1, ",", y, ")")
        elif abs_orientation == 'd':
            if intersect_orientation == 'l': # right
                self.grid[y][x+1] = '-'
                self.graph.add_node(x+2, y)
                print("Adding path to position (", x+1, ",", y, ")")
            else: # left
                self.grid[y][x-1] = '-'
                self.graph.add_node(x-2, y)
                print("Adding path to position (", x-1, ",", y, ")")

        print("Nothing happens...")

    def print_map(self):
        for l in self.grid:
            for c in l:
                print(c, end='')
            print('\n')

    def print_to_file(self):
        file = open("map.txt", "w")
        file.write(" ")
        for i in range(49): file.write(str(i)[-1])
        file.write('\n')
        l_count = 0
        for l in self.grid:
            file.write(str(l_count)[-1])
            for c in l:
                file.write(c)
            file.write('\n')
            l_count += 1
        file.close()

    def get_stubs(self) -> list:
        stubs = []
        for y in range(1,len(self.grid)-1):
            for x in range(1,len(self.grid[y])-1):
                if self.grid[y][x] in [' ', '*']: continue
                elif self.grid[y][x] == '-':
                    if self.grid[y][x-1] != '*': stubs.append((x-1,y))
                    if self.grid[y][x+1] != '*': stubs.append((x+1,y)) 
                elif self.grid[y][x] == '|':
                    if self.grid[y-1][x] != '*': stubs.append((x,y-1))
                    if self.grid[y+1][x] != '*': stubs.append((x,y+1))
        stubs.sort(key=lambda x: distance(self.curr_pos,x)) 
        return stubs

def distance(pos1, pos2):
    return sqrt(pow(pos1[0]-pos2[0],2)+pow(pos1[1]-pos2[1],2))


class Node():

    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
        self.connected_nodes = []


    def connect_node(self, node) -> None:
        self.connected_nodes.append(node)


class Graph():

    def __init__(self) -> None:
        pass