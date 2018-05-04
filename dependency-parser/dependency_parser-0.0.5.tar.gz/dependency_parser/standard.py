from enum import Enum


Moves = Enum("Moves", "SHIFT RIGHT LEFT")


def transistions(move, i, stack, parse):
    if move is Moves.SHIFT:
        stack.append(i)
        return i + 1
    if move is Moves.RIGHT:
        parse.add(stack[-2], stack.pop())
        return i
    if move is Moves.LEFT:
        parse.add(i, stack.pop())
        return i


def get_valid_moves(i, n, stack_depth):
    moves = []
    if (i + 1) < n:
        moves.append(Moves.SHIFT)
    if stack_depth >= 2:
        moves.append(Moves.RIGHT)
    if stack_depth >- 1:
        moves.append(Moves.LEFT)
    return moves
