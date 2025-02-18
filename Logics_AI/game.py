from safety_checker import MineSafetyChecker

GRID_SIZE = 8


class GameLogic:
    def __init__(self):
        self.reset()
        self.step = -1
        self.new_grid()
        self.visited_cells[0][0] = True

    def process_input_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    parts = line.strip().split()
                    x, y = int(parts[0]), int(parts[1])
                    char = parts[2]

                    if char == 'c':
                        message = " ".join(parts[3:])
                        self.messages[x * GRID_SIZE + y] = message
                    self.grid[x][y] = char
        except Exception as e:
            print(f"An error occurred: {e}")

    def new_grid(self):
        self.step = (self.step+1)%3
        self.safety_checker = MineSafetyChecker(GRID_SIZE,self.step)
        match self.step:
            case 0:
                self.process_input_file("grid1")
            case 1:
                self.process_input_file("grid2")
            case 2:
                self.process_input_file("grid3")
        self.safety_checker.add_rule(self.messages[0])

    def reset(self):
        self.grid = [['o' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.agent_position = [0, 0]
        self.visited_cells = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.game_over = False
        self.mines_found = []
        self.messages = {}
        self.safety_checker = None
        self.safe_mode = False

    def new_game(self):
        self.reset()
        self.visited_cells[0][0] = True
        self.new_grid()
        return {"message": self.messages[0], "cell_color": self.get_cell_colors()}

    def toggle_safe_mode(self):
        self.safe_mode = not self.safe_mode
        return {"safe": self.safe_mode}


    def handle_double_click(self, x, y):


        has_mine = self.grid[x][y] == 'm'
        if has_mine:
            self.visited_cells[x][y] = True
            self.game_over = False
            colors = self.get_cell_colors()
            colors[x][y] = "white"
            if (x, y) not in self.mines_found:
                self.mines_found.append((x,y))
            if len(self.mines_found) != 4:
                return {"has_mine": True, "message": "Mine hit!", "game_over": False, "cell_color": colors}
            else:
                return {"has_mine": True, "message": "You win!", "game_over": False, "cell_color": colors}
        else:
            self.visited_cells[x][y] = True
            colors = self.get_cell_colors()
            colors[x][y] = "red"
            self.game_over = True
            return {"has_mine": False, "message": "Safe cell clicked. Game Over!", "game_over": True, "cell_color": colors}

    def get_cell_colors(self):
        colors = [["black" for _ in range(len(self.grid[0]))]
                  for _ in range(len(self.grid))]

        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if self.agent_position == [i, j] and self.grid[i][j] != 'm':
                    colors[i][j] = "green"
                elif self.visited_cells[i][j]:
                    if self.agent_position == [i, j] and self.grid[i][j] == 'm':
                        colors[i][j] = "red"
                    elif self.grid[i][j] == 'm' and (i,j) not in self.mines_found:
                        colors[i][j] = "white"
                    else:
                        colors[i][j] = "white"
        return colors


    def move_agent(self, direction):
        if self.game_over:
            return {"status": "Game Over", "position": self.agent_position, "colors": self.get_cell_colors()}

        x, y = self.agent_position
        if direction == "up" and x > 0:
            x -= 1
        elif direction == "down" and x < GRID_SIZE - 1:
            x += 1
        elif direction == "left" and y > 0:
            y -= 1
        elif direction == "right" and y < GRID_SIZE - 1:
            y += 1

        if not self.safe_mode or (self.visited_cells[x][y] and (x,y) not in self.mines_found) or self.safety_checker.check_safety(x+1,y+1) == "safe":
            self.agent_position = [x, y]
        else:
            x,y = self.agent_position

        if self.grid[x][y] == 'm':
            self.game_over = True
            self.visited_cells[x][y] = True
            return {"status": "Mine Hit", "position": self.agent_position, "colors": self.get_cell_colors()}
        elif self.grid[x][y] == 'c':
            key = x * GRID_SIZE + y
            if not self.visited_cells[x][y] :
                self.safety_checker.add_rule(self.messages[key])
            self.visited_cells[x][y] = True
            return {"status": self.messages[x*GRID_SIZE+y], "position": self.agent_position, "colors": self.get_cell_colors()}
        self.visited_cells[x][y] = True
        return {"status": "Moved", "position": self.agent_position, "colors": self.get_cell_colors()}

    def reset_game(self):
        self.agent_position = [0, 0]
        self.game_over = False
        self.visited_cells = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.visited_cells[0][0] = True
        self.mines_found = []
        self.safety_checker = MineSafetyChecker(GRID_SIZE,self.step)
        self.safety_checker.add_rule(self.messages[0])
        self.safe_mode = False
        return {"message": self.messages[0], "colors": self.get_cell_colors() }

    def reveal_answer(self):
        return {
            "grid": self.grid
        }

    def get_game_state(self):
        return {
            "agent_position": self.agent_position,
            "visited_cells": self.visited_cells,
            "grid": self.grid,
            "game_over": self.game_over,
            "cell_colors": self.get_cell_colors(),
            "message": self.messages[0]
        }