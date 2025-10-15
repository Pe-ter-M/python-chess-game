from .piece import Piece

class Pawn(Piece):
    def __init__(self, color, name='pawn', value=1):
        super().__init__(color, name, value)
        self.has_moved = False
    
    def get_valid_moves(self, board, position):
        row, col = position
        moves = []
        capture_moves = []
        
        direction = -1 if self.color == 'white' else 1
        
        # Single forward move
        new_row = row + direction
        if 0 <= new_row < 8:
            forward_square = board.get_square(new_row, col)
            if forward_square.is_empty():
                moves.append((new_row, col))
                
                # Double forward move
                if not self.has_moved:
                    double_row = row + (2 * direction)
                    if 0 <= double_row < 8:
                        double_square = board.get_square(double_row, col)
                        if double_square.is_empty():
                            moves.append((double_row, col))
        
        # Diagonal captures
        for capture_col in [col - 1, col + 1]:
            if 0 <= capture_col < 8 and 0 <= new_row < 8:
                capture_square = board.get_square(new_row, capture_col)
                if (not capture_square.is_empty() and 
                    capture_square.piece.color != self.color):
                    capture_moves.append((new_row, capture_col))
        
        return moves, capture_moves
    
