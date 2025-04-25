import gradio as gr
from app.controllers.game_controller import GameController

# Global game controller instance; initialize with default board size 8.
controller = GameController(8)
cell_buttons = {}  # Global dictionary for cell button references

# Create global status and game complete components.
status_message = gr.Textbox(label="Status", value="", interactive=False)
game_complete_flag = gr.Checkbox(label="Game Complete", value=False, interactive=False)
timer_display = gr.Textbox(label="Timer", value=controller.get_elapsed_time(), interactive=False)

def get_cell_image(row, col, state):
    """
    Determine which image to display for a given cell.
    Returns:
        str: Path to the image asset.
             - "assets/error.png" if an error is flagged.
             - "assets/queen.png" if a queen is placed.
             - "assets/cross.png" otherwise.
    """
    if state["error_board"][row][col]:
        return "assets/error.png"
    elif state["user_board"][row][col] == 'Q':
        return "assets/queen.png"
    else:
        return "assets/cross.png"

def render_board():
    """
    Create a 2D list of image paths representing the current board state.
    
    Returns:
        tuple: (board_images: list of lists of str, elapsed_time: str)
    """
    state = controller.get_game_state()
    board_images = []
    for r in range(controller.board_size):
        row_images = []
        for c in range(controller.board_size):
            row_images.append(get_cell_image(r, c, state))
        board_images.append(row_images)
    return board_images, state["elapsed_time"]

def cell_click(row, col):
    """
    Callback when a board cell is clicked.
    Assumes the move is to place a queen.
    
    Args:
        row (int): Row index of the clicked cell.
        col (int): Column index of the clicked cell.
    
    Returns:
        tuple: (updated_cell_image: str, updated_timer: str, status_message: str, game_complete_flag: bool)
    """
    valid, msg = controller.update_move(row, col, "queen")
    state = controller.get_game_state()
    cell_image = get_cell_image(row, col, state)
    complete = controller.is_game_complete()
    return cell_image, state["elapsed_time"], msg, complete

def update_full_board():
    """
    Update the entire board grid (used to refresh the timer and board state).
    
    Returns:
        str: Updated timer string.
    """
    board_images, timer_str = render_board()
    # Update each cell button with the new image
    for r in range(controller.board_size):
        for c in range(controller.board_size):
            cell_buttons[(r, c)].update(value=board_images[r][c])
    return timer_str

def reset_game(board_size):
    """
    Reset the game with a new board of the specified size.
    
    Args:
        board_size (int): The new board size.
    
    Returns:
        tuple: (new_board_images: list of lists of str, new_timer: str)
    """
    global controller, cell_buttons
    controller = GameController(int(board_size))
    # Recreate the board grid if board size changes or for a full reset.
    create_board_grid(controller.board_size)
    board_images, timer_str = render_board()
    # Update all cell buttons with new images.
    for r in range(controller.board_size):
        for c in range(controller.board_size):
            cell_buttons[(r, c)].update(value=board_images[r][c])
    return timer_str

def create_board_grid(board_size):
    """
    Create a grid of buttons for the board based on the current board size.
    Each button will display the cell image.
    
    Note: Instead of clearing an existing container, we build the grid from scratch.
    """
    global cell_buttons
    cell_buttons = {}
    # Create a new grid layout inside the placeholder column.
    with board_grid_placeholder:
        # Build the grid rows and cells.
        for r in range(board_size):
            with gr.Row():
                for c in range(board_size):
                    # Create a button for each cell.
                    btn = gr.Button(value="", elem_id=f"cell_{r}_{c}", interactive=True)
                    cell_buttons[(r, c)] = btn
    # After creation, update all buttons with their correct images.
    board_images, _ = render_board()
    for r in range(board_size):
        for c in range(board_size):
            cell_buttons[(r, c)].update(value=board_images[r][c])

# Build the Gradio interface.
with gr.Blocks() as demo:
    gr.Markdown("# Queen Game")
    
    with gr.Row():
        board_size_input = gr.Number(label="Board Size (N x N)", value=8, precision=0)
        reset_button = gr.Button("Reset Game")
    
    timer_display_component = timer_display  # Global timer display
    status_component = status_message         # Global status message
    game_complete_component = game_complete_flag  # Global game complete flag
    
    with gr.Column() as board_grid_placeholder:
        # Create the initial board grid.
        create_board_grid(controller.board_size)
    
    # Set up callbacks for each cell button.
    for r in range(controller.board_size):
        for c in range(controller.board_size):
            # Capture row and col in lambda default arguments.
            cell_buttons[(r, c)].click(
                fn=lambda r=r, c=c: cell_click(r, c),
                outputs=[cell_buttons[(r, c)], timer_display_component, status_component, game_complete_component]
            )
    
    # Callback for the reset button.
    reset_button.click(fn=reset_game, inputs=board_size_input, outputs=timer_display_component)
    
    # Optional: A button to refresh the timer and board state.
    refresh_timer = gr.Button("Refresh Timer")
    refresh_timer.click(fn=update_full_board, outputs=timer_display_component)
    
demo.launch()
