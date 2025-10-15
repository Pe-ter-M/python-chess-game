from .piece import Piece

class Bishop(Piece):
    def __init__(self, color, name='bishop', value=3):
        super().__init__(color, name, value)
    
    def get_valid_moves(self, board, position):
        row, col = position
        moves = []
        capture_moves = []
        
        # Four diagonal directions
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
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
                    break  # Stop in this direction after hitting any piece
        
        return moves, capture_moves