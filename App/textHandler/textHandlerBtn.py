from pyscript import window, document
from js import console, Date
import asyncio

console.log("Python script loading...")

# Track last click time
last_click_time = 0
click_delay = 100

async def show_tutorial(dialogue_key="tutorial"):
    """Show tutorial dialog with specific dialogue sequence"""
    try:
        console.log(f"=== SHOW TUTORIAL DEBUG ===")
        console.log(f"Requested dialogue: {dialogue_key}")
        
        if not hasattr(window, 'TextHandler'):
            console.error("TextHandler not found!")
            return
        
        # Create handler if doesn't exist
        if not hasattr(window, 'currentHandler'):
            console.log("Creating new handler...")
            handler = window.TextHandler.new()
            console.log("Loading JSON file...")
            success = await handler.loadFromFile("../App/textHandler/textData.json")
            
            console.log(f"JSON load success: {success}")
            
            if not success:
                console.error("Failed to load JSON file!")
                return
                
            window.currentHandler = handler
            console.log(f"Handler data exists: {window.currentHandler.data is not None}")
        else:
            console.log("Using existing handler")
        
        # Try to access the data directly
        handler = window.currentHandler
        console.log(f"Handler.data type: {type(handler.data)}")
        console.log(f"Handler.data: {handler.data}")
        
        # Load the specific dialogue
        console.log(f"Calling loadSequence with: {dialogue_key}")
        handler.loadSequence(dialogue_key)
        
        # Check what was loaded
        console.log(f"Handler.texts length: {len(handler.texts)}")
        console.log(f"Handler.texts: {handler.texts}")
        
        if len(handler.texts) == 0:
            console.error(f"❌ No texts found for key: {dialogue_key}")
            console.error("Available keys in your JSON should include this key!")
            return
        
        # Open dialog
        console.log("Opening dialog...")
        dialog = document.querySelector("#textDialog")
        dialog.showModal()
        
        console.log("✅ Tutorial dialog opened successfully")
    except Exception as e:
        console.error(f"❌ Error showing tutorial: {e}")
        import traceback
        console.error(traceback.format_exc())

async def text_Start(event):
    console.log("Button clicked!")
    
    try:
        if not hasattr(window, 'TextHandler'):
            console.error("TextHandler not found on window!")
            return
        
        console.log("Creating handler...")
        handler = window.TextHandler.new()
        
        console.log("Loading JSON...")
        success = await handler.loadFromFile("../App/textHandler/textData.json")
        
        if success:
            console.log("JSON loaded, loading sequence...")
            handler.loadSequence("tutorial")
            window.currentHandler = handler
            
            console.log("Opening dialog...")
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
        console.log("Click ignored (too soon)")
        return
    
    last_click_time = current_time
    console.log("Text box clicked!")
    
    if hasattr(window, 'currentHandler'):
        window.currentHandler.nextText()

# Attach event listeners
console.log("Attaching event listeners...")
btn = document.getElementById("startButton")
if btn:
    console.log("Button found, attaching handler")
    btn.onclick = text_Start
else:
    console.error("startButton not found!")

txt = document.getElementById("textBox")
if txt:
    txt.onclick = next_text

# Expose show_tutorial to window so other scripts can call it
window.show_tutorial = show_tutorial

console.log("Python script loaded!")
console.log("✅ show_tutorial function exposed to window")