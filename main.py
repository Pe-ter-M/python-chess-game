import pygame
from chess.board import Board
from chess.constant import WINDOW_WIDTH, WINDOW_HEIGHT

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Chess Game")
    clock = pygame.time.Clock()
    
    board = Board()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        result = board.handle_click(event.pos)
                        if result:
                            action, piece = result
                            print(f"{action}: {piece.color} {piece.name}")
        
        # Draw everything
        board.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()