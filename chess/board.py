import pygame
from .square import Square
from .constant import BOARD_SIZE, SQUARE_SIZE, WHITE
from .pieces.pawn import Pawn

class Board:
    """
    Represents the chess board and manages game state, piece movements, and game rules.
    Includes en passant capture functionality.
    """
    
    def __init__(self):
        self.squares = [[Square(row, col) for col in range(BOARD_SIZE)] 
                       for row in range(BOARD_SIZE)]
        self.selected_square = None
        self.current_player = WHITE
        self.captured_white_pieces = []  # Pieces captured by black
        self.captured_black_pieces = []  # Pieces captured by white
        self.valid_moves = []
        self.enpassant_move =[]
        self.last_move = None  # Track last move for en passant
        self._setup_pieces()
    
    def show_valid_moves(self, row, col):
        """
        Calculate and display valid moves for the piece at the given position.
        
        EN PASSANT LOGIC:
        - When a pawn is selected, check if en passant capture is available
        - En passant occurs when an enemy pawn just moved two squares forward
        - The capturing pawn must be on the 5th rank (for white) or 4th rank (for black)
        - The enemy pawn must be adjacent to the capturing pawn
        - The capture happens diagonally behind the enemy pawn
        
        Args:
            row: Row coordinate of the selected piece
            col: Column coordinate of the selected piece
        """
        piece = self.squares[row][col].piece
        
        if not piece:
            return
        
        # Clear previous valid moves
        self.valid_moves = []
        
        # Get valid moves based on piece type
        if hasattr(piece, 'get_valid_moves'):
            moves, capture_moves = piece.get_valid_moves(self, (row, col))
            
            # ============================================================================
            # EN PASSANT AVAILABILITY CHECK
            # ============================================================================
            if piece.name == 'pawn':
                # Check if this pawn can perform en passant capture
                en_passant_moves = self._get_available_en_passant_moves(piece, (row, col))
                
                # Add en passant moves to the list of possible captures
                # These will be displayed as special highlighted squares
                for en_passant_move in en_passant_moves:
                    capture_moves.append(en_passant_move)
                    self.enpassant_move.append((row,col))
                    print(f"♟️ En passant available for {piece.color} pawn at ({row},{col}) -> {en_passant_move}")
            # ============================================================================
            
            # Highlight regular moves (forward movement)
            for move_row, move_col in moves:
                target_square = self.squares[move_row][move_col]
                target_square.set_highlight('valid_move')
                self.valid_moves.append((move_row, move_col))
            
            # Highlight capture moves (including en passant)
            for move_row, move_col in capture_moves:
                print(f'enpassant moves available {capture_moves}')
                target_square = self.squares[move_row][move_col]
                # Check if this is an en passant move for special highlighting
                is_en_passant = self._is_en_passant_position((row, col), (move_row, move_col))
                if is_en_passant:
                    target_square.set_highlight('capture')
                    direction = 1 if piece.color == 'white' else -1
                    square_with_piece = self.squares[target_square.row + direction][move_col]
                    print(f'square_with_piece {square_with_piece}')
                    square_with_piece.set_highlight('en_passant')
                    print(f"🎯 En passant target highlighted at ({move_row},{move_col})")
                else:
                    target_square.set_highlight('capture')
                self.valid_moves.append((move_row, move_col))
    
    def _get_available_en_passant_moves(self, pawn, position):
        """
        Determine if en passant capture is available for the selected pawn.
        
        EN PASSANT CONDITIONS:
        1. Current piece must be a pawn
        2. Last move must be an enemy pawn moving two squares forward
        3. Current pawn must be on correct rank:
           - White pawns: must be on 4th rank (row 3 in 0-index)
           - Black pawns: must be on 5th rank (row 4 in 0-index)
        4. Enemy pawn must be adjacent to current pawn
        
        The en passant capture square is the empty square diagonally behind the enemy pawn.
        
        Args:
            pawn: The pawn piece being evaluated for en passant
            position: Tuple (row, col) of the pawn's current position
            
        Returns:
            List of (row, col) tuples representing en passant capture positions
        """
        row, col = position
        en_passant_moves = []
        
        # Debug information to track en passant logic
        print(f"🔍 Checking en passant for {pawn.color} pawn at ({row},{col})")
        if self.last_move:
            print(f"   Last move: {self.last_move['piece'].color} {self.last_move['piece'].name} from {self.last_move['from']} to {self.last_move['to']}")
        
        # CONDITION 1: Last move must exist and be a pawn move
        if not self.last_move or self.last_move['piece'].name != 'pawn':
            return en_passant_moves
        
        # CONDITION 2: Last move must be a double pawn move by an enemy
        last_move_piece = self.last_move['piece']
        if not (self.last_move['is_double_pawn_move'] and last_move_piece.color != pawn.color):
            return en_passant_moves
        
        # CONDITION 3: Current pawn must be on correct rank for en passant
        # White pawns can only capture en passant from the 4th rank
        # Black pawns can only capture en passant from the 5th rank
        correct_rank = (pawn.color == 'white' and row == 3) or (pawn.color == 'black' and row == 4)
        if not correct_rank:
            return en_passant_moves
        
        # CONDITION 4: Enemy pawn must be adjacent to current pawn
        last_to_row, last_to_col = self.last_move['to']
        if last_to_row == row and abs(last_to_col - col) == 1:
            # All conditions met! Calculate en passant capture position
            
            # Determine movement direction based on pawn color
            # White moves upward (decreasing row), black moves downward (increasing row)
            direction = -1 if pawn.color == 'white' else 1
            
            # The capture happens diagonally behind the enemy pawn
            en_passant_row = row + direction  # Move forward one square
            en_passant_col = last_to_col      # Capture in enemy pawn's column
            
            # Verify the target square is empty (it should be for en passant)
            if 0 <= en_passant_row < 8 and self.squares[en_passant_row][en_passant_col].is_empty():
                en_passant_moves.append((en_passant_row, en_passant_col))
                print(f"✅ En passant AVAILABLE! {pawn.color} pawn can capture to ({en_passant_row},{en_passant_col})")
        
        return en_passant_moves
    
    def _is_en_passant_move_pattern(self, from_square, to_square):
        """
        Verify if a move matches the pattern of an en passant capture during execution.
        
        This is used when the player actually makes a move to confirm it's en passant.
        The pattern is:
        - Pawn moving diagonally
        - Moving to an empty square
        - On the correct rank for en passant
        
        Args:
            from_square: Square the piece is moving from
            to_square: Square the piece is moving to
            
        Returns:
            Boolean indicating if this move matches en passant pattern
        """
        piece = from_square.piece
        
        # Must be a pawn moving diagonally to empty square
        if not piece or piece.name != 'pawn':
            return False
        
        from_row, from_col = from_square.row, from_square.col
        to_row, to_col = to_square.row, to_square.col
        
        # Must be moving diagonally to empty square
        if not (abs(from_col - to_col) == 1 and to_square.is_empty()):
            return False
        
        # Must be on correct rank for en passant
        if not ((piece.color == 'white' and from_row == 3) or 
                (piece.color == 'black' and from_row == 4)):
            return False
        
        return True
    
    def _is_en_passant_position(self, from_pos, to_pos):
        """
        Identify if a move position represents an en passant capture for highlighting.
        
        Used to apply special visual highlighting to en passant target squares.
        
        Args:
            from_pos: Tuple (row, col) of starting position
            to_pos: Tuple (row, col) of target position
            
        Returns:
            Boolean indicating if this is an en passant position
        """
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # En passant is always diagonal movement to an empty square
        return (abs(from_col - to_col) == 1 and 
                self.squares[to_row][to_col].is_empty())

    def move_piece(self, from_square, to_square, is_en_passant=False):
        """
        Execute a piece move, handling both regular captures and en passant captures.
        
        EN PASSANT EXECUTION:
        - For en passant, the captured pawn is not on the target square
        - The captured pawn is on the same rank as the moving pawn, adjacent column
        - Remove the enemy pawn from the board diagonally behind the target
        
        Args:
            from_square: Square to move piece from
            to_square: Square to move piece to
            is_en_passant: Boolean indicating if this is an en passant capture
            
        Returns:
            The captured piece, if any
        """
        captured_piece = None
        
        # ============================================================================
        # EN PASSANT CAPTURE EXECUTION
        # ============================================================================
        if is_en_passant:
            # Determine movement direction based on pawn color
            direction = 1 if from_square.piece.color == 'white' else -1
            
            # The pawn being captured is diagonally behind the target square
            captured_row = to_square.row
            captured_square = self.squares[captured_row][to_square.col]
            square_with_piece = self.squares[captured_square.row + direction][to_square.col]
            captured_piece = square_with_piece.piece
            
            # Remove the captured pawn from the board
            square_with_piece.clear()
        else:
            # Regular capture - piece is on the target square
            captured_piece = to_square.piece
        # ============================================================================
        
        # Update pawn movement tracking
        if from_square.piece and from_square.piece.name == 'pawn':
            from_square.piece.has_moved = True
        
        # Move the piece to the new square
        to_square.set_piece(from_square.piece)
        from_square.clear()
        
        return captured_piece

    def _update_last_move(self, piece, from_position, to_position, captured_piece):
        """
        Record the last move for en passant tracking.
        
        Stores information about the move including whether it was a double pawn move,
        which is essential for enabling en passant on the next turn.
        
        Args:
            piece: The piece that was moved
            from_position: Tuple (row, col) of starting position
            to_position: Tuple (row, col) of ending position  
            captured_piece: Piece that was captured, if any
        """
        self.last_move = {
            'piece': piece,
            'from': from_position,
            'to': to_position,
            'is_double_pawn_move': self._is_double_pawn_move(from_position, to_position),
            'captured_piece': captured_piece
        }
        print(f"📝 Last move updated: {piece.color} {piece.name} from {from_position} to {to_position}")

    def _is_double_pawn_move(self, from_position, to_position):
        """
        Check if a pawn move was a double-step move from its starting position.
        
        This is used to track when en passant becomes available for the opponent.
        
        Args:
            from_position: Tuple (row, col) of starting position
            to_position: Tuple (row, col) of ending position
            
        Returns:
            Boolean indicating if this was a double pawn move
        """
        from_row, to_row = from_position[0], to_position[0]
        return abs(from_row - to_row) == 2

    # ... rest of your existing methods remain unchanged ...
    
    def _setup_pieces(self):
        """Set up all chess pieces in their standard starting positions."""
        from .pieces.knight import Knight
        from .pieces.bishop import Bishop
        from .pieces.rook import Rook
        from .pieces.queen import Queen
        from .pieces.king import King

        # Set up pawns
        for col in range(BOARD_SIZE):
            self.squares[1][col].set_piece(Pawn('black'))  # Black pawns on row 1
            self.squares[6][col].set_piece(Pawn('white'))  # White pawns on row 6

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
    
    def handle_click(self, pos):
        """
        Handle mouse click events on the board.
        """
        row, col = self.get_board_position(pos)
        if row is None or col is None:
            return None
        
        clicked_square = self.squares[row][col]

        # Clicked on empty square that's not a valid move - clear selection
        if clicked_square.is_empty() and (row, col) not in self.valid_moves:
            self.clear_cache()
            return None
        
        # No piece selected yet - select this piece if it belongs to current player
        if not self.selected_square and self.is_current_player_piece(clicked_square.piece):
            self.selected_square = clicked_square
            clicked_square.set_highlight('selected')
            self.show_valid_moves(row, col)
            return ('piece_selected', clicked_square.piece)
        else:
            # Clicked on already selected piece - deselect it
            if self.selected_square == clicked_square:
                self.clear_cache()
                return None
            
            # Clicked on a different square with selected piece active
            elif self.selected_square and clicked_square:
                # Clicked on a valid move square - execute the move
                if (row, col) in self.valid_moves:
                    # Check if this is an en passant move (based on the move pattern)
                    is_en_passant = self._is_en_passant_move_pattern(self.selected_square, clicked_square)
                    
                    # Store piece reference BEFORE moving
                    moving_piece = self.selected_square.piece
                    from_position = (self.selected_square.row, self.selected_square.col)
                    
                    # Move the piece
                    captured_piece = self.move_piece(self.selected_square, clicked_square, is_en_passant)
                    
                    # Update last move information
                    self._update_last_move(moving_piece, from_position, (row, col), captured_piece)
                    
                    self.clear_cache()
                    if captured_piece:
                        self.add_captured_piece(captured_piece)
                    self.switch_player()
                    return None
                
                # Clicked on a different piece of same color - select the new piece
                elif self.selected_square and self.is_current_player_piece(clicked_square.piece):
                    self.clear_cache()
                    self.selected_square = clicked_square
                    clicked_square.set_highlight('selected')
                    self.show_valid_moves(row=row, col=col)
                    return None
                
                # Invalid click - clear selection
                else:
                    self.clear_cache()
                    return None
    
    # REST OF YOUR METHODS REMAIN THE SAME
    def clear_cache(self):
        self.clear_highlights()
        self.selected_square = None

    def add_captured_piece(self, captured_piece):
        if captured_piece.color == 'white':
            self.captured_white_pieces.append(captured_piece)
        else:
            self.captured_black_pieces.append(captured_piece)
        print(f"Captured: {captured_piece.color} {captured_piece.name}")

    def switch_player(self):
        if self.current_player == 'white':
            self.current_player = 'black'
        else:
            self.current_player = 'white'
        print(f"Now it's {self.current_player}'s turn")

    def clear_highlights(self):
        self.valid_moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                self.squares[row][col].clear_highlight()

    def is_current_player_piece(self, piece):
        return piece and piece.color == self.current_player
    
    def get_board_position(self, pos):
        x, y = pos
        col = x // SQUARE_SIZE
        row = y // SQUARE_SIZE
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return row, col
        return None, None
    
    def get_square(self, row, col):
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return self.squares[row][col]
        return None
    
    def draw(self, screen):
        screen.fill((50, 50, 50))
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                self.squares[row][col].draw(screen)
        self._draw_grid(screen)
    
    def _draw_grid(self, screen):
        for i in range(BOARD_SIZE + 1):
            pygame.draw.line(screen, (0, 0, 0), 
                           (i * SQUARE_SIZE, 0), 
                           (i * SQUARE_SIZE, BOARD_SIZE * SQUARE_SIZE), 2)
            pygame.draw.line(screen, (0, 0, 0),
                           (0, i * SQUARE_SIZE),
                           (BOARD_SIZE * SQUARE_SIZE, i * SQUARE_SIZE), 2)