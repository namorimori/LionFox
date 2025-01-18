import math

BLACK = 1
WHITE = 2

# 初期の盤面
board = [
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 1, 2, 0, 0],
    [0, 0, 2, 1, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
]

# 石を置く
def apply_move(board, stone, x, y):
    new_board = [row[:] for row in board]
    new_board[y][x] = stone

    opponent = 3 - stone
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        stones_to_flip = []

        while 0 <= nx < len(new_board[0]) and 0 <= ny < len(new_board) and new_board[ny][nx] == opponent:
            stones_to_flip.append((nx, ny))
            nx += dx
            ny += dy

        if stones_to_flip and 0 <= nx < len(new_board[0]) and 0 <= ny < len(new_board) and new_board[ny][nx] == stone:
            for flip_x, flip_y in stones_to_flip:
                new_board[flip_y][flip_x] = stone

    return new_board

# 有効な手を取得
def get_valid_moves(board, stone):
    valid_moves = []
    for y in range(len(board)):
        for x in range(len(board[0])):
            if can_place_x_y(board, stone, x, y):
                valid_moves.append((x, y))
    return valid_moves

# 手を置けるかチェック
def can_place_x_y(board, stone, x, y):
    if board[y][x] != 0:
        return False

    opponent = 3 - stone
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        found_opponent = False

        while 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == opponent:
            nx += dx
            ny += dy
            found_opponent = True

        if found_opponent and 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == stone:
            return True

    return False

# 評価関数（動的に調整）
def evaluate_board(board, stone, depth):
    # コーナーとエッジの強化
    weight = [
        [100, -10, 10, 10, -10, 100],
        [-10, -50, -2, -2, -50, -10],
        [10, -2, 5, 5, -2, 10],
        [10, -2, 5, 5, -2, 10],
        [-10, -50, -2, -2, -50, -10],
        [100, -10, 10, 10, -10, 100]
    ]
    score = 0
    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == stone:
                score += weight[y][x]

    # エンドゲームではコーナーの評価を高くする
    if depth <= 3:
        score *= 2  # 終盤においてコーナーを優先する

    # モビリティの評価
    my_moves = len(get_valid_moves(board, stone))
    opponent_moves = len(get_valid_moves(board, 3 - stone))
    score += (my_moves - opponent_moves) * 10

    # 安定石の評価
    stable_score = 0
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == stone:
                is_stable = True
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    while 0 <= nx < len(board[0]) and 0 <= ny < len(board):
                        if board[ny][nx] == 0:
                            is_stable = False
                            break
                        nx += dx
                        ny += dy
                    if not is_stable:
                        break
                if is_stable:
                    stable_score += 20
    score += stable_score

    # フロンティア石のペナルティ
    frontier_penalty = 0
    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == stone:
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == 0:
                        frontier_penalty += 5
                        break
    score -= frontier_penalty

    return score

# 手の順序を評価関数に基づいて並べ替え
def order_moves(board, stone, depth):
    valid_moves = get_valid_moves(board, stone)
    move_scores = []
    for x, y in valid_moves:
        temp_board = apply_move(board, stone, x, y)
        score = evaluate_board(temp_board, stone, depth)
        move_scores.append((score, (x, y)))
    return [move for _, move in sorted(move_scores, reverse=True)]

# ミニマックス法（深さを増加）
def minimax(board, stone, depth, maximizing_player, alpha=-math.inf, beta=math.inf):
    valid_moves = get_valid_moves(board, stone)

    # 終端条件: 深さ0またはこれ以上石を置けない場合
    if depth == 0 or not valid_moves:
        return evaluate_board(board, stone, depth)

    if maximizing_player:
        max_eval = -math.inf
        for x, y in order_moves(board, stone, depth):  # 手順を工夫
            new_board = apply_move(board, stone, x, y)
            eval = minimax(new_board, 3 - stone, depth - 1, False, alpha, beta)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # βカット
        return max_eval
    else:
        min_eval = math.inf
        for x, y in order_moves(board, stone, depth):  # 手順を工夫
            new_board = apply_move(board, stone, x, y)
            eval = minimax(new_board, 3 - stone, depth - 1, True, alpha, beta)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # αカット
        return min_eval

# FoxxxAI クラス（さらに強化）
class GorillaAI:

    def name(self):
        return "GorillaAI"

    def face(self):
        return "🦍"

    def place(self, board, stone):
        valid_moves = get_valid_moves(board, stone)
        if not valid_moves:
            return None

        # ゲームの進行状況に応じて探索深さを調整
        depth = 5 

        best_move = None
        best_score = -math.inf

        for x, y in order_moves(board, stone, depth):  # 手順を工夫
            temp_board = apply_move(board, stone, x, y)
            score = minimax(temp_board, 3 - stone, depth, maximizing_player=False)

            if score > best_score:
                best_score = score
                best_move = (x, y)

        return best_move
