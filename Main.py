import tkinter as tk
import numpy as np
import heapq
import time

from configurations import _from_rgb,victory,moveself

class PuzzleSolver:
    def __init__(self, initial_state, goal_state):
        self.initial_state = initial_state
        self.goal_state = goal_state
    @staticmethod
    def calculatedistance(state):
        distance = 0
        goal_state = ['1', '2', '3', '4', '5', '6', '7', '8', '']
        for i, tile in enumerate(state):
            if tile != '':
                # Calculate the distance of each tile from its goal position
                goal_index = goal_state.index(tile)
                distance += abs(i - goal_index)
        return distance    
    @staticmethod    
    def manhattan_distance(state):
        distance = 0
        for i in range(1, 9):
            current_position = state.index(str(i))
            goal_position = i - 1
            current_row, current_col = divmod(current_position, 3)
            goal_row, goal_col = divmod(goal_position, 3)
            distance += abs(current_row - goal_row) + abs(current_col - goal_col)
        return distance
    
    @staticmethod
    def get_neighbors(state):
        neighbors = []
        zero_index = state.index("")
        zero_row, zero_col = divmod(zero_index, 3)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  
        for dr, dc in directions:
            new_row, new_col = zero_row + dr, zero_col + dc
            if 0 <= new_row < 3 and 0 <= new_col < 3:
                new_index = new_row * 3 + new_col
                new_state = state[:]
                new_state[zero_index], new_state[new_index] = new_state[new_index], new_state[zero_index]
                neighbors.append(new_state)
        return neighbors
    def a_star_search(self):
        initial_state = tuple(self.initial_state)
        goal_state = tuple(self.goal_state)
        open_set = []
        heapq.heappush(open_set, (0, initial_state))
        came_from = {initial_state: None}
        g_score = {initial_state: 0}
        f_score = {initial_state: self.calculatedistance(initial_state)}
        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal_state:
                return self.reconstruct_path(came_from, current)
            for next_state in self.get_neighbors(list(current)):
                next_state = tuple(next_state)
                tentative_g_score = g_score[current] + 1
                if next_state not in g_score or tentative_g_score < g_score[next_state]:
                    came_from[next_state] = current
                    g_score[next_state] = tentative_g_score
                    f_score[next_state] = tentative_g_score + self.calculatedistance(next_state)
                    
                    heapq.heappush(open_set, (f_score[next_state], next_state))
        return None
    def hill_climbing_search(self):
      current_state = list(self.initial_state)
      while True:
        neighbors = self.get_neighbors(current_state)
        best_neighbor = None
        best_distance = float('inf')
        for neighbor in neighbors:
            distance = self.calculatedistance(neighbor)
            if distance < best_distance:
                best_neighbor = neighbor
                best_distance = distance
        if self.calculatedistance(current_state) <= best_distance:
            return self.reconstruct_path({}, tuple(current_state))
        current_state = best_neighbor
      return None

    def beam_search(self):
      initial_state = tuple(self.initial_state)
      goal_state = tuple(self.goal_state)
      open_set = []
      heapq.heappush(open_set, (0, initial_state))
      came_from = {initial_state: None}
      while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal_state:
            return self.reconstruct_path(came_from, current)
        closed_set = set()
        for next_state in self.get_neighbors(list(current)):
            next_state = tuple(next_state)  # Convert to tuple to make it hashable
            if next_state in closed_set:
                continue
            if next_state not in open_set:
                came_from[next_state] = current
                heapq.heappush(open_set, (self.calculatedistance(next_state), next_state))
            closed_set.add(next_state)  # Add the tuple to closed_set
      return None


    def best_first_search(self):
        initial_state = tuple(self.initial_state)
        goal_state = tuple(self.goal_state)
        open_set = []
        closed_set=set()
        heapq.heappush(open_set, (0, initial_state))
        came_from = {initial_state: None}
        while open_set:
            _,current = heapq.heappop(open_set)
            if current == goal_state:
                return self.reconstruct_path(came_from,current)
            closed_set.add(current)
            for next_state in self.get_neighbors(list(current)):
                next_state = tuple(next_state)
                if next_state in closed_set:
                    continue
                if next_state not in open_set:
                    came_from[next_state] = current
                    heapq.heappush(open_set,(self.calculatedistance(next_state),next_state))
        return None
    @staticmethod
    def reconstruct_path(came_from, current):
        path = []
        while current:
            path.append(list(current))
            current = came_from.get(current)
        return path[::-1]
