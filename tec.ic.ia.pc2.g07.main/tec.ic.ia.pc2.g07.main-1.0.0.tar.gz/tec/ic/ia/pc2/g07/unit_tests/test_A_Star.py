from tec.ic.ia.pc2.g07.algorithms.A_Star import A_Star

'''
[A*] Search where is located the rabbit at the start.
Function tested: search_start()
Outputs: A list containing the row and the column of the rabbit. [0,2]
'''
def test_search_rabbit_on_board_at_start():
    board = [[" "," ","C"],["Z"," "," "],[" ","Z"," "]]
    a_test = A_Star(board, vision=2, carrots=2, MaxLastMovements=2)
    [row, column] = a_test.search_start(board)
    assert [row, column] == [0,2]


'''
[A*] Search if [2,2] is inside a board of 3x3.
Function tested: is_in_board()
Outputs: True.
'''
def test_2_2_is_in_a_board_of_3x3():
    board = [[" "," ","C"],["Z"," "," "],[" ","Z"," "]]
    a_test = A_Star(board, vision=2, carrots=2, MaxLastMovements=2)
    result = a_test.is_in_board(x=2, y=2, board=board)
    assert result == True

'''
[A*] Search if [4,5] is inside a board of 3x3.
Function tested: is_in_board()
Outputs: False.
'''
def test_4_5_is_in_a_board_of_3x3():
    board = [[" "," ","C"],["Z"," "," "],[" ","Z"," "]]
    a_test = A_Star(board, vision=2, carrots=2, MaxLastMovements=2)
    result = a_test.is_in_board(x=4, y=5, board=board)
    assert result == False

'''
[A*] Search if [-2,-1] is inside a board of 3x3.
Function tested: is_in_board()
Outputs: False.
'''
def test_4_5_is_in_a_board_of_3x3():
    board = [[" "," ","C"],["Z"," "," "],[" ","Z"," "]]
    a_test = A_Star(board, vision=2, carrots=2, MaxLastMovements=2)
    result = a_test.is_in_board(x=-2, y=-1, board=board)
    assert result == False

'''
[A*] Search neighbors states of [2,2] in a board of 3x3.
Function tested: search_neighbors()
Outputs: A list containing every neighbor state. Neighbors = [1,2], [2,1]
'''
def test_neighbors_of_2_2():
    board = [[" "," ","C"],["Z"," "," "],[" ","Z"," "]]
    a_test = A_Star(board, vision=2, carrots=2, MaxLastMovements=2)
    neigbors = a_test.search_neighbors(current_state=[2,2], board=board)
    assert [2,1] in neigbors and [1,2] in neigbors

'''
[A*] Get the lower cost of states, each with a different cost. States=[[1,2],[2,2]]. Costs=[3,2]
Function tested: get_lower()
Outputs: A tuple containing the lower cost and the better state. (2,[2,2])
'''
def test_get_lower_cost_of_states_with_different_cost():
    board = [[" "," ","C"],["Z"," "," "],[" ","Z"," "]]
    a_test = A_Star(board, vision=2, carrots=2, MaxLastMovements=2)
    a_test.open = [[1,2],[2,2]]
    a_test.f = [3,2]
    best, next_state = a_test.get_lower()
    assert best == 2 and next_state == [2,2]

'''
[A*] Get the lower cost of states, each with the same cost. States=[[1,2],[2,2]]. Costs=[2,2]
Function tested: get_lower()
Requirements: This case is solved with randomness, a seed is put. (2)
Outputs: A tuple containing the lower cost and the better state. (2,[1,2])
'''
def test_get_lower_cost_of_states_with_same_cost():
    board = [[" "," ","C"],["Z"," "," "],[" ","Z"," "]]
    a_test = A_Star(board, vision=2, carrots=2, MaxLastMovements=2)
    a_test.set_random_seed(2)
    a_test.open = [[1,2],[2,2]]
    a_test.f = [2,2]
    best, next_state = a_test.get_lower()
    assert best == 2 and next_state == [1,2]

