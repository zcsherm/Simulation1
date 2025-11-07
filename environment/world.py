HEIGHT = 30
WIDTH = 30
CELLS = HEIGHT * WIDTH
DIRECTIONS =[(1,0),(0,1),(-1,0),(0,-1)]


class World:
    
    def __init__(self, height=HEIGHT, width=WIDTH):
        self._height = height
        self._width = width
        self._cells = height * width
        self._grid = []
        for i in range(height):
            row = []
            for j in range(width):
                row.append(Cell(self, (i, j)))
            self._grid.append(row)
        self.seed_cells()
        self.print_grid()
                    
    def progress_sim(self):
        for i in range(self._height):
            for j in range(self._width):
                occupant = self._grid[i][j].get_occupant()
                food = occupant = self._grid[i][j].get_food()
                if occupant is not None:
                    pass
                if food is not None:
                    pass

    def print_grid(self):
        for row in self._grid:
            print_row = []
            for cell in row:
                space = ' '
                food = cell.get_food
                occupant = cell.get_occupant()
                if food:
                    space = 'O' 
                if occupant:
                    space = 'X'
                print_row.append(space)
            print(print_row)
            
    def forward_step(self):
        self.progress_sim()
        self.print_grid()

    def handle_choice(self, occupant, choice):
        cell = occupant.get_cell()
        coords = cell.get_coords()
            
class Cell:
    def __init__(self, grid, coords):
        self._occupant = None
        self._food = None
        self._grid = grid
        self._coords = coords

    def set_occupant(self, occupant):
        self._occupant = occupant

    def set_food(self, food):
        self._food = food

    def get_occupant(self):
        return self._occupant

    def get_food(self):
        return self._food

    def get_coords(self):
        return self._coords
        
