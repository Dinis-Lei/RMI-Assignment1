from math import sqrt
from graph import MyGraph

class WorldMap():

    def __init__(self) -> None:
        self.grid = [[' ' for i in range(49) ] for j in range(21)]
        self.curr_pos = (24,10)
        self.grid[self.curr_pos[1]][self.curr_pos[0]] = '*'
        self.graph = MyGraph()
        self.graph.add_node(24, 10)
        



    def add_pos(self, x, y) -> bool:
        ret = False # returns whether or not the bot is walking territory that's already been explored
        

        if self.grid[y][x] == ' ':
            self.grid[y][x] = '*'
            self.graph.add_node(x, y)
        else: 
            ret = True

        print(f"1 ADD NODE: ({x}, {y})")

        diff_x = x - self.curr_pos[0]
        diff_y = y - self.curr_pos[1]

        if not ret:
            if diff_x > 0: 
                self.grid[y][x-1] = '-'   # left
                self.graph.connect_nodes(x,y, x-2,y)
            elif diff_x < 0: 
                self.grid[y][x+1] = '-' # right
                self.graph.connect_nodes(x,y, x+2,y)
            elif diff_y > 0: 
                self.grid[y-1][x] = '|' # up
                self.graph.connect_nodes(x,y, x,y-2)
            elif diff_y < 0: 
                self.grid[y+1][x] = '|' # down
                self.graph.connect_nodes(x,y, x,y+2)

        self.curr_pos = (x, y)

        return ret 

    def add_intersect(self, abs_orientation, intersect_orientation, offset=0): #substituir if else por dict
        x = self.curr_pos[0]
        y = self.curr_pos[1]

        #print(abs_orientation, intersect_orientation, x, y)

        if abs_orientation == intersect_orientation: # down
            self.grid[y-1][x] = '|'
            self.graph.add_node(x, y-2)
            self.graph.connect_nodes(x,y, x,y-2)
            print("Adding path to position (", x, ",", y-1, ")")
            print(f"ADD NODE: ({x}, {y-2})")
        elif abs_orientation in ['r','l']: # up
            self.grid[y+1][x] = '|'
            self.graph.add_node(x, y+2)
            self.graph.connect_nodes(x,y, x,y+2)
            print("Adding path to position (", x, ",", y+1, ")")
            print(f"ADD NODE: ({x}, {y+2})")
        elif abs_orientation == 'u':
            if intersect_orientation == 'l': # left
                self.grid[y][x-1] = '-'
                self.graph.add_node(x-2, y)
                self.graph.connect_nodes(x,y, x-2,y)
                print("Adding path to position (", x-1, ",", y, ")")
                print(f"ADD NODE: ({x-2}, {y})")
            else: # right
                self.grid[y][x+1] = '-'
                self.graph.add_node(x+2, y)
                self.graph.connect_nodes(x,y, x+2,y)
                print("Adding path to position (", x+1, ",", y, ")")
                print(f"ADD NODE: ({x+2}, {y})")
        elif abs_orientation == 'd':
            if intersect_orientation == 'l': # right
                self.grid[y][x+1] = '-'
                self.graph.add_node(x+2, y)
                self.graph.connect_nodes(x,y, x+2,y)
                print("Adding path to position (", x+1, ",", y, ")")
                print(f"ADD NODE: ({x+2}, {y})")
            else: # left
                self.grid[y][x-1] = '-'
                self.graph.add_node(x-2, y)
                self.graph.connect_nodes(x,y, x-2,y)
                print("Adding path to position (", x-1, ",", y, ")")
                print(f"ADD NODE: ({x-2}, {y})")
        else:
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
        l_count = 20
        for i in range(len(self.grid)-1, -1, -1):
            file.write(str(l_count)[-1])
            for c in self.grid[i]:
                file.write(c)
            file.write('\n')
            l_count -= 1
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
        stubs.sort(key=lambda x: (distance_manhatan(self.curr_pos,x), not self.graph.get_node(f"{x[0]}:{x[1]}").is_connected(self.graph.get_node(f"{self.curr_pos[0]}:{self.curr_pos[1]}")))) 
        return stubs



def distance_manhatan(pos1, pos2):
    return abs(pos1[0]-pos2[0])+abs(pos1[1]-pos2[1])

