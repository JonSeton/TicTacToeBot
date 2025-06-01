from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import sys

class TicTacToeBot:
    def __init__(self):
        try:
            print("Setting up Chrome options...")
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
            chrome_options.add_argument("--disable-software-rasterizer")  # Disable software rasterizer
            chrome_options.add_experimental_option("detach", True)  # Keep browser open
            
            print("Installing ChromeDriver...")
            service = Service()
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.actions = ActionChains(self.driver)
            
            print("ChromeDriver initialized successfully!")
            self.board = [['' for _ in range(3)] for _ in range(3)]
            self.wait = WebDriverWait(self.driver, 10)
            self.is_x_player = True
            self.last_board_state = None
            
        except Exception as e:
            print(f"Error initializing Chrome: {str(e)}")
            print("\nTroubleshooting steps:")
            print("1. Make sure Chrome browser is installed and up to date")
            print("2. Try running the script as administrator")
            print("3. If the error persists, try manually installing ChromeDriver")
            sys.exit(1)
        
    def wait_for_element(self, by, value, timeout=10):
        """Wait for an element to be present and visible."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            print(f"Timeout waiting for element: {value}")
            return None
        
    def start_game(self):
        """Navigate to the Tic-tac-toe game."""
        try:
            print("Navigating to the game...")
            self.driver.get("https://playtictactoe.org/")
            time.sleep(3)  # Wait for initial load
            
            print("Waiting for game board...")
            # First try to find any clickable cell
            cells = self.driver.find_elements(By.CSS_SELECTOR, "td")
            if not cells:
                # Try alternate selector
                cells = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='square']")
            
            if not cells or len(cells) != 9:
                print(f"Found {len(cells) if cells else 0} cells")
                # Try to find the game container
                game_container = self.wait_for_element(By.CSS_SELECTOR, "div[class*='game']")
                if not game_container:
                    raise Exception("Could not find game board")
                cells = game_container.find_elements(By.CSS_SELECTOR, "td") or game_container.find_elements(By.CSS_SELECTOR, "div[class*='square']")
            
            print(f"Found {len(cells)} cells")
            
            if len(cells) == 9:
                print("Making first move in the center...")
                # Try to click the center cell
                center_cell = cells[4]
                try:
                    # Try regular click
                    center_cell.click()
                except:
                    try:
                        # Try JavaScript click
                        self.driver.execute_script("arguments[0].click();", center_cell)
                    except:
                        # Try moving to element and clicking
                        self.actions.move_to_element(center_cell).click().perform()
                
                time.sleep(1)  # Wait for move to register
                print("First move made!")
                
                # Get initial board state
                self.last_board_state = self.get_board_state()
                if not self.last_board_state:
                    raise Exception("Could not get initial board state")
                print("Initial board state captured")
            else:
                print(f"Error: Expected 9 cells, found {len(cells) if cells else 0}")
                raise Exception("Invalid board size")
            
        except Exception as e:
            print(f"Error starting game: {str(e)}")
            return False
        return True
        
    def get_board_state(self):
        """Get the current state of the board."""
        try:
            # Wait for cells to be present
            self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "td, div[class*='square']")))
            
            # Try different selectors to find cells
            cells = self.driver.find_elements(By.CSS_SELECTOR, "td")
            if not cells:
                cells = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='square']")
            
            if len(cells) != 9:
                print(f"Warning: Found {len(cells)} cells instead of 9")
                return None
            
            new_board = [['' for _ in range(3)] for _ in range(3)]
            for row in range(3):
                for col in range(3):
                    cell_index = row * 3 + col
                    cell = cells[cell_index]
                    
                    # Find the inner div that contains the X or O marker
                    try:
                        inner_div = cell.find_element(By.CSS_SELECTOR, "div")
                        marker_class = inner_div.get_attribute("class").strip().lower()
                    except:
                        marker_class = ""
                    
                    # Debug print for cell state
                    print(f"Cell ({row},{col}) - Marker class: {marker_class}")
                    
                    # Check the inner div's class for x or o
                    if marker_class == "x":
                        new_board[row][col] = 'X'
                    elif marker_class == "o":
                        new_board[row][col] = 'O'
                    else:
                        new_board[row][col] = ''
            
            # Update the internal board state
            self.board = [row[:] for row in new_board]
            
            # Debug print
            print("\nCurrent board state:")
            for row in self.board:
                print(row)
            
            return new_board
            
        except WebDriverException as e:
            print(f"Browser error while getting board state: {str(e)}")
            return None
        except Exception as e:
            print(f"Error getting board state: {str(e)}")
            return None
        
    def board_has_changed(self, new_state):
        """Check if the board state has changed."""
        if not self.last_board_state or not new_state:
            return False
            
        has_changed = False
        num_changes = 0
        for i in range(3):
            for j in range(3):
                if new_state[i][j] != self.last_board_state[i][j]:
                    print(f"Change detected at position ({i}, {j}): {self.last_board_state[i][j]} -> {new_state[i][j]}")
                    has_changed = True
                    num_changes += 1
        
        # If more than one change, something went wrong with detection
        if num_changes > 1:
            print("Warning: Multiple changes detected, may be detection error")
            return False
            
        return has_changed
        
    def make_move(self, row, col):
        """Make a move at the specified position."""
        try:
            print(f"Attempting move at ({row}, {col})")
            
            # Wait for cells to be present and interactable
            self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "td, div[class*='square']")))
            
            # Try different selectors to find cells
            cells = self.driver.find_elements(By.CSS_SELECTOR, "td")
            if not cells:
                cells = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='square']")
            
            if len(cells) != 9:
                print(f"Error: Found {len(cells)} cells instead of 9")
                return False
            
            cell_index = row * 3 + col
            cell = cells[cell_index]
            
            # Check if cell is empty by looking at its inner div
            try:
                inner_div = cell.find_element(By.CSS_SELECTOR, "div")
                marker_class = inner_div.get_attribute("class").strip().lower()
            except:
                marker_class = ""
            
            print(f"Cell state before click - Marker class: {marker_class}")
            
            if marker_class == "":
                # Try multiple click methods with retry
                for attempt in range(3):
                    try:
                        # Scroll cell into view
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", cell)
                        time.sleep(0.5)
                        
                        # Method 1: Click the cell itself
                        cell.click()
                        print("Click attempt 1 (Regular) succeeded")
                        break
                    except:
                        try:
                            # Method 2: Click the inner div
                            inner_div = cell.find_element(By.CSS_SELECTOR, "div")
                            inner_div.click()
                            print("Click attempt 2 (Inner div) succeeded")
                            break
                        except:
                            try:
                                # Method 3: JavaScript click
                                self.driver.execute_script("arguments[0].click();", cell)
                                print("Click attempt 3 (JavaScript) succeeded")
                                break
                            except:
                                if attempt == 2:  # Last attempt failed
                                    raise Exception("All click methods failed")
                                print(f"Click attempt {attempt + 1} failed, retrying...")
                                time.sleep(1)  # Wait longer before next attempt
                
                # Wait for move to register
                time.sleep(1)
                
                # Verify the move was made
                try:
                    inner_div = cell.find_element(By.CSS_SELECTOR, "div")
                    new_marker_class = inner_div.get_attribute("class").strip().lower()
                except:
                    new_marker_class = ""
                
                print(f"Cell state after click - Marker class: {new_marker_class}")
                
                expected_marker = 'x' if self.is_x_player else 'o'
                if new_marker_class == expected_marker:
                    print(f"Move verified at ({row}, {col})")
                    return True
                else:
                    print(f"Move not verified at ({row}, {col})")
                    return False
            else:
                print(f"Cell ({row}, {col}) is already occupied")
                return False
            
        except WebDriverException as e:
            print(f"Browser error while making move: {str(e)}")
            return False
        except Exception as e:
            print(f"Error making move: {str(e)}")
            return False
    
    def calculate_best_move(self):
        """Calculate the best move using minimax algorithm."""
        print("Calculating best move...")
        best_score = float('-inf')
        best_move = None
        
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == '':
                    self.board[i][j] = 'X'
                    score = self.minimax(self.board, 0, False)
                    self.board[i][j] = ''
                    if score > best_score:
                        best_score = score
                        best_move = (i, j)
        
        if best_move:
            print(f"Best move calculated: {best_move}")
        else:
            print("No valid moves found")
        return best_move
    
    def minimax(self, board, depth, is_maximizing):
        """Minimax algorithm for calculating the best move."""
        result = self.check_winner()
        if result is not None:
            return {'O': -1, 'X': 1, 'tie': 0}[result]
            
        if is_maximizing:
            best_score = float('-inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == '':
                        board[i][j] = 'X'
                        score = self.minimax(board, depth + 1, False)
                        board[i][j] = ''
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == '':
                        board[i][j] = 'O'
                        score = self.minimax(board, depth + 1, True)
                        board[i][j] = ''
                        best_score = min(score, best_score)
            return best_score
    
    def check_winner(self):
        """Check if there's a winner or tie."""
        # Get current board state
        board = self.board
        
        # Check rows
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != '':
                print(f"Win detected in row {i}")
                return board[i][0]
        
        # Check columns
        for i in range(3):
            if board[0][i] == board[1][i] == board[2][i] != '':
                print(f"Win detected in column {i}")
                return board[0][i]
        
        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] != '':
            print("Win detected in main diagonal")
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != '':
            print("Win detected in other diagonal")
            return board[0][2]
        
        # Check for tie (board full)
        if all(board[i][j] != '' for i in range(3) for j in range(3)):
            print("Game is a tie")
            return 'tie'
        
        return None
    
    def count_pieces(self, board):
        """Count X and O pieces on the board."""
        x_count = sum(1 for row in board for cell in row if cell == 'X')
        o_count = sum(1 for row in board for cell in row if cell == 'O')
        return x_count, o_count

    def is_our_turn(self, new_state):
        """Determine if it's our turn to move."""
        x_count, o_count = self.count_pieces(new_state)
        print(f"Current piece count - X: {x_count}, O: {o_count}")
        
        if self.is_x_player:
            # We are X
            if x_count < o_count:
                # We've fallen behind, definitely our turn
                print("We (X) have fallen behind in moves, catching up...")
                return True
            # Normal case: our turn if X count equals O count
            return x_count == o_count
        else:
            # We are O
            if o_count < x_count - 1:
                # We've fallen behind, definitely our turn
                print("We (O) have fallen behind in moves, catching up...")
                return True
            # Normal case: our turn if X count is one more than O count
            return x_count == o_count + 1

    def is_game_over(self):
        """Check if the game is over by looking for win conditions or a full board."""
        try:
            # First check for a winner
            winner = self.check_winner()
            if winner is not None:
                print(f"Game over - Winner: {winner}")
                return True
            
            # Check for game-over message or winning line
            game_over_elements = self.driver.find_elements(By.CSS_SELECTOR, ".game-over, [class*='game-over'], [class*='win']")
            if game_over_elements:
                print("Game over detected via UI elements")
                return True
            
            # Check if board is full
            cells = self.driver.find_elements(By.CSS_SELECTOR, "td") or self.driver.find_elements(By.CSS_SELECTOR, "div[class*='square']")
            if not cells:
                return False
            
            # Count filled cells
            filled_count = 0
            for cell in cells:
                try:
                    inner_div = cell.find_element(By.CSS_SELECTOR, "div")
                    marker_class = inner_div.get_attribute("class").strip().lower()
                    if marker_class in ['x', 'o']:
                        filled_count += 1
                except:
                    continue
            
            if filled_count == 9:
                print("Game over - Board is full")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error checking game over: {str(e)}")
            return False

    def start_new_game(self):
        """Start a new game by first clearing the board and then making the first move if we're X."""
        try:
            print("\nStarting new game...")
            time.sleep(1)  # Wait for any animations
            
            # First check if a new game has already started
            current_state = self.get_board_state()
            if current_state:
                x_count, o_count = self.count_pieces(current_state)
                if x_count == 0 and o_count == 1:
                    # Opponent has started a new game as O
                    print("Opponent has already started a new game as O")
                    self.is_x_player = True
                    self.last_board_state = current_state
                    return True
                elif x_count == 1 and o_count == 0:
                    # Opponent has started a new game as X
                    print("Opponent has already started a new game as X")
                    self.is_x_player = False
                    self.last_board_state = current_state
                    return True
            
            # If no game in progress, try to restart
            max_restart_attempts = 3
            for attempt in range(max_restart_attempts):
                try:
                    restart_button = self.wait_for_element(By.CSS_SELECTOR, "div.restart, div[class*='restart']")
                    if restart_button and restart_button.is_displayed():
                        print("Found restart button, clicking it...")
                        try:
                            # Try JavaScript click first as it's most reliable
                            self.driver.execute_script("arguments[0].click();", restart_button)
                        except:
                            try:
                                # Try regular click
                                restart_button.click()
                            except:
                                # Try with action chains
                                self.actions.move_to_element(restart_button).click().perform()
                        time.sleep(1)  # Wait for board to clear
                        break
                except Exception as e:
                    print(f"Restart attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_restart_attempts - 1:
                        time.sleep(1)  # Wait before next attempt
                    else:
                        print("Could not click restart button after multiple attempts")
            
            # Verify the board is clear
            time.sleep(0.5)
            cells = self.driver.find_elements(By.CSS_SELECTOR, "td") or self.driver.find_elements(By.CSS_SELECTOR, "div[class*='square']")
            if len(cells) != 9:
                print("Error: Could not find game board after clearing")
                return False
            
            # Get current board state again
            new_state = self.get_board_state()
            if not new_state:
                return False
                
            # Count pieces to determine if we're X or O and if game has started
            x_count, o_count = self.count_pieces(new_state)
            
            if x_count == 0 and o_count == 0:
                # No moves yet, we're X
                print("We are X, making first move...")
                self.is_x_player = True
                center_cell = cells[4]  # Center square is index 4
                
                # Try multiple click methods for the first move
                for attempt in range(3):
                    try:
                        # Scroll into view
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", center_cell)
                        time.sleep(0.5)
                        
                        # Try clicking the cell
                        center_cell.click()
                        time.sleep(0.5)  # Wait for move to register
                        
                        # Verify the move was made
                        inner_div = center_cell.find_element(By.CSS_SELECTOR, "div")
                        marker_class = inner_div.get_attribute("class").strip().lower()
                        if marker_class == 'x':
                            print("First move made in new game!")
                            time.sleep(0.5)  # Wait for any animations
                            self.last_board_state = self.get_board_state()
                            return True
                    except:
                        try:
                            # Try JavaScript click
                            self.driver.execute_script("arguments[0].click();", center_cell)
                            time.sleep(0.5)
                            
                            # Verify the move was made
                            inner_div = center_cell.find_element(By.CSS_SELECTOR, "div")
                            marker_class = inner_div.get_attribute("class").strip().lower()
                            if marker_class == 'x':
                                print("First move made in new game!")
                                time.sleep(0.5)
                                self.last_board_state = self.get_board_state()
                                return True
                        except:
                            if attempt == 2:
                                print("Failed to make first move in new game")
                                return False
                            time.sleep(1)
                return False
            elif x_count == 1 and o_count == 0:
                # X has moved, we're O
                print("Opponent moved first as X, we are O")
                self.is_x_player = False
                self.last_board_state = new_state
                return True
            elif x_count == 0 and o_count == 1:
                # O has moved, we're X
                print("Opponent moved first as O, we are X")
                self.is_x_player = True
                self.last_board_state = new_state
                return True
            else:
                print(f"Unexpected board state - X: {x_count}, O: {o_count}")
                return False
            
        except Exception as e:
            print(f"Error starting new game: {str(e)}")
            return False

    def play_multiple_games(self, num_games=5):
        """Play multiple games in succession."""
        games_played = 0
        max_games = num_games
        consecutive_failures = 0
        max_failures = 3
        
        print(f"\nStarting session of {max_games} games...")
        
        while games_played < max_games and consecutive_failures < max_failures:
            print(f"\nGame {games_played + 1} of {max_games}")
            
            if games_played == 0:
                # First game starts automatically
                if not self.start_game():
                    print("Failed to start first game")
                    consecutive_failures += 1
                    continue
            else:
                # Subsequent games need to be started manually
                if not self.start_new_game():
                    print("Failed to start new game")
                    consecutive_failures += 1
                    continue
            
            # Reset failure counter on successful game start
            consecutive_failures = 0
            
            # Play the game
            self.play_single_game()
            games_played += 1
            
            print(f"Game {games_played} completed")
            time.sleep(1)  # Short break between games
        
        if consecutive_failures >= max_failures:
            print("\nToo many consecutive failures to start new games. Ending session.")
        
        print(f"\nSession finished. Played {games_played} games.")

    def play_single_game(self):
        """Play a single game."""
        game_active = True
        retry_count = 0
        max_retries = 3
        moves_made = 0
        last_move_time = time.time()
        no_change_count = 0
        max_no_change = 10  # Maximum number of checks without board changes
        last_piece_counts = None
        
        while game_active and retry_count < max_retries and moves_made < 9:
            try:
                current_time = time.time()
                
                # Get new board state
                new_state = self.get_board_state()
                if not new_state:
                    print("Error getting board state")
                    retry_count += 1
                    time.sleep(1)
                    continue
                
                # Check if game is over
                if self.is_game_over():
                    print("Game is over!")
                    break
                
                # Get current piece counts
                x_count, o_count = self.count_pieces(new_state)
                current_counts = (x_count, o_count)
                
                # Check if the board has changed
                board_changed = self.board_has_changed(new_state)
                time_since_last_move = current_time - last_move_time
                
                if board_changed:
                    print(f"Board changed after {time_since_last_move:.1f} seconds")
                    self.last_board_state = new_state
                    last_piece_counts = current_counts
                    no_change_count = 0
                else:
                    # If no change but we've fallen behind in moves, try to catch up
                    if last_piece_counts != current_counts:
                        print("Piece counts changed without board state change detected")
                        self.last_board_state = new_state
                        last_piece_counts = current_counts
                        no_change_count = 0
                    else:
                        no_change_count += 1
                        if no_change_count >= max_no_change:
                            print("No board changes detected for too long, assuming game is over")
                            break
                
                # Check if it's our turn
                if self.is_our_turn(new_state):
                    print("It's our turn!")
                    
                    # Make our move
                    print("\nCalculating next move...")
                    best_move = self.calculate_best_move()
                    if best_move:
                        print(f"Making move at position {best_move}")
                        if self.make_move(*best_move):
                            moves_made += 1
                            last_move_time = time.time()
                            time.sleep(0.5)
                            self.last_board_state = self.get_board_state()
                            print(f"Move {moves_made} completed")
                            retry_count = 0
                            no_change_count = 0
                        else:
                            print("Failed to make move")
                            retry_count += 1
                    else:
                        print("No valid moves available")
                        break
                else:
                    print("Waiting for opponent's move...")
                
                # Adaptive polling interval
                if time_since_last_move < 2:
                    time.sleep(0.2)
                else:
                    time.sleep(0.5)
                
            except WebDriverException as e:
                print(f"Browser error in game loop: {str(e)}")
                retry_count += 1
            except Exception as e:
                print(f"Error in game loop: {str(e)}")
                game_active = False
        
        # Final game over check
        if self.is_game_over():
            print("Game completed normally")
        elif moves_made >= 9:
            print("Game ended - maximum moves reached")
        elif retry_count >= max_retries:
            print("Game ended - maximum retries reached")
        elif no_change_count >= max_no_change:
            print("Game ended - no changes detected")
        
        # Wait for any end-game animations
        time.sleep(2)

    def close(self):
        """Clean up resources."""
        try:
            input("Press Enter to close the browser...")
            self.driver.quit()
            print("\nClosed browser successfully")
        except:
            pass

if __name__ == "__main__":
    print("Starting Tic-tac-toe Bot (X player)...")
    bot = None
    try:
        bot = TicTacToeBot()
        bot.play_multiple_games(5)  # Play 5 games by default
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        if bot:
            bot.close() 
