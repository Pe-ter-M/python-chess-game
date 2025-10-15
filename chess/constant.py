# chess/constants.py

# Colors
WHITE = 'white'
BLACK = 'black'
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT = (246, 246, 105, 150)  # Added alpha for transparency
MOVE_HIGHLIGHT = (106, 190, 48, 150)

# Board dimensions
BOARD_SIZE = 8
SQUARE_SIZE = 80
BOARD_PX = BOARD_SIZE * SQUARE_SIZE
MARGIN = 50

# Window dimensions
WINDOW_WIDTH = BOARD_PX + 2 * MARGIN
WINDOW_HEIGHT = BOARD_PX + 2 * MARGIN

# Piece types
PAWN = 'pawn'
ROOK = 'rook'
KNIGHT = 'knight'
BISHOP = 'bishop'
QUEEN = 'queen'
KING = 'king'

# Piece colors
PIECE_WHITE = 'white'
PIECE_BLACK = 'black'

# Game states
STATE_WHITE_TURN = 'white_turn'
STATE_BLACK_TURN = 'black_turn'
STATE_GAME_OVER = 'game_over'

# highlight colors
HIGHLIGHT_COLORS = {
    'selected': (106, 190, 48, 200),     # Green for selected piece
    'valid_move': (106, 190, 48, 150),   # Green for valid moves
    'capture': (255, 50, 50, 200),       # Red for capture moves
    'check': (255, 0, 0, 100)            # Red background for check
}