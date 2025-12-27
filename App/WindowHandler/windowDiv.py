from pyscript import window, document
from pyodide.ffi import create_proxy
import asyncio

async def wait_for_dom():
    """Wait for DOM to be ready"""
    await asyncio.sleep(0.3)

def close_all_modals_on_start():
    """Ensure all dialogs are closed when page loads (except tutorial dialog)"""
    all_dialogs = document.querySelectorAll('dialog')
    
    for dialog in all_dialogs:
        # Skip the tutorial dialog - it manages itself
        if dialog.id == 'textDialog':
            continue
            
        dialog.style.display = 'none'
        if dialog.open:
            try:
                dialog.close()
            except:
                pass
    

def open_modal_by_id(modal_id):
    """Open a modal dialog by its ID"""
    dialog = document.getElementById(modal_id)
    
    if not dialog:
        window.console.error(f"Dialog '{modal_id}' not found")
        return
    
    # Make it visible first
    dialog.style.display = ''
    
    # Then open the dialog
    try:
        if not dialog.open:
            dialog.show()
    except Exception as e:
        window.console.error(f"Error opening dialog: {e}")
        return
    
    # Make it active using the unified system
    if hasattr(window, 'set_window_active'):
        window.set_window_active(dialog, 100)

def handle_level_button(event):
    """Handle level button click"""
    open_modal_by_id('lvl-Selector')
    event.stopPropagation()
    event.preventDefault()

def handle_modal_button(event):
    """Handle modal button click"""
    button = event.currentTarget
    modal_id = button.getAttribute('data-modal-id')
    
    
    if modal_id:
        open_modal_by_id(modal_id)
    
    event.stopPropagation()
    event.preventDefault()

def minimize_modal(event):
    """Minimize a modal dialog window"""
    button = event.target
    dialog = button.closest('dialog')
    
    if dialog:
        dialog.style.display = 'none'
    
    event.stopPropagation()
    event.preventDefault()

async def init_modal_system():
    """Initialize the modal system"""
    await wait_for_dom()
    
    # Hide all dialogs
    close_all_modals_on_start()
    
    # Setup level button
    level_button = document.querySelector("#level-modal-btn")
    if level_button:
        level_button.onclick = create_proxy(handle_level_button)
    
    # Setup modal buttons
    editor_button = document.querySelector("#editor-modal-btn")
    if editor_button:
        editor_button.onclick = create_proxy(handle_modal_button)
    
    terminal_button = document.querySelector("#terminal-modal-btn")
    if terminal_button:
        terminal_button.onclick = create_proxy(handle_modal_button)
    
    # Setup minimize buttons
    minimize_buttons = document.querySelectorAll('.minimize-modal-btn')
    for button in minimize_buttons:
        button.onclick = create_proxy(minimize_modal)
    

# Initialize
asyncio.create_task(init_modal_system())

# Expose functions
window.open_modal_by_id = open_modal_by_id