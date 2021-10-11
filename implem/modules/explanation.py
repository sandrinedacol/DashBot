import numpy as np


class Explanation:
    def __init__(self, remove_or_add, dimension):
        self.name = (remove_or_add, dimension)
        self.remove_or_add = remove_or_add
        self.dimension = dimension
        self.occurence = [0,0]
        self.score = None       # exp ( ratio / tempertaure )
        self.proba = None       # local proba (0 if not possible, normalized score otherwise)

