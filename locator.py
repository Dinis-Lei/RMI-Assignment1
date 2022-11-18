from math import sin, cos

class Locator:
    

    def __init__(self ,x=0, y=0) -> None:
        self.x = x
        self.y = y
        self.rot = 0
        self.out_r = 0
        self.out_l = 0



    def update(self, ml, mr):
        
        new_out_r = (mr + self.out_r)/2
        new_out_l = (ml + self.out_l)/2


        lin = (new_out_r+new_out_l)/2
        new_x = self.x + lin * cos(self.rot)
        new_y = self.y + lin * sin(self.rot)

        rot_mod = new_out_r - new_out_l
        rot = self.rot + rot_mod

        self.x = round(new_x, 2)
        self.y = round(new_y, 2)
        self.rot = rot
        self.out_r = new_out_r
        self.out_l = new_out_l

        return self.x, self.y, self.rot

    def __str__(self) -> str:
        return f"({self.x}, {self.y}) : {self.rot}"