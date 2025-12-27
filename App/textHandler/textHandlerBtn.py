from pyscript import window, document
from pyodide.ffi import create_proxy
from js import console, Date, setTimeout
import asyncio


# Track last click time
last_click_time = 0
click_delay = 100

async def show_tutorial(dialogue_key="tutorial"):
    """Show tutorial dialog with specific dialogue sequence"""
    try:
        if not hasattr(window, 'TextHandler'):
            console.error("TextHandler not found!")
            return
        
        # Create handler if doesn't exist
        if not hasattr(window, 'currentHandler'):
            handler = window.TextHandler.new()
            success = await handler.loadFromFile("../App/textHandler/textData.json")
            
            
            if not success:
                console.error("Failed to load JSON file!")
                return
                
            window.currentHandler = handler
        # Try to access the data directly
        handler = window.currentHandler
        
        # Load the specific dialogue
        handler.loadSequence(dialogue_key)
        
        if len(handler.texts) == 0:
            console.error(f"❌ No texts found for key: {dialogue_key}")
            console.error("Available keys in your JSON should include this key!")
            return
        
        # Open dialog
        dialog = document.querySelector("#textDialog")
        dialog.showModal()
        
    except Exception as e:
        console.error(f"❌ Error showing tutorial: {e}")
        import traceback
        console.error(traceback.format_exc())

def hide_title_screen():
    """Smoothly hide the title screen"""
    menu = document.querySelector(".starting-Menu")
    if menu:
        # Add fade-out class to trigger transition
        menu.classList.add("fade-out")
        
        # After transition completes, hide completely
        def complete_hide():
            menu.classList.add("hidden")
        
        # Create a proxy so the function persists for setTimeout
        hide_proxy = create_proxy(complete_hide)
        setTimeout(hide_proxy, 600)  # Match the CSS transition duration

async def text_Start(event):
    
    try:
        # First, hide the title screen
        hide_title_screen()
        
        # Wait a bit for the transition to look smoother
        await asyncio.sleep(0.3)
        
        if not hasattr(window, 'TextHandler'):
            console.error("TextHandler not found on window!")
            return
        
        handler = window.TextHandler.new()
        
        success = await handler.loadFromFile("../App/textHandler/textData.json")
        
        if success:
            handler.loadSequence("tutorial")
            window.currentHandler = handler
            
            dialog = document.querySelector("#textDialog")
            dialog.showModal()
        else:
            console.error("Failed to load JSON!")
    except Exception as e:
        console.error(f"Error: {e}")

def next_text(event):
    global last_click_time
    
    current_time = Date.new().getTime()
    
    if current_time - last_click_time < click_delay:
        return
    
    last_click_time = current_time
    
    if hasattr(window, 'currentHandler'):
        window.currentHandler.nextText()

# Attach event listeners
btn = document.getElementById("startButton")
if btn:
    btn.onclick = text_Start
else:
    console.error("startButton not found!")

txt = document.getElementById("textBox")
if txt:
    txt.onclick = next_text

# Expose show_tutorial to window so other scripts can call it
window.show_tutorial = show_tutorial
