from pyscript import window, document
from pyodide.ffi import create_proxy

def resize_ace_editor(container_div):
    """Force Ace Editor to recalculate its dimensions"""
    try:
        # Find ace editor element inside the container
        editor_element = container_div.querySelector('.ace_editor')
        if editor_element:
            editor_id = editor_element.id
            if editor_id and hasattr(window.ace, 'edit'):
                editor = window.ace.edit(editor_id)
                editor.resize()
    except Exception as e:
        window.console.error(f"Error resizing ace editor: {e}")

def make_resizable(resize_div):
    """Make a div resizable by adding resize handles"""
    
    # Add resize handles to the div
    resize_div.insertAdjacentHTML('beforeend', '''
        <div class="resize-handle resize-n"></div>
        <div class="resize-handle resize-s"></div>
        <div class="resize-handle resize-e"></div>
        <div class="resize-handle resize-w"></div>
        <div class="resize-handle resize-nw"></div>
        <div class="resize-handle resize-ne"></div>
        <div class="resize-handle resize-sw"></div>
        <div class="resize-handle resize-se"></div>
    ''')
    
    # Get all resize handles
    handles = resize_div.querySelectorAll('.resize-handle')
    
    is_resizing = False
    start_x = 0
    start_y = 0
    start_width = 0
    start_height = 0
    start_left = 0
    start_top = 0
    current_handle = None
    
    def start_resize(event):
        nonlocal is_resizing, start_x, start_y, start_width, start_height
        nonlocal start_left, start_top, current_handle
        
        is_resizing = True
        start_x = event.clientX
        start_y = event.clientY
        
        rect = resize_div.getBoundingClientRect()
        start_width = rect.width
        start_height = rect.height
        start_left = rect.left
        start_top = rect.top
        
        current_handle = event.target
        
        # Add no-select class to prevent text selection
        document.body.classList.add('no-select')
        
        event.stopPropagation()
        event.preventDefault()
    
    def do_resize(event):
        nonlocal is_resizing
        
        if not is_resizing or current_handle is None:
            return
        
        dx = event.clientX - start_x
        dy = event.clientY - start_y
        
        # Minimum dimensions
        min_width = 200
        min_height = 150
        
        # Check which handle is being dragged
        if 'resize-se' in current_handle.className:
            # Bottom-right corner
            new_width = max(min_width, start_width + dx)
            new_height = max(min_height, start_height + dy)
            resize_div.style.width = f"{new_width}px"
            resize_div.style.height = f"{new_height}px"
            
        elif 'resize-s' in current_handle.className:
            # Bottom edge
            new_height = max(min_height, start_height + dy)
            resize_div.style.height = f"{new_height}px"
            
        elif 'resize-e' in current_handle.className:
            # Right edge
            new_width = max(min_width, start_width + dx)
            resize_div.style.width = f"{new_width}px"
            
        elif 'resize-n' in current_handle.className:
            # Top edge
            new_height = max(min_height, start_height - dy)
            if new_height > min_height:
                resize_div.style.height = f"{new_height}px"
                resize_div.style.top = f"{start_top + dy}px"
                
        elif 'resize-w' in current_handle.className:
            # Left edge
            new_width = max(min_width, start_width - dx)
            if new_width > min_width:
                resize_div.style.width = f"{new_width}px"
                resize_div.style.left = f"{start_left + dx}px"
                
        elif 'resize-nw' in current_handle.className:
            # Top-left corner
            new_width = max(min_width, start_width - dx)
            new_height = max(min_height, start_height - dy)
            if new_width > min_width:
                resize_div.style.width = f"{new_width}px"
                resize_div.style.left = f"{start_left + dx}px"
            if new_height > min_height:
                resize_div.style.height = f"{new_height}px"
                resize_div.style.top = f"{start_top + dy}px"
                
        elif 'resize-ne' in current_handle.className:
            # Top-right corner
            new_width = max(min_width, start_width + dx)
            new_height = max(min_height, start_height - dy)
            resize_div.style.width = f"{new_width}px"
            if new_height > min_height:
                resize_div.style.height = f"{new_height}px"
                resize_div.style.top = f"{start_top + dy}px"
                
        elif 'resize-sw' in current_handle.className:
            # Bottom-left corner
            new_width = max(min_width, start_width - dx)
            new_height = max(min_height, start_height + dy)
            if new_width > min_width:
                resize_div.style.width = f"{new_width}px"
                resize_div.style.left = f"{start_left + dx}px"
            resize_div.style.height = f"{new_height}px"
    
    def stop_resize(event):
        nonlocal is_resizing, current_handle
        is_resizing = False
        current_handle = None
        document.body.classList.remove('no-select')
        
        # Trigger resize event for Ace Editor
        resize_ace_editor(resize_div)
    
    # Create proxies
    start_resize_proxy = create_proxy(start_resize)
    do_resize_proxy = create_proxy(do_resize)
    stop_resize_proxy = create_proxy(stop_resize)
    
    # Add event listeners to all handles
    for handle in handles:
        handle.addEventListener('mousedown', start_resize_proxy)
    
    document.addEventListener('mousemove', do_resize_proxy)
    document.addEventListener('mouseup', stop_resize_proxy)


# Make all resizable divs resizable
all_resizable_divs = document.querySelectorAll('.resizable-div')

for div in all_resizable_divs:
    make_resizable(div)