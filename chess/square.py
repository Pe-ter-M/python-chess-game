import pygame
from .constant import SQUARE_SIZE, LIGHT_SQUARE, DARK_SQUARE, HIGHLIGHT_COLORS

class Square:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.highlight = None
        self.color = 'light' if (row + col) % 2 == 0 else 'dark'
        self.piece = None
        self.rect = pygame.Rect(
            col * SQUARE_SIZE,
            row * SQUARE_SIZE, 
            SQUARE_SIZE,
            SQUARE_SIZE
        )

    def __repr__(self) -> str:
        return f'Square({self.row}, {self.col}, {self.piece})'
    
    def set_highlight(self, highlight_type):
        """Set highlight type: 'selected', 'valid_move', 'capture', 'check'"""
        self.highlight = highlight_type

    def clear_highlight(self):
        """Remove highlight"""
        self.highlight = None

    def is_empty(self):
        """Check if the specific square is empty"""
        return self.piece is None
    
    def set_piece(self, piece):
        """Set a specific piece on a certain square"""
        self.piece = piece
    
    def clear(self):
        """Remove a piece from the square"""
        self.piece = None
    
    def draw(self, screen):
        # Draw square background
        square_color = LIGHT_SQUARE if self.color == 'light' else DARK_SQUARE
        pygame.draw.rect(screen, square_color, self.rect)
        
        # Draw highlight if exists
        if self.highlight and self.highlight in HIGHLIGHT_COLORS:
            highlight_color = HIGHLIGHT_COLORS[self.highlight]
            
            # Different highlight styles based on type
            if self.highlight == 'selected':
                # Thick border for selected piece
                pygame.draw.rect(screen, highlight_color, self.rect, 4)
            elif self.highlight == 'valid_move':
                # Dot in center for valid moves
                center = self.rect.center
                pygame.draw.circle(screen, highlight_color, center, 8)
            elif self.highlight == 'capture':
                # Circle around piece for capture moves
                pygame.draw.rect(screen, highlight_color, self.rect, 3)
            elif self.highlight == 'check':
                # Red background for king in check
                pygame.draw.rect(screen, highlight_color, self.rect)
                # Redraw piece on top
                if self.piece and self.piece.image:
                    image_rect = self.piece.image.get_rect(center=self.rect.center)
                    screen.blit(self.piece.image, image_rect)
            elif self.highlight == 'en_passant':
                # Four corner dots for en passant
                corners = [
                    (self.rect.left + 8, self.rect.top + 8),      # Top-left
                    (self.rect.right - 8, self.rect.top + 8),     # Top-right
                    (self.rect.left + 8, self.rect.bottom - 8),   # Bottom-left
                    (self.rect.right - 8, self.rect.bottom - 8)   # Bottom-right
                ]
                for corner in corners:
                    pygame.draw.circle(screen, highlight_color, corner, 4)
        
        # Draw piece if exists (unless we're in check highlight)
        if self.piece and self.piece.image and self.highlight != 'check':
            image_rect = self.piece.image.get_rect(center=self.rect.center)
            screen.blit(self.piece.image, image_rect)