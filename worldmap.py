


class WorldMap():

    def __init__(self) -> None:
        self.grid = [[' ' for i in range(49) ] for j in range(21)]
        self.curr_pos = (24,10)
        self.grid[self.curr_pos[1]][self.curr_pos[0]] = '*'


    def add_pos(self, x, y):
        
        x = self.curr_pos[0] + x
        y = self.curr_pos[1] + y

        self.grid[y][x] = '*'

        self.curr_pos = (x, y)

    def print_map(self):
        for l in self.grid:
            for c in l:
                print(c, end='')
            print('\n')


