
import sys
from croblink import *
from math import *
import xml.etree.ElementTree as ET
import time

from worldmap import WorldMap

CELLROWS=7
CELLCOLS=14

class MyRob(CRobLinkAngs):
    def __init__(self, rob_name, rob_id, angles, host):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)
        self.direction = 0 # Right
        self.map = WorldMap()


    # In this map the center of cell (i,j), (i in 0..6, j in 0..13) is mapped to labMap[i*2][j*2].
    # to know if there is a wall on top of cell(i,j) (i in 0..5), check if the value of labMap[i*2+1][j*2] is space or not
    def setMap(self, labMap):
        self.labMap = labMap

    def printMap(self):
        for l in reversed(self.labMap):
            print(''.join([str(l) for l in l]))

    def run(self):
        if self.status != 0:
            print("Connection refused or error")
            quit()

        state = 'stop' ####
        stopped_state = 'run'

        self.init_pos = None
        prev_loc = None
        self.intersections = []
        direction = None
        count = 0
        wanted_rotation = 0
        stub_seeking = False
        curr_stub = None
        path = []

        path = [(26, 10), (26, 8), (28, 8)]
        target = path.pop(0)


        while True:
            #print(f"{state= }")
            self.readSensors()

            # self.driveMotors(0.05,-0.05)
            # print(self.measures.compass)


            if not self.init_pos:
                self.init_pos = (self.measures.x, self.measures.y)
                prev_loc = [24, 10]
                print(prev_loc)

            if self.measures.endLed:
                print(self.rob_name + " exiting")
                quit()

            if state == 'stop' and self.measures.start:
                state = stopped_state
                #self.driveMotors(0,0)

            if state != 'stop' and self.measures.stop:
                stopped_state = state
                state = 'stop'
                
            if state == 'run':
                cur_loc = [self.measures.x, self.measures.y]

                repeat = False

                cur_x = cur_loc[0] - self.init_pos[0] + 24
                cur_y = cur_loc[1] - self.init_pos[1] + 10

                if abs(prev_loc[0] - cur_x) >= 2:
                    count = 1
                    print("VERTICE")
                    print(cur_loc, prev_loc)
                    print(cur_x, cur_y)
                    repeat = self.map.add_pos(round(cur_x), prev_loc[1])
                    prev_loc[0] = round(cur_x)
                    print("------")
                    while self.intersections:
                        intersect = self.intersections.pop()
                        print("Intersect:", intersect)
                        self.map.add_intersect(intersect[0],intersect[1]) 
                elif abs(prev_loc[1] - cur_y) >= 2:
                    count = 1
                    print("VERTICE")
                    print(cur_loc, prev_loc)
                    print(cur_x, cur_y)
                    self.map.add_pos(prev_loc[0], round(cur_y))
                    prev_loc[1] = round(cur_y)
                    print("------")
                    while self.intersections:
                        intersect = self.intersections.pop()
                        print("Intersect:", intersect)
                        self.map.add_intersect(intersect[0],intersect[1]) 
                
                if prev_loc[0] == 24 and prev_loc[1] == 10 and count != 0:
                    repeat = True
                

                self.map.print_to_file()

                self.detect_intersection()
                
                if not repeat:
                    self.wander()
                else:
                    print("STUB SEEKING STARTED")
                    # self.driveMotors(0,0)
                    # stubs = self.map.get_stubs()
                    # if stubs:
                    #     curr_stub = self.map.get_stubs().pop(0)
                    # else:
                    #     quit() # map found?
                    state = "seek_stub"

            elif state == "seek_stub":
                print("SEEK STUB")
                for node in self.map.graph.nodes:
                    print(self.map.graph.nodes[node])

                stubs = self.map.get_stubs()

                if not stubs:
                    state = "finish"
                    return

                curr_stub = stubs.pop(0)
                print(stubs)
                print(curr_stub)
                print(self.map.curr_pos)
                pos = self.map.curr_pos
                
                node1 = self.map.graph.get_node(f"{pos[0]}:{pos[1]}")
                node2 = self.map.graph.get_node(f"{curr_stub[0]}:{curr_stub[1]}")

                path = self.map.graph.shortest_path(node1, node2)[1:]
                print(f"Path: {[x.id for x in path]}")
                target = path.pop(0)
                state = "move_to"
                print(self.measures.compass)
                print(state)
                #return

            elif state == "move_to":
                #print(f"Target: {target.id}")

                cur_loc = [self.measures.x, self.measures.y]
                cur_x = cur_loc[0] - self.init_pos[0] + 24
                cur_y = cur_loc[1] - self.init_pos[1] + 10
                tar_x = target.x
                tar_y = target.y
                #print(f"Position: {(cur_x, cur_y)}")
                if cur_x == tar_x and cur_y == tar_y:
                    

                    # Reached desired node
                    self.map.add_pos(int(cur_x), int(cur_y))
                    self.detect_intersection()
                    line = [x == '1' for x in self.measures.lineSensor]
                    print("LINE: ", line)
                    if sum(line[2:5]) > 0:
                        print("ADD")
                        self.map.add_stub(self.measures.compass)

                    while self.intersections:
                        intersect = self.intersections.pop()
                        print("Intersect:", intersect)
                        self.map.add_intersect(intersect[0],intersect[1]) 

                    self.map.print_to_file()

                    if not path:
                        # found path
                        state = "seek_stub"
                        print("DONE")
                        self.driveMotors(0,0)
                        continue
                        
                    target = path.pop(0)
                    tar_x = target.x
                    tar_y = target.y

                diff = 0
                breaker = 0
                direction = 0

                if cur_x != tar_x:
                    diff = cur_x - tar_x
                    if diff < 0:
                        direction = 0
                    else:
                        direction = 180
                elif cur_y != tar_y:
                    diff = cur_y - tar_y
                    if diff > 0:
                        direction = -90
                    else:
                        direction = 90

                breaker = 0.06 if 0 < abs(diff) < 0.2 else 0.03 if abs(diff) < 0.4 else 0
                    
                #print(f"Direction: {direction}")

                self.move(direction, breaker)

                

    def move(self, direction, breaker):

        cur_direction = self.measures.compass

        #print(f"{cur_direction}, {direction}, {breaker}")
        if direction == 180 and not (177 <= abs(cur_direction)):
            mod = 1 if cur_direction < 0 else -1
            self.driveMotors(0.05*mod, 0.05*-mod)
        elif direction != 180 and  not (direction-3 < cur_direction < direction+3):
            diff = cur_direction - direction
            mod = 1 if diff > 0 else -1
            self.driveMotors(0.05*mod, 0.05*-mod)
        else:
            self.driveMotors(0.1 - breaker,0.1 - breaker)

        self.detect_intersection()

    def detect_intersection(self):
        curr_orientation = None
        if -5 < self.measures.compass < 5: curr_orientation = 'r' # right
        elif 85 < self.measures.compass < 95: curr_orientation = 'u' # up
        elif 175 < abs(self.measures.compass) < 180: curr_orientation = 'l' #left
        elif -95 < self.measures.compass < -85: curr_orientation= 'd' #down

        if curr_orientation:
            cross_roads = self.detect_cross_roads()
            if 'l' in cross_roads: # relative to the robot orientation
                self.intersections.append((curr_orientation,'l'))
            if 'r' in  cross_roads:
                self.intersections.append((curr_orientation,'r'))


            

    def wander(self):
        wheel_speed = 0.15
        line = [x == '1' for x in self.measures.lineSensor]

        # if sum(line[0:3]) > sum(line[-3:]):
        #     line[-3:] = [0,0,0]
        # elif sum(line[0:3]) < sum(line[-3:]):
        #     line[0:3] = [0,0,0]

        # print(line)

        if line[0] and line[1]:
            #print('Rotate Left')
            self.driveMotors(-wheel_speed,+wheel_speed)
        elif line[1]:
            #print('Rotate slowly Left')
            self.driveMotors(0,+wheel_speed)
        elif line[-1] and line[-2]:
            #print('Rotate Right')
            self.driveMotors(+wheel_speed,-wheel_speed)
        elif line[-2]:
            #print('Rotate slowly Right')
            self.driveMotors(+wheel_speed,0)
        elif not line[4]:
            #print('Rotate slowly Left 2')
            self.driveMotors(0,+wheel_speed)
        elif not line[2]:
            #print('Rotate slowly Right 2')
            self.driveMotors(+wheel_speed,0)
        else:
            #print('Go')
            self.driveMotors(wheel_speed,wheel_speed)

    def detect_cross_roads(self):
        line = [x == '1' for x in self.measures.lineSensor]
        cross_roads = []
        if sum(line[:3]) == 3:
            #rotate left
            cross_roads.append('l')
        if sum(line[4:]) == 3:
            #rotate right
            cross_roads.append('r')
       
        return cross_roads

    def rotate(self, goal):
        if self.measures.compass - goal > 0:
            self.driveMotors(+0.05, -0.05)
        else:
            self.driveMotors(-0.05, +0.05)          



