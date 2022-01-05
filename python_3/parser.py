from functools import total_ordering
from enum import Enum
from collections import deque


class InvalidExpressionException(Exception):
    pass


class ExpressionParseError(Exception):
    pass


class Token(Enum):
    number = 0
    open_paren = 1
    close_paren = 2
    add = 3
    sub = 4
    mul = 5
    div = 6


def precedence(operator):
    if operator in ('+', '-'):
        return 2

    elif operator in ('/', '*'):
        return 3


def associative(operator):
    return operator in ('+', '*')

@total_ordering
class BinaryIntegerArithmeticExpression:
    _value = None
    o1 = None
    o2 = None
    o = None

    def __init__(self, value=None, op1=None, op2=None, o=None):
        if value is not None:
            assert type(value) == int
            self._value = value

        else:
            if o == '/' and (op1.value % op2.value != 0):
                raise InvalidExpressionException(
                    "Division is only allowed if the quotient is an integer."
                )

            self.op1 = op1
            self.op2 = op2
            self.o = o

    @property
    def value(self):
        if self._value is None:
            v1 = self.op1.value
            v2 = self.op2.value

            if self.o == '+':
                self._value = v1 + v2
            elif self.o == '-':
                self._value = v1 - v2
            elif self.o == '*':
                self._value = v1 * v2
            else:
                self._value = int(v1 / v2)

        return self._value

    def rep(self, parent_op=None, side=None):
        if self.o is None:
            return '{}'.format(self._value)

        else:
            r1 = self.op1.rep(parent_op=self.o, side='l')
            r2 = self.op2.rep(parent_op=self.o, side='r')
            r = '{r1} {o} {r2}'.format(r1=r1, o=self.o, r2=r2)

            # we need parens if we're of lower precedence than our parent.
            # eg 3 * 2 + 2 vs 3 * (2 + 2)
            if parent_op and precedence(parent_op) > precedence(self.o):
                r = '({r})'.format(r=r)

            # we also need parens if we're on the right side of a
            # left-associative operation and our parent is not associative
            # i.e 4 - 2 + 2 vs 4 - (2 + 2)
            elif (not associative(parent_op)) and side == 'r':
                r = '({r})'.format(r=r)

            return r

    def __str__(self):
        return self.rep()
        
    def __lt__(self, other):
        return self.value < other.value

    @classmethod
    def parse(cls, s):
        def tokenize(s):
            tokens = []
            numbers = "0123456789"

            on_number = False
            number = ''
            for c in s:
                if c in numbers:
                    number = number + c
                    on_number = True
                    continue

                if on_number:
                    on_number = False
                    tokens.append((Token.number, int(number)))
                    number = ''

                if c in [' ', '\n', '\t']:
                    continue

                elif c == '(':
                    tokens.append((Token.open_paren, c))

                elif c == ')':
                    tokens.append((Token.close_paren, c))

                elif c == '+':
                    tokens.append((Token.add, c))

                elif c == '-':
                    tokens.append((Token.sub, c))

                elif c == '*':
                    tokens.append((Token.mul, c))

                elif c == '/':
                    tokens.append((Token.div, c))

                else:
                    raise ExpressionParseError('Unknown symbol: ' + c)

            if on_number:
                on_number = False
                tokens.append((Token.number, int(number)))
                number = ''

            return tokens

        tokens = tokenize(s)

        output_queue = deque()
        operator_stack = []

        for token in tokens:
            token_type, val = token

            if token_type == Token.number:
                output_queue.append(val)

            elif token_type in [Token.add, Token.sub, Token.mul, Token.div]:
                while operator_stack:
                    val2 = operator_stack[len(operator_stack) - 1]

                    if val2 == '(':
                        break

                    elif precedence(val) <= precedence(val2):
                        val2 = operator_stack.pop()
                        output_queue.append(val2)

                    else:
                        break

                operator_stack.append(val)

            elif token_type == Token.open_paren:
                operator_stack.append(val)

            elif token_type == Token.close_paren:
                open_found = False
                while operator_stack:
                    val2 = operator_stack.pop()
                    if val2 == '(':
                        open_found = True
                        break

                    else:
                        output_queue.append(val2)

                if not open_found:
                    raise ExpressionParseError('Mismatched parentheses')

        # tokens are now empty, pop any remaining operators into the queue
        while operator_stack:
            op = operator_stack.pop()

            if op == '(':
                raise ExpressionParseError('Mismatched parentheses')

            output_queue.append(op)

        stack = []

        for item in output_queue:
            if type(item) == int:
                stack.append(BinaryIntegerArithmeticExpression(item))

            else:
                operand2 = stack.pop()
                operand1 = stack.pop()
                stack.append(BinaryIntegerArithmeticExpression(
                    op1=operand1, op2=operand2, o=item
                ))

        return stack.pop()

if __name__ == '__main__':
    tests = [
        '1 + 1',
        '2 / 1',
        '2 * 2',
        '3 - 1',
        '1 - (1 - 1)',
        '3 - (1 + 1)',
        '4 / 2 / 2',
        '4 / (2 / 2)'
    ]

    for test in tests:
        e = BinaryIntegerArithmeticExpression.parse(test)
        print("input {test} je rezultovao izrazom {e} čija je vrednost {v}".format(
            test=test,
            e=str(e),
            v=e.value
        ))
