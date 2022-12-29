import numpy as np

import pyautogui
import termcolor

colors = np.array([
    [189, 189, 189], # 0
    [0, 0, 255], # 1
    [0, 123, 0], # 2 
    [255, 0, 0], # 3
    [0, 0, 123], # 4
    [123, 0, 0], # 5
    [0, 123, 123], # 6
    [0, 0, 0], # 7
    [123, 123, 123], # 8
    [255, 255, 255] # 9 covered
])

colors_no0 = np.array([
    [1000, 1000, 1000], # not 0
    [0, 0, 255], # 1
    [0, 123, 0], # 2 
    [255, 0, 0], # 3
    [0, 0, 123], # 4
    [123, 0, 0], # 5
    [0, 123, 123], # 6
    [0, 0, 0], # 7
    [123, 123, 123], # 8
    [255, 255, 255] # 9 covered
])

colors_dict = {
    '0' : 'grey',
    '1' : 'blue',
    '2' : 'green',
    '3' : 'red',
    '4' : 'magenta',
    '5' : 'red',
    '6' : 'cyan',
    '7' : 'yellow',
    '8' : 'yellow',
    '.' : 'white',
    'F' : 'white'
} 


class Cell: 
    def __init__(self, r, c):
        ''' Initiatlize a cell with coordinates (r, c)
        '''
        self.r, self.c = r, c
        self.value = 'covered' # 0-8, covered, flag

