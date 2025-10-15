from .piece import Piece

class King(Piece):
    def __init__(self, color, name='king', value=100):
        super().__init__(color, name, value)
        self.has_moved = False
    
    def get_valid_moves(self, board, position):
        row, col = position
        moves = []
        capture_moves = []
        
        # All 8 surrounding squares
        king_moves = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for move in king_moves:
            new_row = row + move[0]
            new_col = col + move[1]
            
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target_square = board.get_square(new_row, new_col)
                
                if target_square.is_empty():
                    moves.append((new_row, new_col))
                elif target_square.piece.color != self.color:
                    capture_moves.append((new_row, new_col))
        
        # TODO: Add castling logic later
        return moves, capture_moves
    