class Map():
    def __init__(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        
        self.labMap = [[' '] * (CELLCOLS*2-1) for i in range(CELLROWS*2-1) ]
        i=1
        for child in root.iter('Row'):
           line=child.attrib['Pattern']
           row =int(child.attrib['Pos'])
           if row % 2 == 0:  # this line defines vertical lines
               for c in range(len(line)):
                   if (c+1) % 3 == 0:
                       if line[c] == '|':
                           self.labMap[row][(c+1)//3*2-1]='|'
                       else:
                           None
           else:  # this line defines horizontal lines
               for c in range(len(line)):
                   if c % 3 == 0:
                       if line[c] == '-':
                           self.labMap[row][c//3*2]='-'
                       else:
                           None
               
           i=i+1


rob_name = "C2Rob"
host = "localhost"
pos = 1
mapc = None

for i in range(1, len(sys.argv),2):
    if (sys.argv[i] == "--host" or sys.argv[i] == "-h") and i != len(sys.argv) - 1:
        host = sys.argv[i + 1]
    elif (sys.argv[i] == "--pos" or sys.argv[i] == "-p") and i != len(sys.argv) - 1:
        pos = int(sys.argv[i + 1])
    elif (sys.argv[i] == "--robname" or sys.argv[i] == "-r") and i != len(sys.argv) - 1:
        rob_name = sys.argv[i + 1]
    elif (sys.argv[i] == "--map" or sys.argv[i] == "-m") and i != len(sys.argv) - 1:
        mapc = Map(sys.argv[i + 1])
    else:
        print("Unkown argument", sys.argv[i])
        quit()

if __name__ == '__main__':
    #sys.stdout = open("debug.txt", "w")
    rob=MyRob(rob_name,pos,[0.0,60.0,-60.0,180.0],host)
    if mapc != None:
        rob.setMap(mapc.labMap)
        rob.printMap()
    
    rob.run()
