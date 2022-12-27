
import sys
from croblink import *
from math import *
import xml.etree.ElementTree as ET
import time
import locator
from lineSensor import LineSensor

from worldmap import WorldMap

CELLROWS=7
CELLCOLS=14

class MyRob(CRobLinkAngs):
    def __init__(self, rob_name, rob_id, angles, host):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)
        self.direction = 0 # Right
        self.map = WorldMap(rob_name)
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
        self.intersections = []
        self.readSensors()
        self.init_pos = (self.measures.x, self.measures.y)
        self.linesensor : list[LineSensor] = []
        self.finish_flag = False

        self.just_rotated = False

        direction = None

        while True:
            self.readSensors()
            #print(self.measures.time, self.simTime, self.measures.time == self.simTime)
            if int(self.measures.time) == int(self.simTime):
                print(self.robName + " exiting")
                print(self.measures.time)
                print(self.simTime)
                print(self.map.graph.get_beacons())
                #self.map.print_beacons()
                self.map.print_output_map()
                self.finish()
                quit()


            # Robot exiting
            if state == "finish":
                print(self.robName + " exiting")
                print(self.measures.time)
                print(self.simTime)
                print(self.map.graph.get_beacons())
                #self.map.print_beacons()
                self.map.print_output_map()
                self.finish()
                quit()

            # Robot starts challenge
            elif state == 'stop' and self.measures.start:
                print("STATE: start challenge")
                
                self.path = []
                
                # Set up the line sensor
                self.init_line_sensor()

                # Check if starting node has a beacon, if so, mark it
                if self.measures.ground != -1:
                    self.map.graph.get_node("24:10").beacon = self.measures.ground
                
                # Get our current (absolute) orientation
                curr_orientation = None
                if -5 < self.measures.compass < 5: curr_orientation = 0 # right
                elif 85 < self.measures.compass < 95: curr_orientation = 90 # up
                elif 175 < abs(self.measures.compass) <= 180: curr_orientation = 180 #left
                elif -95 < self.measures.compass < -85: curr_orientation= -90 #down

                # Compute line coordinates
                line_x = round(self.locator.x + 0.3*cos(self.measures.compass*pi/180), 2)
                line_y = round(self.locator.y + 0.3*sin(self.measures.compass*pi/180), 2)

                cur_x = round(line_x)
                cur_y = round(line_y)

                print(f"Pos: Line({line_x}, {line_y}), Robot({cur_x}, {cur_y}), Locator({self.locator.x}, {self.locator.y}), Compass({self.measures.compass})")

                # Robot is minimally aligned with the line
                if curr_orientation is not None:
                    # Detect roads (forward, backwards, right or left)
                    cross_roads = self.detect_cross_roads() 
                    print(f"{cross_roads = }")
                    for road in cross_roads:
                        # if road == 0 and not self.between((self.locator.x-0.1, self.locator.y-0.1), cur_coords, line_coords, self.measures.compass):
                        #     continue
                        self.map.add_intersect2(curr_orientation, road, cur_x, cur_y) # Add detected intersections

                state = stopped_state # Go to seek stub
                self.map.print_to_file() # Update map file
                #print("END STATE: start challenge")

            elif state != 'stop' and self.measures.stop:
                stopped_state = state
                state = 'stop'

            elif state == "seek_stub":
                #print("STATE: Seeking a stub")
                state = self.seek_stub()
                #print("END STATE: Seeking a stub")

            elif state == "move_to":
                #print("STATE: Move to...")
                #print(f"Path: {[x.id for x in self.path]}")

                gps_x, gps_y = self.measures.x - self.init_pos[0] + 24, self.measures.y - self.init_pos[1] + 10
                print(f"\tGPS: ({gps_x}, {gps_y}), Error: ({gps_x-self.locator.x},{gps_y-self.locator.y})")
                print(f"\tLocator({self.locator.x},{self.locator.y})\n\tLine({round(line_x,1)}, {round(line_y,1)}), \n\tCompass({self.measures.compass})")
                
                # Target coordinates
                tar_x = self.target.x
                tar_y = self.target.y

                #print(f"Target: ({tar_x},{tar_y})")

                # Our current coordinates
                cur_x = self.locator.x
                cur_y = self.locator.y

                #print(f"Current Position: ({cur_x},{cur_y})")
                if abs(cur_x-tar_x) < 0.05 and abs(cur_y-tar_y) < 0.05:
                    print(f"Target hit: ({tar_x}, {tar_y})")
                    if (tar_x,tar_y) == (24,10) and self.finish_flag:
                        self.map.print_output_map()
                        self.map.print_beacons()
                        self.finish()
                        state = "finish"
                        continue
                    print(f"\t{self.locator.x}, {self.locator.y}")
                    self.path.pop(0)
                    self.map.add_pos(tar_x, tar_y) # add target to map

                    if self.measures.ground != -1: # check if target has beacon
                        print("NEW BEACON:", tar_x, tar_y, self.measures.ground)
                        self.map.graph.get_node(f"{tar_x}:{tar_y}").beacon = self.measures.ground

                    self.map.print_to_file() # Update map

                    if not self.path: # Path has ended
                        state = "seek_stub" # Seek a new stub
                        print("Path done, seeking new stub...")
                        self.driveMotors(0,0) # Break
                        continue
                    
                    # Path has not yet ended, moving on to new target
                    self.target = self.path[0] 
                    tar_x = self.target.x
                    tar_y = self.target.y
                    print(f"New Target: ({tar_x},{tar_y})")
                    print(f"Path: {[x.id for x in self.path]}")

                    diff_x = cur_x - tar_x # Manhattam distance (x coord)
                    diff_y = cur_y - tar_y # Manhattam distance (y coord)

                    if abs(diff_x) > abs(diff_y): # move in x axis
                        diff = diff_x
                    else: # move in y axis
                        diff = diff_y
                    

                # Not yet at our target
                diff = 0
                breaker = 0
                direction = 0

                diff_x = cur_x - tar_x # Manhattam distance (x coord)
                diff_y = cur_y - tar_y # Manhattam distance (y coord)

                if abs(diff_x) > abs(diff_y): # move in x axis
                    diff = diff_x
                    direction = 0 if diff_x < 0 else 180 # choose orientation in which to move
                else: # move in y axis
                    diff = diff_y
                    direction = 90 if diff_y < 0 else -90


                #breaker = 0.05 if 0 <= abs(diff) < 0.2 else 0.025 if abs(diff) < 0.4 else 0 # determine how hard we should set our breaks to
                breaker = round(0.05*e**(-abs(diff)),2)  if abs(diff) <= 0.5 else 0


                self.detect_intersection2()
                self.move(direction, breaker) # movement...
                self.map.print_to_file()

                #print("END STATE: Move to...")

            elif state == 'wander':
                self.wander()

    def move(self, direction, breaker):
        print("Moving...")
        cur_direction = self.measures.compass # our direction (may not match desired direction)  
        diff = (cur_direction-direction)*pi/180 # difference in directions in radians

        if abs(sin(diff)) > sin(5 * pi/180) or cos(diff) < 0:
            for sensor in self.linesensor:
                sensor.clear_state()

            mod = 1 if sin(diff) > 0 else -1
            acc = 0.05 if cos(diff) <= 0 else abs(sin(diff))/20
            power = 0.05 + acc
            self.driveMotors(power*mod, power*-mod)
            self.locator.update(power*mod, power*-mod, cur_direction)

            self.just_rotated = True #4 if self.just_rotated > 1 else self.just_rotated + 1
            print(f"\tRotate: {power*mod}, {power*-mod}")
        
        else:
            BASESPEED = 0.075
            mod = 0,0#(abs(sin(diff))/3, 0) if sin(diff) > 0 else (0, abs(sin(diff))/3) if sin(diff) < 0 else (0, 0)

            line = [x == '1' for x in self.measures.lineSensor]

            mod2 = 0.03 * (not line[2]), 0.03 * (not line[4])
            motor = BASESPEED - breaker + mod[0] + mod2[0], BASESPEED - breaker + mod[1] + mod2[1]

            self.driveMotors(motor[0], motor[1])
            self.locator.update(motor[0], motor[1], cur_direction)   

            self.just_rotated = False #0  if self.just_rotated < 1 else self.just_rotated - 2 
            print(f"\tMove: {motor[0]}, {motor[1]}")  
            print(f"\t\t{breaker = }")
            print(f"\t\t{mod = }")
            print(f"\t\t{mod2 = }")   

        for sensor in self.linesensor:
            sensor.move(self.locator)

    def between(self, border1, target, border2, orientation): # orientation -> abs orientation, target -> coordinates we're evalutaing
        idx = int(abs(sin(orientation * pi/180))) # vertical (y, 1) or horizontal (x, 0) orientation?

        return border1[idx] < round(target[idx],1) < border2[idx] or border1[idx] > round(target[idx],1) > border2[idx] # check if target is between the line

    def after(self, border1, target, border2, orientation):
        idx = int(abs(sin(orientation * pi/180)))

        return border1[idx] < round(target[idx],1) if orientation in [0, 90] else border2[idx] > round(target[idx],1) # check if target is after the line

    def detect_intersection2(self): # Detect current intersecting roads
        cross_roads = self.detect_cross_roads() # Detect roads to the left, right or forward

        # Check if lined up minimally with for intersection detection
        curr_orientation = None
        if -10 <= self.measures.compass <= 10: curr_orientation = 0 # right
        elif 80 <= self.measures.compass <= 100: curr_orientation = 90 # up
        elif 170 <= abs(self.measures.compass) <= 180: curr_orientation = 180 #left
        elif -100 <= self.measures.compass <= -80: curr_orientation= -90 #down

        if curr_orientation is None or self.just_rotated: # Not lined up, we won't detect intersections...
            return

        #print("Checking for intersections...")

        # line sensor offset = 0.438
        # line thickness = 0.2

        # Position of the line sensor
        line_x = round(self.locator.x + 0.438*cos(self.measures.compass*pi/180), 3)
        line_y = round(self.locator.y + 0.438*sin(self.measures.compass*pi/180), 3)

        line_coords = (line_x, line_y)

        cur_x = round(line_x)
        cur_y = round(line_y)

        mod_x = mod_y = 0

        if abs(self.locator.x - self.target.x) > 2:
            mod_x = floor(abs(self.locator.x - self.target.x))//2 * 2*cos(curr_orientation*pi/180)

        if abs(self.locator.y - self.target.y) > 2:
            mod_y = floor(abs(self.locator.y - self.target.y))//2 * 2*sin(curr_orientation*pi/180)


        border1 = (
            self.target.x + 0.2 - mod_x, 
            self.target.y + 0.2 - mod_y
        ) # positive borders

        border2 = (
            self.target.x - 0.2 - mod_x, 
            self.target.y - 0.2 - mod_y
        ) # negative borders

        print(f"\tOrientation({curr_orientation})")
        print(f"\t{border1 = }")
        print(f"\t{border2 = }")
        print(f"\tTarget: {self.target}")
        print(f"\tMod: {mod_x}, {mod_y}")

        roads = [0, 0]
        line = []

        for sensor in self.linesensor:
            if not sensor.get_state(): # sensor not active
                if sensor.road == 0:
                    roads = [road-1 for road in roads]
                continue

            if sensor.road in [-90, 90]:
                roads[sensor.road > 0] += 1

            line.append(sensor.get_state())

        idx = int(abs(sin(curr_orientation * pi/180)))
        sensor = self.linesensor[3]
        wrong = (sensor.x,sensor.y)
        if not sum(line) == 0 and not sensor.get_state():
            border = None
            # No Left
            if self.linesensor[2].get_state():
                # Positive Border
                if curr_orientation in [90, 180]:
                    border = +0.1
                # Negative border
                elif curr_orientation in [0, -90]:
                    border = -0.1
            # No Right
            elif self.linesensor[4].get_state():
                if curr_orientation in [90, 180]:
                    border = -0.1
                elif curr_orientation in [0, -90]:
                    border = +0.1
            if border:
                if not idx:
                    self.locator.y = round(self.locator.y) + border
                else:
                    self.locator.x = round(self.locator.x) + border

            print(f"UPDATE LOCATOR2: ({self.locator.x}, {self.locator.y}), Sensor: ({sensor.x},{sensor.y},{sensor.id}), B4 Update: {wrong}")

        for road_idx in [0,1]: # left, right
            if roads[road_idx] > 2:
                sensor = self.linesensor[0 if not road_idx else 6] # the tips
                # side sensors are active but not between the line, adjust the location
                if not self.between(border1=border1, target=(sensor.x, sensor.y), border2=border2, orientation=curr_orientation):
                    closest = border1 if abs(border1[idx]-line_coords[idx]) < abs(border2[idx]-line_coords[idx]) else border2

                    wrong = (sensor.x,sensor.y)

                    if idx: # vertical, y
                        dist = sensor.y-closest[1] 
                        self.locator.y -= dist
                    else: # horizontal, x
                        dist = sensor.x-closest[0]
                        self.locator.x -= dist
                    
                    cur_x = round(self.locator.x)
                    cur_y = round(self.locator.y)

                    for sensor in self.linesensor: sensor.move(self.locator)

                    print(f"UPDATE LOCATOR: ({self.locator.x}, {self.locator.y}), Sensor: ({sensor.x},{sensor.y},{sensor.id}), B4 Update: {wrong}")

                    line_coords = (line_x, line_y)

                print("Intersection to the side!")
                self.map.add_intersect2(curr_orientation, [-90, 90][road_idx], cur_x, cur_y)
                for sensor in self.linesensor: sensor.clear_state()

        # forward sensor is active and after the line
        if self.linesensor[3].get_state() and self.after(border1=border1, target=(self.linesensor[3].x, self.linesensor[3].y), border2=border2, orientation=curr_orientation):
            #print("Intersection Forward!")
            self.map.add_intersect2(curr_orientation, sensor.road, cur_x, cur_y)

        print("End checking for intersections.")

    def detect_cross_roads(self): # Detect roads to the left, right or forward, TODO use line sensor mechanics?
        # Current Line
        line = [x == '1' for x in self.measures.lineSensor]
        updated_line = []

        # Update LineSensor class
        for sensor in self.linesensor:
            sensor.move(self.locator)
            sensor.update(line[sensor.id])
            updated_line.append(sensor.get_state())
            
        #self.line_history = self.line_history[1:] + line
        cross_roads = []
        print(f"{updated_line = }")
        print(f"{self.linesensor = }")
        #print(line)
        if sum(line[:4]) > 3:
            #rotate left
            cross_roads.append(-90)
        if sum(line[3:]) > 3:
            #rotate right
            cross_roads.append(90)
        if sum(line[2:5]) > 1:
            # path ahead
            cross_roads.append(0)
        if sum(line[2:5]) == 0:
            cross_roads.append(-180)
       
        return cross_roads

    def seek_stub(self):
        self.stubs = self.map.get_stubs(self.measures.compass) # get map stubs
        print(f"STUBS: {self.stubs}")

        if not self.stubs: # No stubs left, the map has been fully explored
            self.curr_stub = (24, 10)
            self.finish_flag = True
        else:
            self.curr_stub = self.stubs.pop(0) # Get best stub to follow
        
        print(f"New stub: {self.curr_stub}, Current position: {self.map.curr_pos}")
        pos = self.map.curr_pos
        
        node1 = self.map.graph.get_node(f"{pos[0]}:{pos[1]}")
        node2 = self.map.graph.get_node(f"{self.curr_stub[0]}:{self.curr_stub[1]}")

        self.path = self.map.graph.shortest_path(node1, node2)[::2] # Get shortest path to get to stub

        # Compress path
        #
        # (0,0), (2,0), (4,0), (4,2), (6,2), (8,2)
        #  -->
        # (4,0), (4,2), (8,2)
        #
        # if len(self.path) > 2:
        #     x_diff = y_diff = True
        #     tmp_path =  [self.path[0]]
        #     for i in range(1, len(self.path)):
        #         if x_diff and tmp_path[-1].x - self.path[i].x != 0:
        #             y_diff = False
        #             tmp_path[-1] = self.path[i]
        #         if y_diff and tmp_path[-1].y - self.path[i].y != 0:
        #             x_diff = False
        #             tmp_path[-1] = self.path[i]
        #         else:
        #             tmp_path.append(self.path[i])
        #             x_diff = not x_diff
        #             y_diff = not y_diff

        #     print(f"Old Path: {self.path}")
        #     print(f"New Path: {tmp_path}")
        #     self.path = tmp_path
        # else:
        self.path = self.path[1:]

        print(f"Path: {[x.id for x in self.path]}")
        
        self.target = self.path[0] # Next (immediate) target
        print(f"Target: {self.target}")

        return "move_to" # New state

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

    def init_line_sensor(self):
        oposit = [0.24, 0.16, 0.8, 0, 0.8, 0.16, 0.24]
        ctr = 0
        roads = [-90, -90, -90, 0, 90, 90, 90]
        for o in oposit:
            h = sqrt(o**2 + 0.438**2)
            ang = atan(o/0.438)
            ang = ang if ctr < 3 else -ang
            self.linesensor.append(LineSensor(ctr, self.locator.x, self.locator.y, ang, h, roads[ctr]))
            #print(f"INIT LINE: {ctr}, {ang}, {h}")
            ctr += 1

    def get_line_sensor_majority(self):
        pass

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
    elif (sys.argv[i] == "--debug" or sys.argv[i] == "-d") and i != len(sys.argv) - 1:
        sys.stdout = open(sys.argv[i + 1], "w")
    else:
        print("Unkown argument", sys.argv[i])
        quit()

if __name__ == '__main__':

    # sys.stdout = open("debug.txt", "w")
    rob=MyRob(rob_name,pos,[0.0,60.0,-60.0,180.0],host)
    if mapc != None:
        rob.setMap(mapc.labMap)
        rob.printMap()
    
    rob.run()
