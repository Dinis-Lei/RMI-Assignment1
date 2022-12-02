
import sys
from croblink import *
from math import *
import xml.etree.ElementTree as ET
import time
import locator

from worldmap import WorldMap

CELLROWS=7
CELLCOLS=14

class MyRob(CRobLinkAngs):
    def __init__(self, rob_name, rob_id, angles, host):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)
        self.direction = 0 # Right
        self.map = WorldMap()
        self.map.map_output = "map4.txt"
        self.line_history = [[0 for _ in range(7)] for _ in range(3)]


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
        stopped_state = 'seek_stub'

        self.init_pos = None
        self.locator = locator.Locator(24, 10)
        prev_loc = None
        self.intersections = []
        direction = None
        count = 0
        wanted_rotation = 0
        stub_seeking = False
        curr_stub = None
        path = []
        flg = False
        while True:
            self.readSensors()

            if self.measures.endLed:
                print(self.robName + " exiting")
                print(self.measures.time)
                print(self.simTime)
                quit()

            if not self.init_pos:
                self.init_pos = (self.measures.x, self.measures.y)


            if state == 'stop' and self.measures.start:
                if self.measures.beacon != -1:
                    self.map.graph.get_node("24:10").has_beacon = self.measures.beacon
                
                curr_orientation = None
                if -5 < self.measures.compass < 5: curr_orientation = 0 # right
                elif 85 < self.measures.compass < 95: curr_orientation = 90 # up
                elif 175 < abs(self.measures.compass) <= 180: curr_orientation = 180 #left
                elif -95 < self.measures.compass < -85: curr_orientation= -90 #down


                line_x = round(self.locator.x + 0.3*cos(self.measures.compass*pi/180), 2)
                line_y = round(self.locator.y + 0.3*sin(self.measures.compass*pi/180), 2)

                line_coords = (line_x, line_y)

                cur_x = round(line_x)
                cur_y = round(line_y)

                cur_coords = (cur_x, cur_y)

                print(f"Pos: ({line_x}, {line_y}), ({cur_x}, {cur_y}), ({self.locator.x}, {self.locator.y}), {self.measures.compass}")

                if curr_orientation is not None:
                    cross_roads = self.detect_cross_roads2()
                    print(cross_roads)
                    for road in cross_roads:
                        if road == 0 and not self.between((self.locator.x-0.1, self.locator.y-0.1), cur_coords, line_coords, self.measures.compass):
                            continue
                        self.map.add_intersect2(curr_orientation, road, cur_x, cur_y)

                state = stopped_state
                self.map.print_to_file()

            if state != 'stop' and self.measures.stop:
                stopped_state = state
                state = 'stop'
            elif state == "seek_stub":
                state = self.seek_stub()
            elif state == "move_to":
                # print(self.locator)


                tar_x = self.target.x
                tar_y = self.target.y

                cur_x = self.locator.x
                cur_y = self.locator.y

                if abs(cur_x-tar_x) < 0.05 and abs(cur_y-tar_y) < 0.05:
                    print("TARGET HIT")
                    self.map.add_pos(tar_x, tar_y)

                    if self.measures.ground != -1:
                        print("----BEACON----", tar_x, tar_y, self.measures.ground)
                        self.map.graph.get_node(f"{tar_x}:{tar_y}").has_beacon = True
                        # if len(self.map.graph.get_beacons()) >= int(self.nBeacons):
                        #     self.map.change_sort()
                    # if len(self.map.graph.get_beacons()) >= int(self.nBeacons):
                    # self.map.graph.spbb()
                        # beacons = self.map.graph.get_beacons()
                        # for beacon in beacons:
                        #     print(f"{beacon.id}")
                        #     for b2 in beacon.sptb:
                        #         print(f"-- {b2}: {[n.id for n in beacon.sptb[b2]]}")

                    while self.intersections: 
                        intersect = self.intersections.pop()
                        print("Intersect:", intersect)
                        if not (abs(intersect[2] - tar_x) >= 1 or abs(intersect[3] - tar_y) >= 1):
                            self.map.add_intersect(intersect[0],intersect[1]) 

                    self.map.print_to_file()

                    if not path:
                        # found path
                        state = "seek_stub"
                        print("DONE")
                        self.driveMotors(0,0)
                        continue
                        
                    self.target = path.pop(0)
                    tar_x = self.target.x
                    tar_y = self.target.y


                diff = 0
                breaker = 0
                direction = 0

                diff_x = cur_x - tar_x
                diff_y = cur_y - tar_y

                if abs(diff_x) > abs(diff_y):
                    diff = diff_x
                    direction = 0 if diff_x < 0 else 180
                else:
                    diff = diff_y
                    direction = 90 if diff_y < 0 else -90

                breaker = 0.06 if 0 <= abs(diff) < 0.2 else 0.03 if abs(diff) < 0.4 else 0

                self.move(direction, breaker)
                self.detect_intersection2()
                self.map.print_to_file()


            elif state == 'wander':
                self.wander()

    def move(self, direction, breaker):
        cur_direction = self.measures.compass   
        diff = (cur_direction-direction)*pi/180
        #print(f"{cur_direction}, {direction}, {breaker}, {diff}")
        if abs(sin(diff)) > sin(5 * pi/180) or cos(diff) < 0:
            mod = 1 if sin(diff) > 0 else -1
            acc = 0.05 if cos(diff) <= 0 else abs(sin(diff))/20
            power = 0.05 + acc
            self.driveMotors(power*mod, power*-mod)
            self.locator.update(power*mod, power*-mod)
        else:
            mod = (abs(sin(diff))/10,0) if sin(diff) > 0 else (0,abs(sin(diff))/10) if sin(diff) < 0 else (0,0)
            self.driveMotors(0.1 - breaker + mod[0], 0.1 - breaker + mod[1])
            self.locator.update(0.1 - breaker + mod[0], 0.1 - breaker + mod[1])

    def between(self, border1, target, border2, orientation):
        if not ( abs(sin(orientation*pi/180)) < sin(5 * pi/180) or abs(cos(orientation*pi/180)) < cos(5 * pi/180)):
            return False

        idx = 0 if abs(sin(orientation * pi/180)) < sin(5 * pi/180) else 1

        return border1[idx] < target[idx] < border2[idx] or border1[idx] > target[idx] > border2[idx]

    def detect_intersection2(self):
        curr_orientation = None
        if -5 <= self.measures.compass <= 5: curr_orientation = 0 # right
        elif 85 <= self.measures.compass <= 95: curr_orientation = 90 # up
        elif 175 <= abs(self.measures.compass) <= 180: curr_orientation = 180 #left
        elif -95 <= self.measures.compass <= -85: curr_orientation= -90 #down


        line_x = round(self.locator.x + 0.4*cos(self.measures.compass*pi/180), 2)
        line_y = round(self.locator.y + 0.4*sin(self.measures.compass*pi/180), 2)

        line_coords = (line_x, line_y)

        cur_x = round(line_x)
        cur_y = round(line_y)

        cur_coords = (cur_x + 0.2*cos(self.measures.compass*pi/180), cur_y + 0.2*sin(self.measures.compass*pi/180))

        print(f"GPS: ({self.measures.x - self.init_pos[0] + 24}, {self.measures.y - self.init_pos[1] + 10})")
        print(f"Pos: ({line_x}, {line_y}), ({cur_x}, {cur_y}), ({self.locator.x}, {self.locator.y}), {self.measures.compass}")

        if curr_orientation is not None:
            cross_roads = self.detect_cross_roads2()
            print(cross_roads)
            for road in cross_roads:
                if road == 0 and not self.between((self.locator.x, self.locator.y), cur_coords, line_coords, self.measures.compass):
                    continue
                self.map.add_intersect2(curr_orientation, road, cur_x, cur_y)

    def detect_cross_roads2(self):
        line = [x == '1' for x in self.measures.lineSensor]
        #self.line_history = self.line_history[1:] + line
        cross_roads = []
        print(line)
        if sum(line[:4]) > 3:
            #rotate left
            cross_roads.append(-90)
        if sum(line[3:]) > 3:
            #rotate right
            cross_roads.append(90)
        if sum(line[2:5]) > 1:
            # path ahead
            cross_roads.append(0)
       
        return cross_roads

    def detect_intersection(self):
        curr_orientation = None
        if -5 <= self.measures.compass <= 5: curr_orientation = 'r' # right
        elif 85 <= self.measures.compass <= 95: curr_orientation = 'u' # up
        elif 175 <= abs(self.measures.compass) <= 180: curr_orientation = 'l' #left
        elif -95 <= self.measures.compass <= -85: curr_orientation= 'd' #down

        cur_x = self.locator.x
        cur_y = self.locator.y

        if curr_orientation:
            cross_roads = self.detect_cross_roads()
            # print(cross_roads)
            if 'l' in cross_roads: # relative to the robot orientation
                self.intersections.append((curr_orientation,'l',cur_x, cur_y, self.measures.lineSensor, self.measures.compass))
                # self.map.add_intersect(curr_orientation, 'l')
            if 'r' in  cross_roads:
                self.intersections.append((curr_orientation,'r',cur_x, cur_y, self.measures.lineSensor, self.measures.compass))
            if 's' in cross_roads:
                # print(cur_x, cur_y)
                if curr_orientation == 'r' and 2 >= cur_x%2 > 1.8:
                    self.intersections.append((curr_orientation,'s',cur_x, cur_y, self.measures.lineSensor, self.measures.compass))
                elif curr_orientation == 'l' and 0 <= cur_x%2 < 0.2:
                    self.intersections.append((curr_orientation,'s',cur_x, cur_y, self.measures.lineSensor, self.measures.compass))
                elif curr_orientation == 'u' and 2 >= cur_y%2 > 1.8:
                    self.intersections.append((curr_orientation,'s',cur_x, cur_y, self.measures.lineSensor, self.measures.compass))
                elif curr_orientation == 'd' and 0 <= cur_y%2 < 0.2:
                    self.intersections.append((curr_orientation,'s',cur_x, cur_y, self.measures.lineSensor, self.measures.compass))

    def detect_cross_roads(self):
        line = [x == '1' for x in self.measures.lineSensor]
        #self.line_history = self.line_history[1:] + line
        cross_roads = []
        #print(line)
        if sum(line[:4]) >= 3:
            #rotate left
            cross_roads.append('l')
        if sum(line[3:]) >= 3:
            #rotate right
            cross_roads.append('r')
        if sum(line[2:5]) > 1:
            # path ahead
            cross_roads.append('s')
       
        return cross_roads


    def seek_stub(self):
        print("SEEK STUB")
        # for node in self.map.graph.nodes:
        #     print(self.map.graph.nodes[node])

        self.stubs = self.map.get_stubs()

        if not self.stubs:
            state = "finish"
            #self.map.print_beacons()
            self.finish()
            return "finish"

        self.curr_stub = self.stubs.pop(0)
        print(self.curr_stub, self.map.curr_pos)
        pos = self.map.curr_pos
        
        node1 = self.map.graph.get_node(f"{pos[0]}:{pos[1]}")
        node2 = self.map.graph.get_node(f"{self.curr_stub[0]}:{self.curr_stub[1]}")

        path = self.map.graph.shortest_path(node1, node2)[1:]
        print(f"Path: {[x.id for x in path]}")
        self.target = path.pop(0)
        return "move_to"


    def wander(self):
        center_id = 0
        left_id = 1
        right_id = 2
        back_id = 3

        wheel_speed = 0.1

        line = [x == '1' for x in self.measures.lineSensor]

        #print(self.measures.time , line)

        if sum(line[0:3]) > sum(line[-3:]):
            line[-3:] = [0,0,0]
        elif sum(line[0:3]) < sum(line[-3:]):
            line[0:3] = [0,0,0]

        #print(line)

        if line[0] and line[1]:
            print('Rotate Left')
            self.driveMotors(-wheel_speed,+wheel_speed)
            self.locator.update(-wheel_speed,+wheel_speed)
        elif line[1]:
            print('Rotate slowly Left')
            self.driveMotors(0,+wheel_speed)
            self.locator.update(0,+wheel_speed)
        elif line[-1] and line[-2]:
            print('Rotate Right')
            self.driveMotors(+wheel_speed,-wheel_speed)
            self.locator.update(+wheel_speed,-wheel_speed)
        elif line[-2]:
            print('Rotate slowly Right')
            self.driveMotors(+wheel_speed,0)
            self.locator.update(+wheel_speed,0)
        # elif line[0]:
        #     print('Rotate slowly Left 3')
        #     self.driveMotors(0,+0.15)
        # elif line[-1]:
        #     print('Rotate slowly Right 3')
        #     self.driveMotors(+0.15,0)
        elif not line[4]:
            print('Rotate slowly Left 2')
            self.driveMotors(0,+wheel_speed)
            self.locator.update(0,+wheel_speed)
        elif not line[2]:
            print('Rotate slowly Right 2')
            self.driveMotors(+wheel_speed,0)
            self.locator.update(+wheel_speed,0)
        else:
            print('Go')
            self.driveMotors(wheel_speed,wheel_speed)
            self.locator.update(wheel_speed,wheel_speed)

        print(self.locator)
        print(self.measures.x - self.init_pos[0], self.measures.y - self.init_pos[1], self.measures.compass)


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


rob_name = "C4Rob"
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
