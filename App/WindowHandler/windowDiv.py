from pyscript import window, document
from pyodide.ffi import create_proxy
import asyncio

async def wait_for_dom():
    """Wait a bit for DOM to be ready"""
    await asyncio.sleep(0.1)

def close_all_modals_on_start():
    """Ensure all dialogs are closed when page loads"""
    all_dialogs = document.querySelectorAll('dialog.movable-div')
    for dialog in all_dialogs:
        if dialog.open:
            dialog.close()
        dialog.style.display = ''
    window.console.log(f"✅ Closed {len(all_dialogs)} dialogs on startup")

def open_modal_by_id(modal_id):
    """Open a modal dialog by its ID"""
    dialog = document.getElementById(modal_id)
    
    if not dialog:
        window.console.error(f"Dialog with id '{modal_id}' not found")
        return
    
    window.console.log(f"Opening modal: {modal_id}, current open state: {dialog.open}")
    
    # Reset display style
    dialog.style.display = ''
    
    # Open the dialog
    try:
        if not dialog.open:
            dialog.show()
            window.console.log(f"✅ Modal opened: {modal_id}")
        else:
            window.console.log(f"Modal already open: {modal_id}")
    except Exception as e:
        window.console.error(f"Error opening dialog: {e}")
        return
    
    # Make it active using the unified system
    if hasattr(window, 'set_window_active'):
        window.set_window_active(dialog, 100)

def open_modal(event):
    """Open a modal dialog window from button click"""
    button = event.target
    modal_id = button.getAttribute('data-modal-id')
    
    if not modal_id:
        window.console.error("No modal-id specified on button")
        return
    
    open_modal_by_id(modal_id)

def minimize_modal(event):
    """Minimize a modal dialog window"""
    button = event.target
    dialog = button.closest('dialog')
    
    if dialog:
        window.console.log(f"Minimizing modal: {dialog.id}")
        # Hide using display none (keeps dialog open state)
        dialog.style.display = 'none'
    
    # Stop ALL event propagation
    event.stopPropagation()
    event.preventDefault()
    return False

def setup_modal_buttons():
    """Setup all modal control buttons"""
    # Open buttons
    open_buttons = document.querySelectorAll('[data-modal-id]')
    window.console.log(f"Found {len(open_buttons)} buttons with data-modal-id")
    
    for button in open_buttons:
        parent_class = button.parentElement.className if button.parentElement else ""
        if 'items_Modal' in parent_class:
            button.addEventListener('click', create_proxy(open_modal))
            window.console.log(f"Attached click handler to button for: {button.getAttribute('data-modal-id')}")
    
    # Minimize buttons
    minimize_buttons = document.querySelectorAll('.minimize-modal-btn')
    window.console.log(f"Found {len(minimize_buttons)} minimize buttons")
    
    for button in minimize_buttons:
        button.addEventListener('click', create_proxy(minimize_modal))
    
    window.console.log("✅ Modal buttons setup complete")

async def init_modal_system():
    """Initialize the modal system"""
    await wait_for_dom()
    close_all_modals_on_start()
    setup_modal_buttons()

# Initialize
asyncio.create_task(init_modal_system())

# Expose functions to window for use anywhere
window.open_modal = open_modal
window.open_modal_by_id = open_modal_by_id
window.minimize_modal = minimize_modal