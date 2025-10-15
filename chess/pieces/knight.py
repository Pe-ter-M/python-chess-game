from .piece import Piece

class Knight(Piece):
    def __init__(self, color, name='knight', value=3):
        super().__init__(color, name, value)
    
    def get_valid_moves(self, board, position):
        """
        Calculate all valid knight moves from current position
        Returns: (moves, capture_moves) where:
        - moves: squares that are empty and can be moved to
        - capture_moves: squares with opponent pieces that can be captured
        """
        row, col = position
        moves = []
        capture_moves = []
        
        # All possible knight moves (8 possible L-shapes)
        knight_moves = [
            (-2, -1), (-2, 1),  # Up 2, left/right 1
            (-1, -2), (-1, 2),  # Up 1, left/right 2
            (1, -2), (1, 2),    # Down 1, left/right 2
            (2, -1), (2, 1)     # Down 2, left/right 1
        ]
        
        for move in knight_moves:
            new_row = row + move[0]
            new_col = col + move[1]
            
            # Check if move is within board bounds
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target_square = board.get_square(new_row, new_col)
                
                if target_square.is_empty():
                    # Empty square - regular move
                    moves.append((new_row, new_col))
                elif target_square.piece.color != self.color:
                    # Opponent piece - capture move
                    capture_moves.append((new_row, new_col))
    
        return moves, capture_moves
    
    def __str__(self):
        return f"{self.color[0].upper()}N"  # WN or BN
    
    def __repr__(self):
        return f"Knight({self.color})"