from pyscript import window, document
from pyodide.ffi import create_proxy

last_active_div = None

def make_draggable(move_div):
    top_bar = move_div.querySelector(".top-bar")

    offset_x = 0
    offset_y = 0

    def overlay(zDex):
        global last_active_div

        if last_active_div == None:
            move_div.style.zIndex = zDex + 1
            last_active_div = move_div
            return

        if move_div != last_active_div:
            if last_active_div != None:
                last_active_div.style.zIndex = zDex - 1

            move_div.style.zIndex = zDex + 1
            last_active_div = move_div
            return
    
    def draggableMove(event):
        nonlocal offset_x, offset_y
        
        position_x = event.clientX - offset_x
        position_y = event.clientY - offset_y
        
        move_div.style.left = f"{position_x}px"
        move_div.style.top = f"{position_y}px"
    
    def holdingMouse(event):
        overlay(1)
        nonlocal offset_x, offset_y
        
        rect = move_div.getBoundingClientRect()
        offset_x = event.clientX - rect.left
        offset_y = event.clientY - rect.top
        
        document.addEventListener("mousemove", draggable_move_proxy)
    
    def releaseMouse(event):
        document.removeEventListener("mousemove", draggable_move_proxy)
    
    draggable_move_proxy = create_proxy(draggableMove)
    holding_mouse_proxy = create_proxy(holdingMouse)
    release_mouse_proxy = create_proxy(releaseMouse)
    
    if top_bar:
        top_bar.addEventListener("mousedown", holding_mouse_proxy)

    document.addEventListener("mouseup", release_mouse_proxy)

all_movable_divs = document.querySelectorAll(".movable-div")

for div in all_movable_divs:
    make_draggable(div)