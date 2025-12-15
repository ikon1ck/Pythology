from pyscript import window, document
from pyodide.ffi import create_proxy

last_active_div = None

def set_window_active(move_div, z_index=1):
    """Centralized function to set a window as active"""
    global last_active_div
    
    # Get all movable divs (including dialogs)
    all_windows = document.querySelectorAll('.movable-div')
    
    # Reset all windows to inactive state
    for win in all_windows:
        win.style.zIndex = str(z_index - 1)
        win.style.backgroundColor = "#000000"
        top_bar = win.querySelector(".top-bar")
        if top_bar:
            top_bar.style.backgroundColor = "#1e1e1e"
    
    # Set the clicked window as active
    move_div.style.zIndex = str(z_index + 1)
    move_div.style.backgroundColor = "#1a1a1a"
    top_bar = move_div.querySelector(".top-bar")
    if top_bar:
        top_bar.style.backgroundColor = "#007acc"
    
    last_active_div = move_div

def make_draggable(move_div):
    top_bar = move_div.querySelector(".top-bar")

    offset_x = 0
    offset_y = 0
    
    def draggableMove(event):
        nonlocal offset_x, offset_y
        
        position_x = event.clientX - offset_x
        position_y = event.clientY - offset_y
        
        move_div.style.left = f"{position_x}px"
        move_div.style.top = f"{position_y}px"
    
    def holdingMouse(event):
        # Make active when starting to drag
        set_window_active(move_div, 100)
        
        nonlocal offset_x, offset_y
        
        rect = move_div.getBoundingClientRect()
        offset_x = event.clientX - rect.left
        offset_y = event.clientY - rect.top
        
        document.addEventListener("mousemove", draggable_move_proxy)
    
    def releaseMouse(event):
        document.removeEventListener("mousemove", draggable_move_proxy)
    
    def handleClick(event):
        """Handle click anywhere on the window to make it active"""
        # Don't activate if clicking on resize handles
        if 'resize-handle' in event.target.className:
            return
        set_window_active(move_div, 100)
    
    draggable_move_proxy = create_proxy(draggableMove)
    holding_mouse_proxy = create_proxy(holdingMouse)
    release_mouse_proxy = create_proxy(releaseMouse)
    click_proxy = create_proxy(handleClick)
    
    if top_bar:
        top_bar.addEventListener("mousedown", holding_mouse_proxy)
    
    # Add click listener to entire div to handle focus
    move_div.addEventListener("mousedown", click_proxy)

    document.addEventListener("mouseup", release_mouse_proxy)

# Initialize all movable divs
all_movable_divs = document.querySelectorAll(".movable-div")

for div in all_movable_divs:
    make_draggable(div)

# Expose the set_window_active function for use by modal system
window.set_window_active = set_window_active