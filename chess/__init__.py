import pygame
from chess.board import Board
from chess.constant import WINDOW_WIDTH, WINDOW_HEIGHT
from chess.ai.minmax.MinimaxNode import MinimaxNode
class ChessGameManager:
    """
    Manages different game modes and AI integration
    Compatible with existing Board class and Node system
    """
    
    def __init__(self, game_mode='human_vs_human', ai_color='black', ai_depth=3):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(f"Chess - {game_mode.replace('_', ' ').title()}")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.board = Board()
        self.game_mode = game_mode
        self.ai_color = ai_color
        self.ai_depth = ai_depth
        self.running = True
        self.game_over = False
        
        # Node system (your existing functionality)
        self.current_node = None
        self.move_history = []
        
        # AI system (extensible for multiple AIs)
        self.ai_players = {}
        self._initialize_ai_system()
        
        # Initialize nodes
        self._initialize_root_node()
        
        # Game mode specific
        self._setup_game_mode()
    
    def _initialize_ai_system(self):
        """Initialize AI players - extensible for multiple AI types"""
        # Placeholder for future AI implementations
        self.ai_players = {
            'minimax': None,  # Will be initialized when needed
            'neural_net': None,
            'random': None
        }
        print(f"🤖 AI System Ready - Modes: {list(self.ai_players.keys())}")
    
    def _initialize_root_node(self):
        """Your existing node initialization"""
        print("🎯 INITIALIZING ROOT NODE...")
        self.current_node = MinimaxNode(
            board=self.board,
            move=None,
            depth=0,
            is_maximizing=True
        )
        self.current_node.evaluate_position()
        self.move_history.append(self.current_node)
        print(f"✅ Root node created: {self.current_node}")
    
    def _setup_game_mode(self):
        """Configure the selected game mode"""
        mode_descriptions = {
            'human_vs_human': "Human vs Human",
            'human_vs_ai': f"Human vs AI ({self.ai_color})", 
            'ai_vs_ai': "AI vs AI",
            'analysis': "Position Analysis Mode"
        }
        
        print(f"🎮 Game Mode: {mode_descriptions.get(self.game_mode, self.game_mode)}")
        
        if self.game_mode == 'human_vs_ai':
            print(f"🤖 AI playing as: {self.ai_color}")
        elif self.game_mode == 'ai_vs_ai':
            print("🤖 AI vs AI match started!")
    
    # ============================================================================
    # GAME MODE MANAGEMENT
    # ============================================================================
    
    def set_game_mode(self, new_mode, ai_color=None):
        """Change game mode dynamically"""
        self.game_mode = new_mode
        if ai_color:
            self.ai_color = ai_color
        self._setup_game_mode()
        print(f"🔄 Game mode changed to: {new_mode}")
    
    def is_ai_turn(self):
        """Check if it's currently AI's turn to move"""
        if self.game_mode == 'human_vs_human':
            return False
        elif self.game_mode == 'human_vs_ai':
            return self.board.current_player == self.ai_color
        elif self.game_mode == 'ai_vs_ai':
            return True  # Always AI's turn in AI vs AI
        return False
    
    def get_current_player_type(self):
        """Get type of current player (human/ai)"""
        if self.game_mode == 'human_vs_human':
            return 'human'
        elif self.game_mode == 'human_vs_ai':
            return 'ai' if self.board.current_player == self.ai_color else 'human'
        elif self.game_mode == 'ai_vs_ai':
            return 'ai'
        return 'human'
    
    # ============================================================================
    # MOVE HANDLING (Compatible with your existing system)
    # ============================================================================
    
    def handle_human_move(self, pos):
        """Handle human move - compatible with your existing Board.handle_click"""
        result = self.board.handle_click(pos)
        if result:
            action, piece = result
            print(f"\n🖱️ {action}: {piece.color} {piece.name}")
            
            if action == 'move_executed':
                self._create_move_node()
                return True
        return False
    
    def handle_ai_move(self):
        """Handle AI move - placeholder for AI implementation"""
        if not self.is_ai_turn() or self.game_over:
            return False
        
        print(f"🤖 AI ({self.board.current_player}) thinking...")
        
        # Placeholder - replace with actual AI logic
        # For now, just make a random legal move
        # legal_moves = self._get_all_legal_moves(self.board.current_player)
        
        legal_square_moves = self._get_square_ai_piece_with_move(self.board.current_player)
        for move in legal_square_moves:
            print(move)
        # if legal_moves:
        #     from_square, to_square = legal_moves[0]  # First legal move
        #     captured_piece = self.board.move_piece(from_square, to_square)
        #     self._create_move_node((from_square, to_square), captured_piece)
        #     print(f"🤖 AI moved: {self.current_node.move_notation}")
        #     return True
        
        # return False
    
    def _create_move_node(self, move=None, captured_piece=None):
        """Create node for the current position - your existing functionality"""
        new_node = MinimaxNode(
            board=self.board,
            move=move,
            parent=self.current_node,
            depth=len(self.move_history),
            is_maximizing=(self.board.current_player == 'white')
        )
        new_node.evaluate_position()
        
        self.current_node = new_node
        self.move_history.append(new_node)
        
        self._print_move_analysis(new_node, captured_piece)
        
        # Check game end
        self._check_game_end()
    
    def _get_all_legal_moves(self, color):
        """Get all legal moves for a color - compatible with your Board"""
        legal_moves = []
        for row in range(8):
            for col in range(8):
                square = self.board.squares[row][col]
                if not square.is_empty() and (square.piece and square.piece.color == color):
                    moves, captures = self.board.get_legal_moves(row, col)
                    for move_row, move_col in moves + captures:
                        from_square = self.board.squares[row][col]
                        to_square = self.board.squares[move_row][move_col]
                        legal_moves.append((from_square, to_square))
        return legal_moves
    
    def _get_square_ai_piece_with_move(self,color):
        square_pos = []
        for row in range(8):
            for col in range(8):
                square = self.board.squares[row][col]
                if not square.is_empty() and (square.piece and square.piece.color == color):
                    moves, captures = self.board.get_legal_moves(row, col)
                    if moves :
                        square_pos.append(moves)
                    elif captures:
                        square_pos.append(captures)
        return square_pos


    # ============================================================================
    # YOUR EXISTING NODE DEBUGGING FUNCTIONALITY
    # ============================================================================
    
    def _print_move_analysis(self, node, captured_piece):
        """Your existing move analysis"""
        print("\n" + "="*60)
        print(f"🎯 MOVE {len(self.move_history)}: {node.move_notation}")
        print("="*60)
        print(f"Move: {node.move_notation}")
        print(f"Player: {node.player}")
        print(f"Depth: {node.depth}")
        
        if captured_piece:
            print(f"Capture: {captured_piece.color} {captured_piece.name}")
        
        print("\n📊 POSITION EVALUATION:")
        print(f"Total Value: {node.value}")
        print(f"Material: {node.raw_material}")
        print(f"Positional: {node.positional_score}")
        
        print("\n🔍 EVALUATION BREAKDOWN:")
        for category, score in node.evaluation_breakdown.items():
            if score != 0:
                print(f"  {category:15}: {score:>6}")
        
        print(f"\n⚡ GAME STATE:")
        print(f"Check: {node.is_check}")
        print(f"Current player: {self.board.current_player}")
        print(f"Player type: {self.get_current_player_type()}")
        print("="*60)
    
    def print_current_game_state(self):
        """Your existing game state printing"""
        print("\n" + "="*50)
        print("📈 CURRENT GAME STATE SUMMARY")
        print("="*50)
        print(f"Total moves: {len(self.move_history)}")
        print(f"Current player: {self.board.current_player} ({self.get_current_player_type()})")
        print(f"Game mode: {self.game_mode}")
        print(f"Current node: {self.current_node}")
        
        print("\n📜 LAST 3 MOVES:")
        for i, node in enumerate(self.move_history[-3:]):
            player_type = 'AI' if (i % 2 == 0 and self.ai_color == 'white') or (i % 2 == 1 and self.ai_color == 'black') else 'Human'
            print(f"  Move {node.depth}: {node.move_notation} (Value: {node.value}) - {player_type}")
        
        print("="*50)
    
    def _print_move_history(self):
        """Your existing move history"""
        print("\n" + "="*60)
        print("📜 COMPLETE MOVE HISTORY")
        print("="*60)
        for i, node in enumerate(self.move_history):
            marker = " →" if node == self.current_node else "  "
            player_type = 'AI' if (i % 2 == 0 and self.ai_color == 'white') or (i % 2 == 1 and self.ai_color == 'black') else 'Human'
            print(f"{marker} Move {i}: {node.move_notation:8} | Value: {node.value:6} | Player: {node.player} | Type: {player_type}")
        print("="*60)
    
    # ============================================================================
    # GAME FLOW MANAGEMENT
    # ============================================================================
    
    def _check_game_end(self):
        """Check if game has ended"""
        game_state = self.board.get_game_state()
        if game_state['game_over'] != 'playing':
            self.game_over = True
            winner = "White" if game_state['game_over'] == 'white_win' else "Black" if game_state['game_over'] == 'black_win' else "Draw"
            print(f"\n🏆 GAME OVER! Winner: {winner}")
            return True
        return False
    
    def reset_game(self, new_mode=None, new_ai_color=None):
        """Reset game with optional new settings"""
        print("\n🔄 RESETTING GAME...")
        self.board = Board()
        self.move_history = []
        self.game_over = False
        
        if new_mode:
            self.game_mode = new_mode
        if new_ai_color:
            self.ai_color = new_ai_color
        
        self._initialize_root_node()
        self._setup_game_mode()
        print("✅ Game reset complete!")
    
    # ============================================================================
    # MAIN GAME LOOP
    # ============================================================================
    
    def run(self):
        """Main game loop with AI integration"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and not self.game_over:
                        if self.get_current_player_type() == 'human':
                            self.handle_human_move(event.pos)
                
                # Your existing debug controls
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_d:  # Debug info
                        self.print_current_game_state()
                    elif event.key == pygame.K_n:  # Node details
                        print("\n" + "="*60)
                        print("🔍 CURRENT NODE DETAILS:")
                        print("="*60)
                        # print(self.current_node.detailed_repr())
                    elif event.key == pygame.K_h:  # Move history
                        self._print_move_history()
                    elif event.key == pygame.K_r:  # Reset
                        self.reset_game()
                    elif event.key == pygame.K_1:  # Switch to Human vs Human
                        self.reset_game('human_vs_human')
                    elif event.key == pygame.K_2:  # Switch to Human vs AI (White)
                        self.reset_game('human_vs_ai', 'black')
                    elif event.key == pygame.K_3:  # Switch to Human vs AI (Black)  
                        self.reset_game('human_vs_ai', 'white')
                    elif event.key == pygame.K_4:  # Switch to AI vs AI
                        self.reset_game('ai_vs_ai')
            
            # AI move handling
            if not self.game_over and self.is_ai_turn():
                self.handle_ai_move()
            
            # Drawing
            self._draw_game()
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
    
    def _draw_game(self):
        """Draw game with enhanced UI"""
        self.board.draw(self.screen)
        self._draw_ui_overlay()
    
    def _draw_ui_overlay(self):
        """Draw game information overlay"""
        font = pygame.font.Font(None, 24)
        
        # Game info
        game_info = [
            f"Mode: {self.game_mode}",
            f"Move: {len(self.move_history)}",
            f"Player: {self.board.current_player} ({self.get_current_player_type()})",
            f"Eval: {self.current_node.value if self.current_node else 'N/A'}"
        ]
        
        for i, info in enumerate(game_info):
            text_surface = font.render(info, True, (255, 255, 255))
            self.screen.blit(text_surface, (10, 10 + i * 25))
        
        # Controls
        controls = [
            "D: Debug | N: Node | H: History | R: Reset",
            "1: HvH | 2: HvAI(Black) | 3: HvAI(White) | 4: AIvAI"
        ]
        
        for i, control in enumerate(controls):
            text_surface = font.render(control, True, (200, 200, 200))
            self.screen.blit(text_surface, (10, WINDOW_HEIGHT - 60 + i * 25))
        
        # Game over message
        if self.game_over:
            game_state = self.board.get_game_state()
            if game_state['game_over'] != 'playing':
                winner = game_state['game_over'].replace('_win', '').title()
                overlay = pygame.Surface((WINDOW_WIDTH, 60), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0, WINDOW_HEIGHT // 2 - 30))
                
                font_large = pygame.font.Font(None, 48)
                text = font_large.render(f"GAME OVER - {winner} WINS!", True, (255, 255, 0))
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                self.screen.blit(text, text_rect)