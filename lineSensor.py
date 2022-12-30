from math import sin, cos, pi
from locator import Locator

class LineSensor:

    def __init__(self, _id, x, y, ang, dist, road) -> None:
        self.x = x
        self.y = y
        self.id = _id
        self.ang = ang
        self.dist = dist
        self.state = []
        self.road = road

    def move(self, locator: Locator):
        self.x = round(locator.x + self.dist*cos(self.ang*pi/180+locator.rot), 3)
        self.y = round(locator.y + self.dist*sin(self.ang*pi/180+locator.rot), 3)

    def update(self, state):
        if len(self.state) > 2:
            self.state = self.state[1:]
        self.state += [state]

    def between(self):
        if int(self.x)%2 == 0:
            return self.y%1 < 0.2 or self.y%1 > 0.8 
        elif int(self.y)%2 == 0:
            return self.x%1 < 0.2 or self.x%1 > 0.8 
        else:
            return False
            

    def get_state(self):
        return sum(self.state) > (len(self.state)//2)

    def clear_state(self):
        self.state = []

    def __str__(self) -> str:
        return f"{self.state}"

    def __repr__(self) -> str:
        return f"{self.state}"