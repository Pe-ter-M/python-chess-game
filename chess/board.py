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

        # ============================================================================
    # CHECK AND CHECKMATE DETECTION METHODS
    # ============================================================================
    def can_castle(self, color, side):
            """
            Check if castling is possible for the specified color and side.
            
            Castling conditions:
            1. King and rook haven't moved
            2. No pieces between king and rook
            3. King is not in check
            4. King doesn't move through check
            
            Args:
                color: 'white' or 'black'
                side: 'king' (short) or 'queen' (long) side
                
            Returns:
                Boolean indicating if castling is possible
            """
            row = 7 if color == 'white' else 0
            king_col = 4
            rook_col = 7 if side == 'king' else 0
            
            king_square = self.squares[row][king_col]
            rook_square = self.squares[row][rook_col]
            
            # 1. Check if pieces exist and haven't moved
            if (king_square.is_empty() or rook_square.is_empty() or not king_square.piece or
                king_square.piece.name != 'king' or not rook_square.piece or rook_square.piece.name != 'rook' or
                king_square.piece.has_moved or rook_square.piece.has_moved):
                return False
            
            # 2. Check if king is in check
            if self.is_in_check(color):
                return False
            
            # 3. Check if squares between are empty
            if side == 'king':
                for col in range(5, 7):  # f1 and g1 for white
                    if not self.squares[row][col].is_empty():
                        return False
            else:  # queen side
                for col in range(1, 4):  # b1, c1, d1 for white
                    if not self.squares[row][col].is_empty():
                        return False
            
            # 4. Check if king moves through check
            if side == 'king':
                # Check if f1 (for white) is under attack
                if self._is_square_under_attack((row, 5), color):
                    return False
            else:  # queen side
                # Check if c1 and d1 (for white) are under attack
                if (self._is_square_under_attack((row, 2), color) or 
                    self._is_square_under_attack((row, 3), color)):
                    return False
            
            return True
    
    def _is_square_under_attack(self, position, defender_color):
        """
        Check if a square is under attack by enemy pieces.
        
        Args:
            position: Tuple (row, col) of square to check
            defender_color: Color of the defending player
            
        Returns:
            Boolean indicating if square is under attack
        """
        attacker_color = 'black' if defender_color == 'white' else 'white'
        
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                square = self.squares[row][col]
                if (not square.is_empty() and square.piece and 
                    square.piece.color == attacker_color):
                    moves, captures = square.piece.get_valid_moves(self, (row, col))
                    if position in captures:
                        return True
        return False
    
    def execute_castle(self, color, side):
        """
        Execute castling move.
        
        Args:
            color: 'white' or 'black'
            side: 'king' (short) or 'queen' (long) side
        """
        row = 7 if color == 'white' else 0
        
        if side == 'king':
            # Move king from e1 to g1, rook from h1 to f1
            king_from_col, king_to_col = 4, 6
            rook_from_col, rook_to_col = 7, 5
        else:  # queen side
            # Move king from e1 to c1, rook from a1 to d1
            king_from_col, king_to_col = 4, 2
            rook_from_col, rook_to_col = 0, 3
        
        # Move king
        square_King = self.squares[row][king_from_col]
        if square_King.piece:
            king = square_King.piece
            self.squares[row][king_to_col].set_piece(king)
            self.squares[row][king_from_col].clear()
            king.has_moved = True
        
        # Move rook
        square_ = self.squares[row][rook_from_col]
        if square_.piece:
            rook = square_.piece
            self.squares[row][rook_to_col].set_piece(rook)
            self.squares[row][rook_from_col].clear()
            rook.has_moved = True
        
        print(f"🏰 {color.title()} castled {side} side!")

    # ============================================================================
    # UPDATED CHECK/CHECKMATE METHODS FOR REAL-TIME DETECTION
    # ============================================================================
    
    def is_in_check(self, color):
        """
        Check if the king of the specified color is in check.
        Now called after every move to provide real-time feedback.
        """
        king_position = self._find_king_position(color)
        if not king_position:
            return False
        
        enemy_color = 'black' if color == 'white' else 'white'
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                square = self.squares[row][col]
                if (not square.is_empty() and square.piece and 
                    square.piece.color == enemy_color):
                    moves, captures = square.piece.get_valid_moves(self, (row, col))
                    if king_position in captures:
                        return True
        return False
    
    def _find_king_position(self, color):
        """Find the position of the king for the specified color."""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                square = self.squares[row][col]
                if (not square.is_empty() and square.piece and
                    square.piece.name == 'king' and 
                    square.piece.color == color):
                    return (row, col)
        return None

    # ============================================================================
    # UPDATED MOVE DISPLAY METHODS WITH CASTLING
    # ============================================================================
    
    def show_valid_moves(self, row, col):
        """
        Calculate and display valid moves for the piece at the given position.
        Now includes castling moves for kings.
        """
        piece = self.squares[row][col].piece
        
        if not piece:
            return
        
        # Clear previous valid moves
        self.valid_moves = []
        
        # Get legal moves (considering check/checkmate)
        moves, capture_moves = self.get_legal_moves(row, col)
        
        # ============================================================================
        # SPECIAL MOVES: CASTLING
        # ============================================================================
        if piece.name == 'king' and not piece.has_moved:
            # Check for castling on both sides
            if self.can_castle(piece.color, 'king'):
                castling_move = (row, 6) if piece.color == 'white' else (row, 6)
                moves.append(castling_move)
                print(f"🏰 Kingside castling available for {piece.color}")
            
            if self.can_castle(piece.color, 'queen'):
                castling_move = (row, 2) if piece.color == 'white' else (row, 2)
                moves.append(castling_move)
                print(f"🏰 Queenside castling available for {piece.color}")
        
        # ============================================================================
        # SPECIAL MOVES: EN PASSANT
        # ============================================================================
        if piece.name == 'pawn':
            en_passant_moves = self._get_available_en_passant_moves(piece, (row, col))
            for en_passant_move in en_passant_moves:
                if self._is_move_legal((row, col), en_passant_move, piece.color):
                    capture_moves.append(en_passant_move)
                    self.enpassant_move.append((row, col))
                    print(f"♟️ En passant available for {piece.color} pawn at ({row},{col}) -> {en_passant_move}")
        
        # Highlight regular moves
        for move_row, move_col in moves:
            target_square = self.squares[move_row][move_col]
            # Check if this is a castling move for special highlighting
            if (piece.name == 'king' and not piece.has_moved and 
                abs(move_col - col) == 2):  # Castling moves are 2 squares
                target_square.set_highlight('castling')
            else:
                target_square.set_highlight('valid_move')
            self.valid_moves.append((move_row, move_col))
        
        # Highlight capture moves (including en passant)
        for move_row, move_col in capture_moves:
            target_square = self.squares[move_row][move_col]
            is_en_passant = self._is_en_passant_position((row, col), (move_row, move_col))
            if is_en_passant:
                target_square.set_highlight('capture')
                direction = 1 if piece.color == 'white' else -1
                square_with_piece = self.squares[target_square.row + direction][move_col]
                square_with_piece.set_highlight('en_passant')
            else:
                target_square.set_highlight('capture')
            self.valid_moves.append((move_row, move_col))
        
        # Highlight king if in check (real-time feedback)
        self._highlight_check()
    
    def _highlight_check(self):
        """Highlight the king if it is in check (called after every move)."""
        # Clear previous check highlights
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.squares[row][col].highlight == 'check':
                    self.squares[row][col].clear_highlight()
        
        # Highlight kings in check
        white_king_pos = self._find_king_position('white')
        black_king_pos = self._find_king_position('black')
        
        if white_king_pos and self.is_in_check('white'):
            row, col = white_king_pos
            self.squares[row][col].set_highlight('check')
            print("👑 White king is in check!")
        
        if black_king_pos and self.is_in_check('black'):
            row, col = black_king_pos
            self.squares[row][col].set_highlight('check')
            print("👑 Black king is in check!")

    # ============================================================================
    # UPDATED MOVE EXECUTION WITH CASTLING
    # ============================================================================
    def _display_check_status(self, player_in_check):
        """
        Display and highlight that a player is in check.
        
        Args:
            player_in_check: 'white' or 'black' - the player who is in check
        """
        king_position = self._find_king_position(player_in_check)
        if king_position:
            row, col = king_position
            self.squares[row][col].set_highlight('check')
            print(f"👑 {player_in_check.title()} king is in check! Choose a move to escape.")
        
        # You can also add sound or visual effects here
        # self._play_check_sound()  # If you implement sound later

    def _display_checkmate(self, player_checkmated):
        """
        Display checkmate status and end the game.
        
        Args:
            player_checkmated: 'white' or 'black' - the player who is checkmated
        """
        winner = 'black' if player_checkmated == 'white' else 'white'
        
        king_position = self._find_king_position(player_checkmated)
        if king_position:
            row, col = king_position
            self.squares[row][col].set_highlight('check')
        
        print(f"🎉 {winner.title()} wins by checkmate!")
        print(f"💀 {player_checkmated.title()} is checkmated!")
        
        # You can add game over screen or reset option here
        # self._show_game_over_screen(winner)  # If you implement UI later

    def handle_click(self, pos):
            """
            Handle mouse click events on the board.
            Check if next player is in check after successful moves.
            """
            # Check if game is over
            game_state = self.get_game_state()
            if game_state['game_over'] in ['white_win', 'black_win']:
                print(f"🏆 Game Over! {game_state['game_over'].replace('_win', '').title()} wins!")
                return None
            
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
                        moving_piece = self.selected_square.piece
                        from_position = (self.selected_square.row, self.selected_square.col)
                        
                        # ============================================================================
                        # CHECK FOR SPECIAL MOVES
                        # ============================================================================
                        
                        # Check for castling
                        is_castling = (moving_piece.name == 'king' and 
                                    not moving_piece.has_moved and 
                                    abs(col - self.selected_square.col) == 2)
                        
                        # Check for en passant
                        is_en_passant = self._is_en_passant_move_pattern(self.selected_square, clicked_square)
                        
                        # Execute the appropriate move
                        if is_castling:
                            side = 'king' if col > self.selected_square.col else 'queen'
                            self.execute_castle(moving_piece.color, side)
                            captured_piece = None
                        else:
                            # Regular move or en passant
                            captured_piece = self.move_piece(self.selected_square, clicked_square, is_en_passant)
                        
                        # Update last move information
                        self._update_last_move(moving_piece, from_position, (row, col), captured_piece)
                        
                        # ============================================================================
                        # CHECK FOR CHECK/CHECKMATE AFTER MOVE (BEFORE SWITCHING PLAYERS)
                        # ============================================================================
                        
                        # Store the next player's color before switching
                        next_player = 'black' if self.current_player == 'white' else 'white'
                        
                        # Check if the move puts the next player in check
                        next_player_in_check = self.is_in_check(next_player)
                        next_player_checkmate = self.is_checkmate(next_player)
                        
                        # Clear selection and highlights
                        self.clear_cache()
                        
                        # Add captured piece to list if any
                        if captured_piece:
                            self.add_captured_piece(captured_piece)
                        
                        # ============================================================================
                        # DISPLAY CHECK STATUS BEFORE SWITCHING TURNS
                        # ============================================================================
                        
                        if next_player_checkmate:
                            print(f"💀 CHECKMATE! {next_player.title()} loses the game!")
                            # Game over - don't switch players
                            self._display_checkmate(next_player)
                        elif next_player_in_check:
                            print(f"⚠️ {next_player.title()} is in check!")
                            # Switch player but highlight they're in check
                            self.switch_player()
                            self._display_check_status(next_player)
                        else:
                            # Normal move - just switch players
                            self.switch_player()
                            print(f"♟️ Move completed. Now it's {self.current_player}'s turn")
                        
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

    def is_checkmate(self, color):
        """
        Check if the specified color is in checkmate.
        
        Checkmate occurs when:
        1. The king is in check
        2. No legal moves exist that would get the king out of check
        
        Args:
            color: 'white' or 'black'
            
        Returns:
            Boolean indicating if it's checkmate
        """
        # Condition 1: Must be in check
        if not self.is_in_check(color):
            return False
        
        # Condition 2: Try all possible moves for all pieces of this color
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                square = self.squares[row][col]
                if (not square.is_empty() and square.piece and
                    square.piece.color == color):
                    
                    # Get all possible moves for this piece
                    moves, captures = square.piece.get_valid_moves(self, (row, col))
                    all_moves = moves + captures
                    
                    # Test each move to see if it gets out of check
                    for move_row, move_col in all_moves:
                        if self._is_move_legal((row, col), (move_row, move_col), color):
                            print(f"♟️ Legal escape move found: {square.piece.name} at ({row},{col}) -> ({move_row},{move_col})")
                            return False  # Found a move that escapes check
        
        print(f"💀 CHECKMATE! {color.title()} loses the game!")
        return True  # No moves escape check
    
    def _is_move_legal(self, from_pos, to_pos, color):
        """
        Check if a move is legal (doesn't put/leave king in check).
        
        Args:
            from_pos: Tuple (row, col) of starting position
            to_pos: Tuple (row, col) of target position
            color: Color of the moving piece
            
        Returns:
            Boolean indicating if move is legal
        """
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Store original state
        moving_piece = self.squares[from_row][from_col].piece
        target_piece = self.squares[to_row][to_col].piece
        
        # Make the move temporarily
        self.squares[to_row][to_col].set_piece(moving_piece)
        self.squares[from_row][from_col].clear()
        
        # Check if king is still in check after move
        still_in_check = self.is_in_check(color)
        
        # Undo the move
        self.squares[from_row][from_col].set_piece(moving_piece)
        self.squares[to_row][to_col].set_piece(target_piece)
        
        return not still_in_check
    
    def get_legal_moves(self, row, col):
        """
        Get only legal moves for a piece (that don't put/leave king in check).
        
        Args:
            row: Row of piece
            col: Column of piece
            
        Returns:
            Tuple of (legal_moves, legal_captures)
        """
        piece = self.squares[row][col].piece
        if not piece:
            return [], []
        
        moves, captures = piece.get_valid_moves(self, (row, col))
        legal_moves = []
        legal_captures = []
        
        # Filter moves that would put/leave king in check
        for move in moves + captures:
            if self._is_move_legal((row, col), move, piece.color):
                if move in moves:
                    legal_moves.append(move)
                else:
                    legal_captures.append(move)
        
        return legal_moves, legal_captures
    
    def get_game_state(self):
        """
        Get the current state of the game.
        
        Returns:
            Dictionary with game state information
        """
        white_check = self.is_in_check('white')
        black_check = self.is_in_check('black')
        white_checkmate = self.is_checkmate('white')
        black_checkmate = self.is_checkmate('black')
        
        state = {
            'current_player': self.current_player,
            'white_in_check': white_check,
            'black_in_check': black_check,
            'white_checkmate': white_checkmate,
            'black_checkmate': black_checkmate,
        }
        
        # Determine overall game state
        if white_checkmate:
            state['game_over'] = 'black_win'
        elif black_checkmate:
            state['game_over'] = 'white_win'
        elif white_check:
            state['game_over'] = 'white_check'
        elif black_check:
            state['game_over'] = 'black_check'
        else:
            state['game_over'] = 'playing'
        
        return state
    
    # ============================================================================
    # UPDATED EXISTING METHODS FOR CHECK/CHECKMATE INTEGRATION
    # ============================================================================ 
    
    def _check_post_move_state(self):
        """Check for check and checkmate after a move is made."""
        game_state = self.get_game_state()
        
        if game_state['white_checkmate']:
            print("💀 CHECKMATE! White loses the game!")
        elif game_state['black_checkmate']:
            print("💀 CHECKMATE! Black loses the game!")
        elif game_state['white_in_check']:
            print("⚠️ White is in check!")
        elif game_state['black_in_check']:
            print("⚠️ Black is in check!")
    
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