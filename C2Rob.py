
import sys
from croblink import *
from math import *
import xml.etree.ElementTree as ET

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

        state = 'stop'
        stopped_state = 'run'

        self.init_pos = None
        prev_loc = None
        intersections = []
        direction = None
        count = 0
        wanted_rotation = 0
        stub_seeking = False
        curr_stub = None
        while True:
            #print(f"{state= }")
            self.readSensors()


            if not self.init_pos:
                self.init_pos = (self.measures.x, self.measures.y)
                prev_loc = list(self.init_pos)
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
                x_dif = cur_loc[0] - prev_loc[0]
                y_dif = cur_loc[1] - prev_loc[1]
                repeat = False
                if x_dif >= 2:
                    prev_loc[0] += 2
                    repeat = self.map.add_pos(2,0)
                    while intersections:
                        intersect = intersections.pop()
                        self.map.add_intersect(intersect[0],intersect[1]) 
                    #print("one to the right")
                elif x_dif <= -2:
                    prev_loc[0] -= 2
                    repeat = self.map.add_pos(-2,0)
                    while intersections:
                        intersect = intersections.pop()
                        self.map.add_intersect(intersect[0],intersect[1])
                    #print("one to the left")
                elif y_dif >= 2:
                    prev_loc[1] += 2
                    repeat = self.map.add_pos(0,-2)
                    while intersections:
                        intersect = intersections.pop()
                        self.map.add_intersect(intersect[0],intersect[1])
                    #print("one upwards")
                elif y_dif <= -2:
                    prev_loc[1] -= 2
                    repeat = self.map.add_pos(0,2)
                    while intersections:
                        intersect = intersections.pop()
                        self.map.add_intersect(intersect[0],intersect[1])
                    #print("one downwards")

                self.map.print_to_file()

                curr_orientation = None # absolute orientation
                if -5 < self.measures.compass < 5: curr_orientation = 'r' # right
                elif 85 < self.measures.compass < 95: curr_orientation = 'u' # up
                elif 175 < abs(self.measures.compass) < 180: curr_orientation = 'l' #left
                elif -95 < self.measures.compass < -85: curr_orientation= 'd' #down

                if curr_orientation:
                    cross_roads = self.detect_cross_roads()
                    if 'l' in cross_roads: # relative to the robot orientation
                        intersections.append((curr_orientation,'l'))
                    if 'r' in  cross_roads:
                        intersections.append((curr_orientation,'r'))

                stub_seeking = stub_seeking or repeat # starts stub seeking after reaching its first loop/cycle
                
                if not stub_seeking:
                    self.wander()
                else:
                    print("STUB SEEKING STARTED")
                    if not curr_stub:
                        curr_stub = self.map.get_stubs().pop() # gets closest stub so we seek it

                    # TODO get direction for the curr stub
                    # TODO follow in a straight line to closest stub until we reach its general location, rotate until aligned with the line in the
                    # unexplored direction
                    # TODO go back to simply following the line until we reach a known location again (check repreated), after that recalculate stubs and follow the next
                    # TODO quit when all stubs are gone -> map found

            # elif state=='wait':
            #     prev_loc = (self.measures.x, self.measures.y)
            #     self.driveMotors(0.0,0.0)
            #     count += 1
            #     if count == 10:
            #         state = 'detect'
            #         count = 0
            # elif state=='detect':
            #     cross_roads = self.detect_cross_roads()
            #     if 'left' in cross_roads:
            #         state = 'rotate'
            #         wanted_rotation = self.direction + 90
            #     elif 'right' in  cross_roads:
            #         state = 'rotate'
            #         wanted_rotation = self.direction - 90
            #     else:
            #         state = 'run'
            
            # elif state=='rotate':

            #     self.rotate(wanted_rotation)
            #     if self.measures.compass - wanted_rotation < 0.5:
            #         state ='run'

                

            

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
