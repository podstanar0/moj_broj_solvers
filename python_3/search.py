import heapq
import logging

from functools import total_ordering

logger = logging.getLogger('rl')


@total_ordering
class SearchNode(object):
    """Represents a state of a space used for a search.  Initialization
    requires a dictionary and 3 functions:
    1.  data - a dictionary containing all necessary state information.
    3.  id(node): a function that returns an identifier representing the state
    3.  possible_moves(self): returns a list of moves.
    4.  apply_move(self, move):  returns a SearchNode that is the result of the
    passed in move.
    """

    __slots__ = [
        'data',
        'id',
        'possible_moves',
        'apply_move',
        'move_to_reach',
        'parent',
        'path_length',
        'path_depth',
        'h'
    ]

    def __init__(self, data, id, possible_moves, apply_move):
        self.data = data
        self.id = id
        self.possible_moves = possible_moves
        self.apply_move = apply_move
        self.move_to_reach = None
        self.parent = None
        self.path_length = None
        self.path_depth = None
        self.h = None

    def __eq__(self, other):
        return self.id(self) == other.id(other)

    def expand(self):
        nodes = []
        moves = self.possible_moves(self)
        for move in moves:
            node = self.apply_move(self, move)
            node.parent = self
            node.move_to_reach = move
            nodes.append(node)

        return nodes

    def compute_path_length(self):
        if not self.parent:
            return 0
        else:
            return (
                self.data.get('path_cost', 1) +
                self.parent.get_path_length()
            )

    def compute_path_depth(self):
        if not self.parent:
            return 0
        else:
            return 1 + self.parent.get_path_depth()

    def get_path_length(self):
        if not self.path_length:
            self.path_length = self.compute_path_length()

        return self.path_length

    def get_path_depth(self):
        if not self.path_depth:
            self.path_depth = self.compute_path_depth()

        return self.path_depth

    def get_path(self):
        moves = []

        n = self
        while n.parent:
            moves.append(n.move_to_reach)
            n = n.parent

        return [m for m in reversed(moves)]

    def __str__(self):
        return str(self.data)

    def __lt__(self, other):
        # for the most part, these will be compared based on their g+h values.
        # this is a tie-breaker for when those are equal
        
        return self.id(self) < other.id(other)


class AStarSearch(object):
    """An A* search. Initialization requires:
    1.  start:  A SearchNode representing the initial state
    2.  is_goal: a function testing if a search node is the goal
    3.  heuristic(node):  a function that takes a SearchNode and returns
    an integer, representing an estimated number of moves from state to goal.
    """
    def __init__(self, start, is_goal, heuristic, max_depth=None):
        self.start = start
        self.is_goal = is_goal
        self.heuristic = heuristic
        self.max_depth = max_depth

    def do_search(self):
        visited = {}

        def sortkey(node):
            if not node.h:
                node.h = self.heuristic(node)

            return node.get_path_length() + node.h

        frontier = [(sortkey(self.start), self.start)]
        heapq.heapify(frontier)
        fset = set()
        fset.add(self.start.id(self.start))

        while frontier:

            _, current = heapq.heappop(frontier)

            if self.is_goal(current):
                return True, current.get_path()

            for new in current.expand():
                if (new.id(new) in visited and
                    (new.get_path_length() >=
                     visited[new.id(new)].get_path_length())):
                    continue

                if new.id(new) in fset:
                    continue

                if not self.max_depth:
                    heapq.heappush(frontier, (sortkey(new), new))
                    fset.add(new.id(new))

                elif new.get_path_depth() < self.max_depth:
                    heapq.heappush(frontier, (sortkey(new), new))
                    fset.add(new.id(new))

                visited[new.id(new)] = new

        return False, None
        