class PuzzleGame:
    def __init__(self, master):
        self.master = master
        self.master.title("8Puzzlegame")
        self.master.geometry("600x600")
        self.tiles = {}
        self.moves = 0
        self.status_bar = tk.Label(self.master, text="Shuffling...", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.puzzle = self.generate_puzzle()
        self.winning_pos = [str(i) for i in range(1, 9)] + [""]
        self.start_game(self.puzzle)
        
    def solve_puzzle(self, pressed_button):
        initial_state = [self.tiles[(row, col)]['text'] for row in range(3) for col in range(3)]
        solver = PuzzleSolver(initial_state, self.winning_pos)
        if pressed_button == 1: 
            solution_path = solver.a_star_search()
        elif pressed_button==2:
            solution_path = solver.best_first_search()
        
        if solution_path:
            self.show_solution(solution_path)
        else:
            self.update_status_bar("No solution found.")
    
    def show_solution(self, solution_path, index=0):
        if index < len(solution_path):
            state = solution_path[index]
            self.update_puzzle(state)
            self.master.after(500, self.show_solution, solution_path, index + 1)
        else:
            self.update_status_bar("Solved.")
            self.check_winning_state()
        
    def find_empty_tile(self):
        for row in range(3):
            for col in range(3):
                if self.tiles[(row, col)]['text'] == "":
                    return row, col

    def swap_tiles(self, clicked_tile, empty_tile):
        self.tiles[clicked_tile]['text'], self.tiles[empty_tile]['text'] = self.tiles[empty_tile]['text'], self.tiles[clicked_tile]['text']
        self.tiles[empty_tile]['background'] = 'white'
        self.tiles[clicked_tile]['background'] = _from_rgb((135, 206, 250))
        self.moves += 1
        self.update_status_bar(f"Moves: {self.moves}")
        
    def on_tile_click(self, row, col):
        empty_x, empty_y = self.find_empty_tile()
        if ((row == empty_x and abs(col - empty_y) == 1) or (col == empty_y and abs(row - empty_x) == 1)):
            self.swap_tiles((row, col), (empty_x, empty_y))
            moveself.play()
            self.check_winning_state()

    def is_solvable(self, puzzle):
        p = puzzle[puzzle != 0]
        inversions = 0
        for i, x in enumerate(p):
            for y in p[i + 1:]:
                if x > y:
                    inversions += 1
        return inversions % 2 == 0

    def check_winning_state(self):
        current_state = [self.tiles[(row, col)]['text'] for row in range(3) for col in range(3)]
        if current_state == self.winning_pos :
            self.update_status_bar("Congratulations, You Won!!")
            victory.play()
            
    def update_status_bar(self, message):
        self.status_bar.config(text=message)   
        
    def generate_puzzle(self):
        while True:
            puzzle = np.random.permutation(9)
            if self.is_solvable(puzzle):
                return puzzle

    def reset_game(self):
        self.moves = 0
        self.update_status_bar("Shuffling...")
        self.puzzle = self.generate_puzzle()
        self.tiles[self.find_empty_tile()]["background"] = 'white'
        for c, i in enumerate(self.puzzle.flatten()):
            row, col = divmod(c, 3)
            self.tiles[(row, col)].config(text=str(i) if i != 0 else "", background=_from_rgb((135, 206, 250)) if i == 0 else None)

    def start_game(self, p):
        self.master.configure(background='lightgrey')  # Set a background color for the window
        self.tiles_frame = tk.Frame(self.master, bg='lightgrey')
        self.tiles_frame.pack(pady=(100, 0))  # Add padding to center the frame vertically

        # Use a larger, bold font for the numbers on the tiles
        tile_font = ('Arial', 24, 'bold')

        for c, i in enumerate(p):
            row, col = divmod(c, 3)
            tile_color = 'white' if i != 0 else _from_rgb((135, 206, 250))
            tile_text = str(i) if i != 0 else ""
            tile = tk.Button(self.tiles_frame, background=tile_color, text=tile_text, width=5, height=2,
                             font=tile_font, command=lambda x=row, y=col: self.on_tile_click(x, y))
            tile.grid(row=row, column=col, padx=5, pady=5)  # Add padding between tiles
            self.tiles[(row, col)] = tile

        # Style the control buttons
        button_font = ('Arial', 14)
        control_frame = tk.Frame(self.master, bg='lightgrey')
        control_frame.pack(pady=(20, 0))
        reset_button = tk.Button(control_frame, text="Restart", width=10, height=1, font=button_font, command=self.reset_game)
        reset_button.grid(row=0, column=0, padx=10)
        solve_button = tk.Button(control_frame, text="Solve (A*)", width=10, height=1, font=button_font, command=lambda x=1: self.solve_puzzle(x))
        solve_button.grid(row=0, column=1, padx=10)
        solve_button_2 = tk.Button(control_frame, text="Solve (BFS)", width=20, height=1, font=button_font, command=lambda x=2: self.solve_puzzle(x))
        solve_button_2.grid(row=0, column=2, padx=10)

    def update_puzzle(self, state):
        for index, tile_value in enumerate(state):
            row, col = divmod(index, 3)
            if tile_value == "":
                self.tiles[(row, col)]['background'] = _from_rgb((135, 206, 250))
            else:
                self.tiles[(row, col)]['background'] = 'white'
            self.tiles[(row, col)]['text'] = tile_value
        self.moves += 1
        self.update_status_bar(f"Moves: {self.moves}")
        moveself.play()
    def show_solution(self, solution_path):
        for state in solution_path:
            self.update_puzzle(state)
            self.master.update_idletasks()
            time.sleep(0.2)
            self.update_status_bar("solved")
            self.check_winning_state()
  
        

if __name__ == '__main__':
    mainWindow = tk.Tk()
    game = PuzzleGame(mainWindow)
    mainWindow.mainloop()
