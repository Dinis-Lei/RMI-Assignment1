
import sys
from croblink import *
from math import *
import xml.etree.ElementTree as ET

CELLROWS=7
CELLCOLS=14

class MyRob(CRobLinkAngs):
    def __init__(self, rob_name, rob_id, angles, host):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)
        self.direction = 0 # Right


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
        direction = None
        count = 0
        wanted_rotation = 0
        while True:
            print(f"{state= }")
            self.readSensors()
            print(self.measures.dir)

            if not self.init_pos:
                self.init_pos = (self.measures.x, self.measures.y)
                prev_loc = self.init_pos

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
                cur_loc = (self.measures.x, self.measures.y)
                if (cur_loc[0] - prev_loc[0]) >= 2:
                    prev_loc = cur_loc
                    # send new info to map
                    pass
                elif (cur_loc[1] - prev_loc[1]) >= 2:
                    prev_loc = cur_loc
                    # send new info to map
                    pass

                cross_roads = self.detect_cross_roads()
                if 'left' in cross_roads:
                    # register intersection in map (to be explored later)
                    pass
                if 'right' in  cross_roads:
                    prev_loc = cur_loc
                    pass
                self.wander()
            elif state=='wait':
                prev_loc = (self.measures.x, self.measures.y)
                self.driveMotors(0.0,0.0)
                count += 1
                if count == 10:
                    state = 'detect'
                    count = 0
            elif state=='detect':
                cross_roads = self.detect_cross_roads()
                if 'left' in cross_roads:
                    state = 'rotate'
                    wanted_rotation = self.direction + 90
                elif 'right' in  cross_roads:
                    state = 'rotate'
                    wanted_rotation = self.direction - 90
                else:
                    state = 'run'
            
            elif state=='rotate':

                self.rotate(wanted_rotation)
                if self.measures.compass - wanted_rotation < 0.5:
                    state ='run'

                

            

    def wander(self):
        wheel_speed = 0.15
        line = [x == '1' for x in self.measures.lineSensor]

        # if sum(line[0:3]) > sum(line[-3:]):
        #     line[-3:] = [0,0,0]
        # elif sum(line[0:3]) < sum(line[-3:]):
        #     line[0:3] = [0,0,0]

        # print(line)

        if line[0] and line[1]:
            print('Rotate Left')
            self.driveMotors(-wheel_speed,+wheel_speed)
        elif line[1]:
            print('Rotate slowly Left')
            self.driveMotors(0,+wheel_speed)
        elif line[-1] and line[-2]:
            print('Rotate Right')
            self.driveMotors(+wheel_speed,-wheel_speed)
        elif line[-2]:
            print('Rotate slowly Right')
            self.driveMotors(+wheel_speed,0)
        elif not line[4]:
            print('Rotate slowly Left 2')
            self.driveMotors(0,+wheel_speed)
        elif not line[2]:
            print('Rotate slowly Right 2')
            self.driveMotors(+wheel_speed,0)
        else:
            print('Go')
            self.driveMotors(wheel_speed,wheel_speed)

    def detect_cross_roads(self):
        line = [x == '1' for x in self.measures.lineSensor]
        cross_roads = []
        if sum(line[:3]) == 3:
            #rotate left
            cross_roads.append("left")
        if sum(line[4:]) == 3:
            #rotate right
            cross_roads.append("right")
       
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
