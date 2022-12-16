from math import sin, cos, pi

class Locator:
    

    def __init__(self ,x=0, y=0) -> None:
        self.x = x
        self.y = y
        self.rot = 0
        self.out_r = 0
        self.out_l = 0
        #self.line_x = x + 0.3
        #self.line_y = y + 0



    def update(self, ml, mr, compass=None):
        
        new_out_r = (mr + self.out_r)/2
        new_out_l = (ml + self.out_l)/2


        lin = (new_out_r+new_out_l)/2
        
        mod_x = lin * cos(self.rot)
        mod_y = lin * sin(self.rot)

        new_x = self.x + mod_x
        new_y = self.y + mod_y

        # if compass:
        #     self.rot = compass

        #new_line_x = self.line_x + mod_x
        #new_line_y = self.line_y + mod_y

        rot_mod = new_out_r - new_out_l
        rot = self.rot + rot_mod

        self.x = new_x
        self.y = new_y
        #self.line_x = round(new_line_x, 2)
        #self.line_y = round(new_line_y, 2)
        self.rot = rot if not compass else compass*pi/180
        self.out_r = new_out_r
        self.out_l = new_out_l

        #print(f"Rot: {self.rot}")

        return self.x, self.y, self.rot

    def __str__(self) -> str:
        return f"({self.x}, {self.y}) : {self.rot}"