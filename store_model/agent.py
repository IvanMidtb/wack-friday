from mesa import Agent
import math
import random

wanted_items = ["Electronics", "Clothing", "Food", "misc"]


# from sugarscape_cg
def get_distance(pos_1, pos_2):
    """ Get the distance between two point

    Args:
        pos_1, pos_2: Coordinate tuples for both points.

    """
    x1, y1 = pos_1
    x2, y2 = pos_2
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx ** 2 + dy ** 2)



class Shelf(Agent):
    """
    The shelves
    """
    def __init__(self, unique_id, model, contents, moore=True):
        super().__init__(unique_id, model)
        self.moore = moore
        self.contents = contents
        self.amount = 10


class Customer(Agent):
    """
    The customer
    """
    def __init__(self, unique_id, model, moore=True):
        super().__init__(unique_id, model)
        self.state = "LOOK"
        self.moore = moore
        self.patience = random.randint(500, 1000)
        self.wants = []
        self.exit_positions = [(int(self.model.grid.width/2  - 1 + i), int(self.model.grid.height) -1) for i in range(4)]
        for i in range(3):
            self.wants.append(random.choice(wanted_items))

    def step(self):
        if self.state == "LOOK":
            self.random_move()
            self.shop()
        if self.state == "CHECKOUT":
            if self.pos == self.exit_positions[3]: self.model.exit(self)
            else: self.exit_move()

    # based on wolf_sheep RandomWalker
    def random_move(self):
        """
        Step one cell in any allowable direction.
        """
        # Pick the next cell from the adjacent empty cells.
        next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, True)
        valid_moves = []
        for move in next_moves:
            if self.model.grid.is_cell_empty(move):
                valid_moves.append(move)
        if len(valid_moves) == 0: return
        next_move = self.random.choice(valid_moves)
        # Now move:
        self.patience -= 1
        if self.patience == 0: self.state = "CHECKOUT"
        self.model.grid.move_agent(self, next_move)

    def shop(self):
        n_shelves = [n for n in self.model.grid.get_neighbors(self.pos, self.moore) if type(n) is Shelf]
        for shelf in n_shelves:
            if shelf.amount == 0: continue
            elif self.wants[-1] == shelf.contents:
                del self.wants[-1]
                shelf.amount -= 1
                if len(self.wants) == 0: 
                    self.state = "CHECKOUT"
                    break
            
    def exit_move(self):
        # Get neighborhood within vision
        valid_moves = [n for n in self.model.grid.get_neighborhood(self.pos, self.moore, True) if self.model.grid.is_cell_empty(n)]
        if len(valid_moves) == 0: return
        # For now, just pathfinds to the far right door
        min_dist = min([get_distance(self.exit_positions[3], pos) for pos in valid_moves])
        
        final_candidates = [
            pos for pos in valid_moves if get_distance(self.exit_positions[3], pos) == min_dist
        ]
        self.random.shuffle(final_candidates)
        self.model.grid.move_agent(self, final_candidates[0])

