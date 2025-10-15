from .piece import Piece

class Queen(Piece):
    def __init__(self, color, name='queen', value=9):
        super().__init__(color, name, value)
    
    def get_valid_moves(self, board, position):
        row, col = position
        moves = []
        capture_moves = []
        
        # All 8 directions (rook + bishop moves)
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # Rook directions
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Bishop directions
        ]
        
        for direction in directions:
            for distance in range(1, 8):
                new_row = row + direction[0] * distance
                new_col = col + direction[1] * distance
                
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                
                target_square = board.get_square(new_row, new_col)
                
                if target_square.is_empty():
                    moves.append((new_row, new_col))
                else:
                    if target_square.piece.color != self.color:
                        capture_moves.append((new_row, new_col))
                    break
        
        return moves, capture_moves