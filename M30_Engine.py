import chess
import argparse
import time
import sys
from typing import Dict, List, Any

# piece evaluation values
piece_value = {
    chess.PAWN: 100,
    chess.ROOK: 500,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# PST

# pawn eval
pawnEvalWhite = [    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, -20, -20, 10, 10, 5,
    5, -5, -10, 0, 0, -10, -5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, 5, 10, 25, 25, 10, 5, 5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0, 0, 0, 0, 0, 0, 0, 0]

pawnEvalBlack = list(reversed(pawnEvalWhite))

# knight eval

knightEval = [    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50]

# bishop eval

bishopEvalWhite = [    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20]

bishopEvalBlack = list(reversed(bishopEvalWhite))

# rook eval
rookEvalWhite = [    0, 0, 0, 5, 5, 0, 0, 0,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    5, 10, 10, 10, 10, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0]

rookEvalBlack = list(reversed(rookEvalWhite))

# queen eval
queenEval = [    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -5, 0, 5, 5, 5, 5, 0, -5,
    0, 0, 5, 5, 5, 5, 0, -5,
    -10, 5, 5, 5, 5, 5, 0, -10,
    -10, 0, 5, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20]

# king eval
kingEvalWhite = [    20, 30, 10, 0, 0, 10, 30, 20,
    20, 20, 0, 0, 0, 0, 20, 20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30]
kingEvalBlack = list(reversed(kingEvalWhite))

# king eval endgame
kingEvalEndGameWhite = [    50, -30, -30, -30, -30, -30, -30, -50,
    -30, -30, 0, 0, 0, 0, -30, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -20, -10, 0, 0, -10, -20, -30,
    -50, -40, -30, -20, -20, -30, -40, -50]
kingEvalEndGameBlack = list(reversed(kingEvalEndGameWhite))

debug_info: Dict[str, Any] = {}

MATE_SCORE = 1000000000
MATE_THRESHOLD = 999000000

# Transposition table
transposition_table: Dict[int, tuple] = {}
MAX_TABLE_SIZE = 1000000  # Adjust as needed

# Zobrist hashing
zobrist_keys = {}

def init_zobrist():
    """Initializes the Zobrist keys."""
    for piece_type in chess.PIECE_TYPES:
        zobrist_keys[piece_type] = {}
        for color in chess.COLORS:
            zobrist_keys[piece_type][color] = {}
            for square in chess.SQUARES:
                zobrist_keys[piece_type][color][square] =  hash(str(piece_type) + str(color) + str(square))

    zobrist_keys[chess.KING][chess.WHITE][chess.A1] = hash("castling_white")
    zobrist_keys[chess.KING][chess.WHITE][chess.H1] = hash("castling_white")
    zobrist_keys[chess.KING][chess.BLACK][chess.A8] = hash("castling_black")
    zobrist_keys[chess.KING][chess.BLACK][chess.H8] = hash("castling_black")

def zobrist_hash(board: chess.Board) -> int:
    """Calculates the Zobrist hash of a chess position."""
    hash_value = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            hash_value ^= zobrist_keys[piece.piece_type][piece.color][square]

    hash_value ^= zobrist_keys[chess.KING][chess.WHITE][chess.A1] if board.has_kingside_castling_rights(chess.WHITE) else 0
    hash_value ^= zobrist_keys[chess.KING][chess.WHITE][chess.H1] if board.has_queenside_castling_rights(chess.WHITE) else 0
    hash_value ^= zobrist_keys[chess.KING][chess.BLACK][chess.A8] if board.has_kingside_castling_rights(chess.BLACK) else 0
    hash_value ^= zobrist_keys[chess.KING][chess.BLACK][chess.H8] if board.has_queenside_castling_rights(chess.BLACK) else 0

    hash_value ^= zobrist_keys[chess.PAWN][chess.WHITE][chess.A1] if board.turn == chess.WHITE else 0
    hash_value ^= zobrist_keys[chess.PAWN][chess.BLACK][chess.A8] if board.turn == chess.BLACK else 0

    return hash_value

# main f() for the game and communication
def start():
    board = chess.Board()
    user_side = chess.WHITE if input("Start as [w]hite or [b]lack:\n").lower() == "w" else chess.BLACK

    if user_side == chess.WHITE:
        print(render(board))
        board.push(get_move(board))

    while not board.is_game_over():
        board.push(next_move(get_depth(), board, debug=False))
        print(render(board))
        board.push(get_move(board))

    print(f"\nResult: [w] {board.result()} [b]")


def render(board: chess.Board) -> str:
    ascii_pieces = {
        "R": "R", "N": "N", "B": "B", "Q": "Q", "K": "K", "P": "P",
        "r": "r", "n": "n", "b": "b", "q": "q", "k": "k", "p": "p",
        ".": "."
    }

    board_string = str(board).split('\n')
    translated_board = [''.join(ascii_pieces.get(char, char) for char in line) for line in board_string]
    ranks = ["8", "7", "6", "5", "4", "3", "2", "1"]

    if board.turn == chess.BLACK:
        translated_board.reverse()
        ranks.reverse()

    display = [f"  {rank} {line}" for rank, line in zip(ranks, translated_board)]
    display.append("    a b c d e f g h")
    return "\n".join(display)


def get_move(board: chess.Board) -> chess.Move:
    move = input(f"\nYour move (e.g. {list(board.legal_moves)[0]}):\n")
    for legal_move in board.legal_moves:
        if move == str(legal_move):
            return legal_move
    return get_move(board)


def get_depth() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", default=3, help="provide an integer (default: 3)")
    args = parser.parse_args()
    return max([1, int(args.depth)])


# mov gen + eval
def next_move(depth: int, board: chess.Board, debug=True) -> chess.Move:
    debug_info.clear()
    debug_info["nodes"] = 0
    t0 = time.time()

    move = minimax_root(depth, board)

    debug_info["time"] = time.time() - t0
    if debug:
        print(f"info {debug_info}")
    return move

    print(f"Pruning Count: {pruning_count}")  # Print the counter
    return move


def get_ordered_moves(board: chess.Board) -> List[chess.Move]:
    end_game = check_end_game(board)

    def orderer(move):
        return move_value(board, move, end_game)

    in_order = sorted(
        board.legal_moves, key=orderer, reverse=(board.turn == chess.WHITE)
    )
    return list(in_order)


#HYPER OPTIMIZED
def minimax_root(depth: int, board: chess.Board) -> chess.Move:
    maximize = board.turn == chess.WHITE
    best_move = -float("inf") if maximize else float("inf")
    moves = get_ordered_moves(board)
    best_move_found = moves[0]  # define best_move_found here


    for move in moves:
        board.push(move)
        value = minimax(depth - 1, board, -float("inf"), float("inf"), not maximize, best_move_found) if not board.can_claim_draw() else 0.0
        board.pop()

        if maximize and value >= best_move:
            best_move = value
            best_move_found = move
        elif not maximize and value <= best_move:
            best_move = value
            best_move_found = move

    return best_move_found



def minimax(depth, board, alpha, beta, maximize, best_move_found):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximize:
        max_eval = -float("inf")
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(depth - 1, board, alpha, beta, False, best_move_found)
            board.pop()
            if eval > max_eval:
                max_eval = eval
                best_move_found = move  # Update the best move found so far
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float("inf")
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(depth - 1, board, alpha, beta, True, best_move_found)
            board.pop()
            if eval < min_eval:
                min_eval = eval
                best_move_found = move  # Update the best move found so far
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval



# Evaluation functions
# update log - breh
def move_value(board: chess.Board, move: chess.Move, endgame: bool) -> float:
    if move.promotion:
        return float("inf") if board.turn == chess.WHITE else -float("inf")

    piece = board.piece_at(move.from_square)
    from_value = evaluate_piece(piece, move.from_square, endgame)
    to_value = evaluate_piece(piece, move.to_square, endgame)
    position_change = to_value - from_value

    capture_value = evaluate_capture(board, move) if board.is_capture(move) else 0
    move_value = capture_value + position_change

    return move_value if board.turn == chess.WHITE else -move_value


def evaluate_capture(board: chess.Board, move: chess.Move) -> float:
    if board.is_en_passant(move):
        return piece_value[chess.PAWN]

    to_piece = board.piece_at(move.to_square)
    from_piece = board.piece_at(move.from_square)

    return piece_value[to_piece.piece_type] - piece_value[from_piece.piece_type]


def evaluate_piece(piece: chess.Piece, square: chess.Square, end_game: bool) -> int:
    if piece.piece_type == chess.PAWN:
        mapping = pawnEvalWhite if piece.color == chess.WHITE else pawnEvalBlack
    elif piece.piece_type == chess.KNIGHT:
        mapping = knightEval
    elif piece.piece_type == chess.BISHOP:
        mapping = bishopEvalWhite if piece.color == chess.WHITE else bishopEvalBlack
    elif piece.piece_type == chess.ROOK:
        mapping = rookEvalWhite if piece.color == chess.WHITE else rookEvalBlack
    elif piece.piece_type == chess.QUEEN:
        mapping = queenEval
    elif piece.piece_type == chess.KING:
        if piece.color == chess.WHITE:
            mapping = kingEvalEndGameWhite if end_game else kingEvalWhite
        else:
            mapping = kingEvalEndGameBlack if end_game else kingEvalBlack

    return mapping[square]


def evaluate_board(board: chess.Board) -> float:
    total = 0
    end_game = check_end_game(board)

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_score = piece_value[piece.piece_type] + evaluate_piece(piece, square, end_game)
            total += piece_score if piece.color == chess.WHITE else -piece_score

    return total


def check_end_game(board: chess.Board) -> bool:
    queens = sum(1 for square in chess.SQUARES if (piece := board.piece_at(square)) and piece.piece_type == chess.QUEEN)
    minors = sum(1 for square in chess.SQUARES if (piece := board.piece_at(square)) and piece.piece_type in {chess.BISHOP, chess.KNIGHT})

    return queens == 0 or (queens == 2 and minors <= 1)

#chiru
#communication function for engine interface
def talk():
    board = chess.Board()
    depth = get_depth()

    while True:
        msg = input()
        command(depth, board, msg)


def command(depth: int, board: chess.Board, msg: str):
    msg = msg.strip()
    tokens = msg.split(" ")
    tokens = [token for token in tokens if token]

    if msg == "quit":
        sys.exit()
    elif msg == "isready":
        print("readyok")
    elif msg == "ucinewgame":
        return
    elif msg.startswith("position"):
        board.set_fen(parse_position(tokens))
    elif msg.startswith("go"):
        print(f"bestmove {next_move(depth, board)}")
    elif msg == "uci":
        print(f"id name YourEngineName")
        print(f"id author YourName")
        print(f"uciok")
    else:
        print(f"Unknown command: {msg}")


def parse_position(tokens: List[str]) -> str:
    if tokens[1] == "startpos":
        moves = tokens[3:] if len(tokens) > 2 else []
        board = chess.Board()

        for move in moves:
            board.push_uci(move)

        return board.fen()

    return " ".join(tokens[1:])


if __name__ == "__main__":
    init_zobrist()
    if "--uci" in sys.argv:
        talk()
    else:
        start()

# 
# nahhh i spent way too long for this 100 elo ahh bot