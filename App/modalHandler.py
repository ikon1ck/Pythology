from pyscript import window, document
from pyodide.ffi import create_proxy

modal = document.querySelector("#lvl-Selector")
wrapper = document.querySelector("#wrapper")

def open_level_modal(e=None):
    """Open the level selector modal specifically"""
    if modal:
        modal.showModal()
         

def close_modal(e):
    """Close modal when clicking outside wrapper"""
    if modal and not wrapper.contains(e.target):
        modal.close()

# Create proxies
closer = create_proxy(close_modal)
opener = create_proxy(open_level_modal)

# Expose with a specific name to avoid conflicts
window.open_level_modal = opener

# Attach close handler to modal
if modal:
    modal.addEventListener("click", closer)

# Find and attach to the levels button specifically
level_button = document.querySelector("#level-modal-btn")
if level_button:
    level_button.addEventListener("click", opener)
     