class Game:
    ''' Game class hold information about the game current state,
    methods to solve the field from the current state
    '''
    def __init__(self, nrows, ncols, width, height, left, top):
        self.nrows, self.ncols = nrows, ncols
        self.width, self.height = width, height
        self.left, self.top = left, top
        self.create_field()
    
    def create_field(self):
        ''' Initialize a field by adding cells to a two-dimensional array
        '''
        self.field = np.empty((self.nrows, self.ncols), dtype=object)
        for row in range(self.nrows):
            for col in range(self.ncols):
                self.field[row, col] = Cell(row, col)

    def get_value(self, img, cell):
        ''' Get the current state of a cell from screenshot
        Return: cell value
        '''
        y_center = self.top + cell.r * self.height + 0.5 * self.height
        x_center = self.left + cell.c * self.width + 0.5 * self.width
        is_zero_cell = True
        lowest_error = 3000000

        # Check if value of a cell is zero. If it is not a zero cell, exit loop
        for y in range(int(y_center - 0.3 * self.height), int(y_center + 0.3 * self.height)):      
            color = np.array(img.getpixel((x_center, y)))
            error = np.sum(np.square(color - colors), axis = 1, keepdims = True)
            state = np.argmin(error)
            if state != 0:
                is_zero_cell = False
                break
            value = 0
        
        # Find value of a cell when already know it is not zero
        if not is_zero_cell:
            for y in range(int(y_center - 0.3 * self.height), int(y_center + 0.3 * self.height)):      
                color = np.array(img.getpixel((x_center, y)))
                error = np.sum(np.square(color - colors_no0), axis = 1, keepdims = True)
                state = np.argmin(error)  
                if np.min(error) < lowest_error:
                    lowest_error = np.min(error)
                    value = state

        # Zero cell and covered cell has same color. Check if it is a covered cell
        if is_zero_cell:
            for x in range(int(x_center - 0.5 * self.width), int(x_center - 0.3 * self.width)): 
                color = np.array(img.getpixel((x, y_center)))
                error = np.sum(np.square(color - colors), axis = 1, keepdims = True)
                state = np.argmin(error)      
                if state == 9:
                    value = 9
                    break

        return value

    def print(self, img):
        ''' Print the field on the terminal, modify cells (except flag)
        '''
        for row in range(self.nrows):
            for col in range(self.ncols):
                cell = self.field[row, col]
                if cell.value == 'flag':
                    res = 'F'
                else:
                    res = self.get_value(img, cell)
                    if res == 9:
                        res = '.'
                    else: 
                        cell.value = res
                print(termcolor.colored(res, colors_dict[str(res)]), end = ' ')
            print()
        print()
        print()

    def get_neighbors(self, cell):
        ''' Return a list of neighbor cells
        '''
        r, c = cell.r, cell.c
        neighbors = []

        for row in range(r - 1, r + 2):
            for col in range(c - 1, c + 2):
                if ((row != r or col != c) and
                    (0 <= row < self.nrows) and
                    (0 <= col < self.ncols)):
                    neighbors.append(self.field[row, col])

        return neighbors
    
    def get_covered_neighbors(self, cell):
        ''' Return a list of covered neighbor cells
        '''
        covered_neighbors = []

        for neighbor in self.get_neighbors(cell):
            if neighbor.value == 'covered':
                covered_neighbors.append(neighbor)

        return covered_neighbors
    
    def get_border(self):
        ''' Return a list of border cells
        '''
        border = []

        for row in self.field:
            for cell in row:
                if cell.value != 'covered' and cell.value != 'flag':
                    for neighbor in self.get_covered_neighbors(cell):
                        border.append(cell)

        return list(set(border))

    def is_subgroup(self, cell_1, cell_2):
        ''' Check if uncovered neighbors of cell 1 is a subgroup of 
        uncovered neighbors of cell 2
        Return: boolean
        '''
        res = True

        for neighbor in self.get_covered_neighbors(cell_1):
            if neighbor not in self.get_covered_neighbors(cell_2):
                res = False

        return res
    
    def get_num_covered(self, cell):
        ''' Return: int(number of covered around a cell)
        '''
        count = 0

        for neighbor in self.get_neighbors(cell):
            if neighbor.value == 'covered':
                count += 1
        
        return count

    def get_num_flag(self, cell):
        ''' Return: int(number of flag around a cell)
        '''
        count = 0

        for neighbor in self.get_neighbors(cell):
            if neighbor.value == 'flag':
                count += 1

        return count
    
    def get_num_mine(self, cell):
        ''' Return: int(number of mines left around a cell)
        '''
        return int(cell.value) - self.get_num_flag(cell)
    
    def first_move(self):
        self.click(self.field[self.nrows // 2, self.ncols // 2], 'left')

    def method_naive(self):
        ''' Basic algorithm to solve minesweeper
        '''
        safe, mines = [], []
        
        for cell in self.get_border():
            mine = self.get_num_mine(cell)
            covered = self.get_num_covered(cell)

            # No mines around
            if mine == 0:
                safe.extend(self.get_covered_neighbors(cell))

            # Number of mines left = number of unclicked cells
            if mine == covered:
                mines.extend(self.get_covered_neighbors(cell))
        
        return list(set(safe)), list(set(mines))

    def method_group(self):
        safe, mines = [], []

        for cell_1 in self.get_border():
            for cell_2 in self.get_border():
                if self.is_subgroup(cell_1, cell_2):
                    unclicked = self.get_covered_neighbors(cell_2)
                    for ele in self.get_covered_neighbors(cell_1):
                        unclicked.remove(ele)

                    # Deduce safe cells
                    if self.get_num_mine(cell_1) == self.get_num_mine(cell_2):
                        safe.extend(unclicked)

                    # Deduce mine cells
                    if self.get_num_mine(cell_1) + len(unclicked) == self.get_num_mine(cell_2):
                        mines.extend(unclicked)
        
        return list(set(safe)), list(set(mines))
    
    def method_backtracking(self):
        pass
        # TODO: your code here
    
    def solve(self):
        ''' Go through all methods, then open safe cells and flag mine cells
        '''
        methods = [self.method_naive, self.method_group]

        for method, method_name in methods:
            safe, mines = method()
            if safe or mines:
                break

        for cell in safe:
            self.click(cell, 'left')
        for cell in mines:
            self.click(cell, 'right')
            cell.value = 'flag'

    def click(self, cell, button):
        y_center = self.top + cell.r * self.height + 0.5 * self.height
        x_center = self.left + cell.c * self.width + 0.5 * self.width
        pyautogui.click(x_center, y_center, button = button)