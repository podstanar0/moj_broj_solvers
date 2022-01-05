import random
import argparse
from itertools import combinations
from colorama import Fore, Style

from parser import BinaryIntegerArithmeticExpression as E
from search import SearchNode, AStarSearch


def get_result(n1, n2, operator):
    if operator == '+':
        result = n1 + n2
    elif operator == '-':
        result = n1 - n2
    elif operator == '*':
        result = n1 * n2
    elif operator == '/':
        result = int(n1 / n2)

    return result


class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class CountDownNumbersException(Exception):
    pass


class CountDownNumbers:
    def __init__(self, brojevi, cilj):
        self.brojevi = brojevi
        self.cilj = cilj

    def find_solution(self, tolerance=0):
        def _id(node):
            brojevi = node.data['brojevi']
            return tuple(sorted(brojevi))

        def is_goal(node):
            brojevi = node.data['brojevi']
            for number in brojevi:
                if abs(number - self.cilj) <= tolerance:
                    return True

            return False

        def heuristic(node):
            brojevi = node.data['brojevi']
            diffs = [abs(n - self.cilj) for n in brojevi]
            return min(diffs)

        def possible_moves(node):
            brojevi = node.data['brojevi']
            moves = []
            for (n1, n2) in combinations(brojevi, 2):

                moves.append((n1, '*', n2))
                moves.append((n1, '+', n2))

                # disallow fractions
                if n2 != 0 and n1 % n2 == 0:
                    moves.append((n1, '/', n2))

                if n1 != 0 and n2 % n1 == 0:
                    moves.append((n2, '/', n1))


                # disallow negative numbers
                if n1 >= n2:
                    moves.append((n1, '-', n2))
                else:
                    moves.append((n2, '-', n1))

            return moves

        def apply_move(node, move):
            n1, operator, n2 = move
            brojevi = node.data['brojevi'][:]
            brojevi.remove(n1)
            brojevi.remove(n2)

            result = get_result(n1, n2, operator)

            brojevi.append(result)
            data = {
                'brojevi': brojevi
            }

            return SearchNode(data, _id, possible_moves, apply_move)

        data = {
            'brojevi': self.brojevi
        }

        start_node = SearchNode(data, _id, possible_moves, apply_move)

        search = AStarSearch(start_node, is_goal, heuristic)

        result, path = search.do_search()

        if not result:
            raise CountDownNumbersException("No path found.")
            
        # special case: the solution was already in the numbers
        if not path:
            expressions = [E(number) for number in self.brojevi]
            mindiff, expression = min([
                (abs(e.value-self.cilj), e) for e in expressions
            ])
            
            return [], expression

        return path, self.moves_to_expression(path)

    def moves_to_expression(self, moves):

        def extract_expression(expressions, val):
            to_extract = None
            for e in expressions:
                if e.value == val:
                    to_extract = e
                    break
            expressions.remove(to_extract)
            return to_extract

        expressions = [E(n) for n in self.brojevi]
        for move in moves:
            n1, op, n2 = move
            e1 = extract_expression(expressions, n1)
            e2 = extract_expression(expressions, n2)

            result = E(op1=e1, op2=e2, o=op)
            expressions.append(result)

        mindiff, expression = min([
            (abs(e.value-self.cilj), e) for e in expressions
        ])

        return expression


def report_path(path):
    for move in path:
        n1, operator, n2 = move

        print(Fore.YELLOW + "{n1} {operator} {n2} = {val}".format(
            n1=n1,
            n2=n2,
            operator=operator,
            val=get_result(n1, n2, operator)
        ))


def generate_numbers(nlarge=1):
    assert 0 <= nlarge <= 4
    nsmall = 6 - nlarge

    large = [25, 50, 75, 100]
    small = 2 * list(range(1, 11))

    return random.sample(large, nlarge) + random.sample(small, nsmall)

def generate_goal():
    return random.randrange(101, 1000)


def main():
    parser = argparse.ArgumentParser(description="--- Moj Broj solver by podstanar ---")
    parser.add_argument(
        "brojevi",
        type=int,
        nargs='*',
        help="brojevi koje će solver koristiti da pronađe ciljani broj"
    )
    parser.add_argument(
        "-c",
        "--cilj",
        type=int,
        nargs="?",
        default=-1,
        help="ciljani broj koji treba pronaći"
    )
    args = parser.parse_args()

    brojevi = args.brojevi
    cilj = args.cilj

    if not brojevi:
        brojevi = generate_numbers(
            nlarge=random.randrange(0, 5)
        )
    
    if cilj == -1:
        cilj = generate_goal()

    c = CountDownNumbers(brojevi, cilj)
    tolerance = 0
    success = False

    while not success:
        print(
            "\nPokušavam da pronađem" +
            Fore.RED,
            cilj + tolerance,
            Style.RESET_ALL +
            "kombinovanjem" +
            Fore.BLUE,
            str(brojevi) +
            Style.RESET_ALL +
            ". Tolerancija =",
            tolerance
        )

        try:
            path, expression = c.find_solution(tolerance)
            report_path(path)
            print(
                Style.BRIGHT +
                Fore.GREEN +
                "\n-->" + 
                Style.RESET_ALL + 
                " Rešenje: " + 
                Fore.GREEN + 
                str(expression) + 
                " =" + 
                Fore.LIGHTRED_EX, 
                expression.value
            )

            error = abs(expression.value - c.cilj)
            if error > 0:
                print(
                    Style.RESET_ALL + 
                    "(za", 
                    error, 
                    "dalji od originalnog", 
                    str(cilj) + 
                    ')')

            success = True

        except CountDownNumbersException:
            tolerance += 1
            print(
                Fore.LIGHTMAGENTA_EX +
                "Ne postoji rešenje.",
                Style.RESET_ALL +
                "Novi cilj je:", 
                Fore.RED + 
                str(cilj + 
                tolerance) + 
                Style.RESET_ALL)

if __name__ == '__main__':
    main()
