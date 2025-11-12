"""
Defines the 4 actions available to the critters:
Turn_l, Turn_r, move forward, do nothing, eat <- Possible don't need instead maybe they just go on the space
"""

def turn(direction):
    return direction

def turn_left(heading):
    return turn(-1*heading[1],heading[0])

def turn_right(heading):
    return turn(heading[1],-1*heading[0])

def move_forward(current_space, current_heading):
    return [current_space[0] + current_heading[0], current_space[1]+current_heading[1]]

def nop():
    return
