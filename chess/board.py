import pygame
from .square import Square
from .constant import BOARD_SIZE, SQUARE_SIZE,WHITE
from .pieces.pawn import Pawn

class Board:
    def __init__(self):
        self.squares = [[Square(row, col) for col in range(BOARD_SIZE)] 
                       for row in range(BOARD_SIZE)]
        self.selected_square = None
        self.current_player = WHITE
        self.captured_white_pieces = []  # Pieces captured by black
        self.captured_black_pieces = []  # Pieces captured by white
        self.valid_moves = []
        self._setup_pieces()
    
    def _setup_pieces(self):
        """Set up all chess pieces in their standard starting positions"""
        from .pieces.knight import Knight
        from .pieces.bishop import Bishop
        from .pieces.rook import Rook
        from .pieces.queen import Queen
        from .pieces.king import King

        # Set up pawns
        for col in range(BOARD_SIZE):
            # Black pawns on row 1 (rank 7 in chess notation)
            self.squares[1][col].set_piece(Pawn('black'))
            # White pawns on row 6 (rank 2 in chess notation)
            self.squares[6][col].set_piece(Pawn('white'))

        # Set up black pieces (row 0)
        self.squares[0][0].set_piece(Rook('black'))    # a8
        self.squares[0][1].set_piece(Knight('black'))  # b8
        self.squares[0][2].set_piece(Bishop('black'))  # c8
        self.squares[0][3].set_piece(Queen('black'))   # d8
        self.squares[0][4].set_piece(King('black'))    # e8
        self.squares[0][5].set_piece(Bishop('black'))  # f8
        self.squares[0][6].set_piece(Knight('black'))  # g8
        self.squares[0][7].set_piece(Rook('black'))    # h8

        # Set up white pieces (row 7)
        self.squares[7][0].set_piece(Rook('white'))    # a1
        self.squares[7][1].set_piece(Knight('white'))  # b1
        self.squares[7][2].set_piece(Bishop('white'))  # c1
        self.squares[7][3].set_piece(Queen('white'))   # d1
        self.squares[7][4].set_piece(King('white'))    # e1
        self.squares[7][5].set_piece(Bishop('white'))  # f1
        self.squares[7][6].set_piece(Knight('white'))  # g1
        self.squares[7][7].set_piece(Rook('white'))    # h1
    
    def get_square(self, row, col):
        """Get square at position"""
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return self.squares[row][col]
        return None
    
    def draw(self, screen):
        """Draw the entire board"""
        # Fill background
        screen.fill((50, 50, 50))  # Dark gray background
        
        # Draw all squares and pieces
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                self.squares[row][col].draw(screen)
        
        # Draw grid lines (optional)
        self._draw_grid(screen)
    
    def _draw_grid(self, screen):
        """Draw grid lines between squares"""
        for i in range(BOARD_SIZE + 1):
            # Vertical lines
            pygame.draw.line(screen, (0, 0, 0), 
                           (i * SQUARE_SIZE, 0), 
                           (i * SQUARE_SIZE, BOARD_SIZE * SQUARE_SIZE), 2)
            # Horizontal lines  
            pygame.draw.line(screen, (0, 0, 0),
                           (0, i * SQUARE_SIZE),
                           (BOARD_SIZE * SQUARE_SIZE, i * SQUARE_SIZE), 2)
    
    def handle_click(self,pos):
        row, col = self.get_board_position(pos)
        if row is None or col is None:
            return None
        
        clicked_square = self.squares[row][col]

        if clicked_square.is_empty() and (row, col) not in self.valid_moves:
            self.clear_cache()
            return None
        # print(f'Clicked square: {clicked_square}, Turn: {self.current_player}')
        if not self.selected_square and self.is_current_player_piece(clicked_square.piece):
            # select for the piece on current player move if they have not selected 
            self.selected_square = clicked_square
            clicked_square.set_highlight('selected')
            self.show_valid_moves(row,col)
            return ('piece_selected', clicked_square.piece)
        else:
            if self.selected_square == clicked_square:
                # if same selected square is pressed
                self.clear_cache()
                return None
            elif self.selected_square and clicked_square:
                if (row, col) in self.valid_moves:
                # Click is on a diffrent valid square
                    captured_piece = self.move_piece(self.selected_square, clicked_square)
                    self.clear_cache()
                    if captured_piece:
                        self.add_captured_piece(captured_piece)
                    self.switch_player()
                    return None
                elif self.selected_square and self.is_current_player_piece(clicked_square.piece):
                    # click is on diff piece for current player
                    self.clear_cache()
                    self.selected_square = clicked_square
                    clicked_square.set_highlight('selected')
                    self.show_valid_moves(row=row,col=col)
                    return None
                else:
                    # click isn't on a valid move
                    self.clear_cache()
                    return None
    
    def clear_cache(self):
        self.clear_highlights()
        self.selected_square = None

    def add_captured_piece(self, captured_piece):
        """Add captured piece to the appropriate player's captured pieces list"""
        if captured_piece.color == 'white':
            self.captured_white_pieces.append(captured_piece)
        else:
            self.captured_black_pieces.append(captured_piece)
        
        print(f"Captured: {captured_piece.color} {captured_piece.name}")

    def move_piece(self, from_square, to_square):
        """Move piece from one square to another and return captured piece if any"""
        # pawn move
        if from_square.piece and isinstance(from_square.piece, Pawn):
            from_square.piece.has_moved = True
        # Store the captured piece (if any)
        captured_piece = to_square.piece
        
        # Move the piece
        to_square.set_piece(from_square.piece)
        from_square.clear()
        
        return captured_piece

    def switch_player(self):
        """Switch to the other player's turn"""
        if self.current_player == 'white':
            self.current_player = 'black'
        else:
            self.current_player = 'white'
        
        print(f"Now it's {self.current_player}'s turn")

    def clear_highlights(self):
        """Clear all highlights and valid moves"""
        self.valid_moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                self.squares[row][col].clear_highlight()

    def show_valid_moves(self, row, col):
        """Show valid moves for piece at position"""
        piece = self.squares[row][col].piece
        
        if not piece:
            return
        
        # Clear previous valid moves
        self.valid_moves = []
        
        # Get valid moves based on piece type
        if hasattr(piece, 'get_valid_moves'):
            moves, capture_moves = piece.get_valid_moves(self, (row, col))
            
            # Highlight regular moves
            for move_row, move_col in moves:
                target_square = self.squares[move_row][move_col]
                target_square.set_highlight('valid_move')
                self.valid_moves.append((move_row, move_col))
            
            # Highlight capture moves
            for move_row, move_col in capture_moves:
                target_square = self.squares[move_row][move_col]
                target_square.set_highlight('capture')
                self.valid_moves.append((move_row, move_col))

    def is_current_player_piece(self, piece):
        """Check if piece belongs to current player"""
        return piece.color == self.current_player
    
    def get_board_position(self, pos):
        """Convert screen coordinates to board position"""
        x, y = pos
        col = x // SQUARE_SIZE
        row = y // SQUARE_SIZE
        
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return row, col
        return None, None