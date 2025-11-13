from actions import *
HEIGHT = 30
WIDTH = 30
CELLS = HEIGHT * WIDTH
DIRECTIONS =[(1,0),(0,1),(-1,0),(0,-1)]
ACTIONS = ["Left Turn", "Right Turn", "Move Forward", "Do Nothing"]

class World:
    
    def __init__(self, height=HEIGHT, width=WIDTH):
        # Establish a grid of cells
        self._height = height
        self._width = width
        self._cells = height * width
        self._grid = []
        self._organism_death = False
        self._iterations = 0
        for i in range(height):
            row = []
            for j in range(width):
                row.append(Cell(self, (i, j)))
            self._grid.append(row)

        # seed environment with food
        self.seed_cells()
        self.print_grid()
        
    def seed_cells(self):
        """
        Seed the initial grid with a number of food items
        """
        pass
    
    def progress_sim(self):
        """
        Handles progressing the simulation forward 1 tick. Performs necessary actions on organism and foods
        """
        # Get the food and the organism at each cell
        for i in range(self._height):
            for j in range(self._width):
                occupant = self._grid[i][j].get_occupant()
                food = self._grid[i][j].get_food()
                
                # if there is an organism, have it eat any food on its space, and then decide an action
                if occupant is not None:
                    if food is not None:
                        occupant.eat_food(food)
                        self._grid[i][j].set_food(None)
                        food = None
                    self.check_organism(occupant)
                    action = occupant.take_action()
                    self.handle_action(action, occupant)

                # Decay food or check if food should be placed
                if food is not None:
                    food.decay()
                else:
                    self.place_food()
    
    def run_sim(self):
        """
        Executes a simulation and returns the number of iterations until the organism died
        """
        while self.forward_step() is True:
            pass
        return self._iterations
        
    def print_grid(self):
        """
        Display the current grid in ascii
        """
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
        """
        Take 1 step forward in the simulation, return false if the organism died.
        """
        self.progress_sim()
        self._iterations += 1
        if self._organism_death is True:
            return False
        self.print_grid()
        return True

    def handle_action(self, occupant, choice):
        """
        Executes an organisms desired action
        """
        cell = occupant.get_cell()
        coords = cell.get_coords()
        heading = occupant.get_heading()
        print(f"Organism executed a {ACTIONS[choice]} on turn {self._iterations}")
        if choice == 0:
            new_heading = turn_left(heading)
        elif choice == 1:
            new_heading = turn_right(heading)
        elif choice == 2:
            new_position = move_forward(coords, heading)
        elif choice == 3:
            pass
        if new_heading:
            occupant.set_heading(new_heading)
        if new_position:
            new_x = new_position[0] % self._width
            new_y = new_position[1] % self._height
            cell.set_occupant(None)
            self._grid[new_x,new_y].set_occupant(occupant)
            
            
    def check_organism(self, organism):
        """
        Check for organism death, reduce energy, fire bodyparts
        """
        pass

    def place_food(self):
        """
        Roll to see if new food should be placed.
        """
        pass

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
        
