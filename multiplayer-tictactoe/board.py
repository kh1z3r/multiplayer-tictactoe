class Board:
    def __init__(self):
        self.grid_matrix = [["" for x in range(3)] for y in range(3)]
        self.switch_user = False
        self.gameover = False
        self.y_offset = 0  # This will be set by the client
        
        # Define grid lines
        self.gridlines = [
            # Vertical lines
            ((200, 0), (200, 600)),
            ((400, 0), (400, 600)),
            # Horizontal lines
            ((0, 200), (600, 200)),
            ((0, 400), (600, 400))
        ]
    
    def get_cell_val(self, x, y):
        """Get the value of a cell"""
        if 0 <= x < 3 and 0 <= y < 3:
            return self.grid_matrix[y][x]
        return None
    
    def set_cell_val(self, x, y, val):
        """Set the value of a cell"""
        if 0 <= x < 3 and 0 <= y < 3:
            self.grid_matrix[y][x] = val
            return True
        return False
    
    def get_mouse_input(self, x, y, user):
        """Handle mouse input and update board"""
        if 0 <= x < 3 and 0 <= y < 3:
            if self.grid_matrix[y][x] == "":
                self.grid_matrix[y][x] = user
                self.switch_user = True
                return True
        return False
    
    def clear_board(self):
        """Reset the board"""
        self.grid_matrix = [["" for x in range(3)] for y in range(3)]
        self.switch_user = False
        self.gameover = False
    
    def board_full(self):
        """Check if board is full"""
        return all(cell != "" for row in self.grid_matrix for cell in row) 