'''
[A*] Put a state in last movements. State=[1,2]
Function tested: put_Last_Movement()
Outputs: The list containing the last movements add the state.
'''
def test_put_state_in_last_movements():
    board = [[" "," ","C"],["Z"," "," "],[" ","Z"," "]]
    a_test = A_Star(board, vision=2, carrots=2, MaxLastMovements=2)
    a_test.put_Last_Movement([1,2])
    assert a_test.LastMovements[-1] == [1,2]

'''
[A*] Look for carrots in a 3x3 board with vision of 2.
Function tested: carrots_in_sight()
Outputs: A list containing the carrots in sight. 2 carrots in sight = [[1,0],[2,1]]
'''
def test_2_carrots_in_sight():
    board = [[" "," ","C"],["Z"," "," "],[" ","Z"," "]]
    a_test = A_Star(board, vision=2, carrots=2, MaxLastMovements=2)
    coordinates = a_test.carrots_in_sight(current_state=[0,2], board=board)
    assert coordinates == [[1,0],[2,1]]

'''
[A*] Look for carrots in a 3x3 board with vision of 1.
Function tested: carrots_in_sight()
Outputs: A list containing the carrots in sight. 0 carrots in sight = []
'''
def test_0_carrots_in_sight():
    board = [[" "," ","C"],["Z"," "," "],[" ","Z"," "]]
    a_test = A_Star(board, vision=1, carrots=2, MaxLastMovements=2)
    coordinates = a_test.carrots_in_sight(current_state=[0,2], board=board)
    assert coordinates == []

'''
[A*] Calculate h without consider carrots. States = [[0,1],[1,0],[2,1],[1,2]]
    Cases = [is last movement, been there lately, not passed, been there lately]
Function tested: h_without_carrots()
Outputs: A list containing the heuristic cost of every state. [10,5,1,5]
'''
def test_h_not_considering_carrots():
    board = [[" "," ","C"],["Z"," "," "],[" ","Z"," "]]
    a_test = A_Star(board, vision=1, carrots=2, MaxLastMovements=2)
    a_test.open = [[0,1],[1,0],[2,1],[1,2]]
    a_test.LastMovements = [[1,0],[1,2],[0,1]]
    h = a_test.h_without_carrots()
    assert h == [10,5,1,5]

'''
[A*] Calculate h without consider carrots. Current state = [0,2]. Possible States = [[0,1],[1,2]]
Function tested: h_with_carrots()
Outputs: A list containing the heuristic cost of every state. [3,1].
'''
def test_h_considering_carrots():
    board = [[" "," ","C"],["Z"," "," "],[" "," ","Z"]]
    a_test = A_Star(board, vision=2, carrots=2, MaxLastMovements=2)
    carrots_coordinates = a_test.carrots_in_sight(current_state=[0,2], board=board)
    a_test.open = [[0,1],[1,2]]
    h = a_test.h_with_carrots(carrots_coordinates, current=[0,2])
    assert h == [3,1]

'''
[A*] Calculate the cost for every possible state at start. Current state = [0,2]. Possible States = [[0,1],[1,2]]
Function tested: calculate_f_score()
Outputs: A list containing the total cost (g+h) of every state. [4,2].
'''
def test_total_cost():
    board = [[" "," ","C"],["Z"," "," "],[" "," ","Z"]]
    a_test = A_Star(board, vision=2, carrots=2, MaxLastMovements=2)
    a_test.open = [[0,1],[1,2]]
    a_test.calculate_f_score(current_state=[0,2], board=board)
    assert a_test.f == [4,2]

'''
[A*] Calculate the cost for every possible state after a movemnt. Current state = [1,2]. Possible States = [[0,2],[1,1],[2,2]]
Function tested: calculate_f_score()
Outputs: A list containing the total cost (g+h) of every state. [4,2].
'''
def test_total_cost():
    board = [[" "," ","C"],["Z"," "," "],[" "," ","Z"]]
    a_test = A_Star(board, vision=2, carrots=2, MaxLastMovements=2)
    a_test.g = 1
    a_test.open = [[0,2],[1,1],[2,2]]
    a_test.LastMovements = [[0,2]]
    a_test.calculate_f_score(current_state=[1,2], board=board)
    assert a_test.f == [15,4,3]
