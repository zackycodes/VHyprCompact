# M30
A custom chess engine implemented in Python that utilizes the python-chess library for move validation and board state management
This engine employs a Minimax algorithm with Alpha-Beta pruning and uses Piece-Square Tables (PST) for position-based evaluation

## ✨ Features
* Search Algorithm: Implements a Minimax search with Alpha-Beta pruning to find the optimal move within a specified depth
* Move Ordering: Optimizes the search process by ordering moves before evaluation to improve pruning efficiency

* Evaluation System:
  * __Material Weighting__: Assigns standard values to pieces (e.g., Pawn: 100, Queen: 900, King: 20,000)
  * __Piece-Square Tables (PST)__: Uses specialized tables to encourage pieces to occupy strategically advantageous squares
  * __Endgame Logic__: Automatically detects endgame states to transition the King's behavior from defensive to active positioning

* Efficiency Optimizations:
  * __Zobrist Hashing__: Generates unique hash keys for board positions to allow for fast lookups
  * __Transposition Table__: Stores previously evaluated positions to avoid redundant calculations

* __Dual Interface__: Supports both a standard command-line interface (CLI) and the Universal Chess Interface (UCI) protocol for use with external chess GUIs

## 🔲 Piece-Square Tables (PST)

The engine applies specific evaluation mappings for every piece type to determine the "value" of a square
* __Pawns__: Encouraged to advance and occupy the center
* __Knights__: Penalized for being on the edges of the board
* __Bishops__: Encouraged to stay off the back rank and control diagonals
* __Rooks__: Incentivized to occupy the 7th rank and central files
* __Kings__: In the mid-game, the engine prioritizes king safety (corners); in the endgame, it shifts to a table that encourages the king to participate in the center


## ❔ How to Use

### Requirements
* Python 3.x
* python-chess library

### Running the Engine
You can run the engine in two different modes:
1) __Command Line Interface (CLI)__: Play directly against the engine in your terminal.
2) You can specify the search depth using the --depth flag (default is 3)
3) __UCI Mode__: To use the engine with a GUI (like Arena or Cute Chess), use the --uci flag

## Notes
Good Luck!
talk(): Handles UCI communication protocol
.
