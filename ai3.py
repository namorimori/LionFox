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

# 評価関数（改良版）
def evaluate_board(board, stone, depth):
    weight = [
        [100, -10, 10, 10, -10, 100],
        [-10, -50, -2, -2, -50, -10],
        [10, -2, 5, 5, -2, 10],
        [10, -2, 5, 5, -2, 10],
        [-10, -50, -2, -2, -50, -10],
        [100, -10, 10, 10, -10, 100]
    ]

    mobility = len(get_valid_moves(board, stone)) - len(get_valid_moves(board, 3 - stone))
    stable_stones = 0
    frontier_stones = 0

    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == stone:
                stable_stones += weight[y][x]
                if any(0 <= x + dx < len(board[0]) and 0 <= y + dy < len(board) and board[y + dy][x + dx] == 0 for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]):
                    frontier_stones += 1

    # 一番外がわから一つ手前の場所の評価を低くする
    edge_penalty = 0
    for y in range(1, len(board) - 1):
        for x in range(1, len(board[0]) - 1):
            if y in [1, len(board) - 2] or x in [1, len(board[0]) - 2]:
                if board[y][x] == stone:
                    edge_penalty += 20

    score = stable_stones + mobility - frontier_stones - edge_penalty
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

# ミニマックス法（深さを5に固定）
def minimax(board, stone, depth, maximizing_player, alpha=-math.inf, beta=math.inf):
    valid_moves = get_valid_moves(board, stone)

    # 終端条件: 深さ0またはこれ以上石を置けない場合
    if depth == 0 or not valid_moves:
        return evaluate_board(board, stone, depth)

    if maximizing_player:
        max_eval = -math.inf
        for x, y in order_moves(board, stone, depth):
            new_board = apply_move(board, stone, x, y)
            eval = minimax(new_board, 3 - stone, depth - 1, False, alpha, beta)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # βカット
        return max_eval
    else:
        min_eval = math.inf
        for x, y in order_moves(board, stone, depth):
            new_board = apply_move(board, stone, x, y)
            eval = minimax(new_board, 3 - stone, depth - 1, True, alpha, beta)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # αカット
        return min_eval

# DogAI クラス（さらに強化）
class EagleAI:

    def name(self):
        return "EagleAI"

    def face(self):
        return "🐓"

    def place(self, board, stone):
        valid_moves = get_valid_moves(board, stone)
        if not valid_moves:
            return None

        # 探索深さは常に5に設定
        depth = 5

        best_move = None
        best_score = -math.inf

        for x, y in order_moves(board, stone, depth):
            temp_board = apply_move(board, stone, x, y)
            score = minimax(temp_board, 3 - stone, depth, False)

            if score > best_score:
                best_score = score
                best_move = (x, y)

        return best_move
