from pyscript import window, document
from pyodide.ffi import create_proxy
import asyncio

set_goal = window.set_goal

class LevelSetup:
    def __init__(self):
        self.current_level = 0
        self.completed_levels = set()
        self.levels = [
            {
                "name": "Level 1: Hello World",
                "code": None,
                "output": "10",
                "variables": None,
                "must_have": ["print"],
                "tutorial": "level1",
                "completion": "level1_complete"
            }
        ]
        self.categories = {
            "Chapter 1: First Steps": [0, 1, 2, 3],
        }
        self.setup_completion_detection()
    
    def get_terminal(self):
        """Safely get terminal object"""
        try:
            if hasattr(window, 'terminal') and window.terminal is not None:
                return window.terminal
        except:
            pass
        return None
    
    def terminal_write(self, text):
        """Write to terminal if available"""
        terminal = self.get_terminal()
        if terminal:
            terminal.write(text)
        else:
             window.console.log(text)
    
    def setup_completion_detection(self):
        """Monitor goal_tracker for completion"""
        try:
            original_check = window.goal_tracker.check_match
            
            def wrapped_check(code, output):
                result = original_check(code, output)
                if result:
                    self.on_level_complete()
                return result
            
            window.goal_tracker.check_match = create_proxy(wrapped_check)
        except Exception as e:
            window.console.error(f"Error setting up completion detection: {e}")
    
    def on_level_complete(self):
        self.completed_levels.add(self.current_level)
        self.render_levels()
        
        level = self.levels[self.current_level]
        if "completion" in level and level["completion"]:
            asyncio.ensure_future(window.show_tutorial(level["completion"]))
        
        self.terminal_write("=" * 50)
        self.terminal_write(f"🎉 LEVEL {self.current_level + 1} COMPLETED!")
        self.terminal_write("=" * 50)
        
        next_level = self.current_level + 1
        if next_level < len(self.levels):
            self.terminal_write(f"✅ Level {next_level + 1} unlocked!")
            self.terminal_write(f"Type 'next_lvl' to continue or open level selector")
        else:
            self.terminal_write("🏆 ALL LEVELS COMPLETED! Congratulations!")
    
    async def next_level(self):
        """Go to next level"""
        next_lvl = self.current_level + 1
        if next_lvl < len(self.levels):
            if self.is_locked(next_lvl):
                self.terminal_write("🔒 Complete current level first!")
            else:
                await self.start_lvl(next_lvl)
        else:
            self.terminal_write("No more levels available!")
    
    async def retry_level(self):
        """Retry current level"""
        self.terminal_write(f"🔄 Retrying Level {self.current_level + 1}")
        window.goal_tracker.goal_completed = False
        await self.start_lvl(self.current_level)
    
    async def start_lvl(self, lvl_num):
        if self.is_locked(lvl_num):
            self.terminal_write(f"🔒 Level {lvl_num + 1} is locked! Complete previous levels first.")
            return
        
        self.current_level = lvl_num
        level = self.levels[lvl_num]
        
        if "tutorial" in level and level["tutorial"]:
            try:
                await window.show_tutorial(level["tutorial"])
            except:
                pass
        
        self.terminal_write("=" * 50)
        self.terminal_write(f"🎮 LEVEL {lvl_num + 1}: {level['name']}")
        self.terminal_write("=" * 50)
        self.terminal_write(f"Expected output: {level['output']}")
        if level['must_have']:
            self.terminal_write(f"Must use: {', '.join(level['must_have'])}")
        self.terminal_write("Good luck!")
        self.terminal_write("")

        set_goal(
            level["code"],
            level["output"],
            level["variables"],
            level["must_have"]
        )
        
        self.close_modal()
        self.render_levels()
    
    def is_locked(self, lvl_num):
        if lvl_num == 0:
            return False
        return (lvl_num - 1) not in self.completed_levels
    
    def open_modal(self):
         
        modal = document.getElementById("lvl-Selector")
         
        if modal:
            modal.showModal()
             
            self.render_levels()
             
        else:
            window.console.error("Modal not found!")
    
    def close_modal(self):
        modal = document.getElementById("lvl-Selector")
        if modal:
            modal.close()
    
    def render_levels(self):
         
        wrapper = document.getElementById("wrapper")
         
        
        if not wrapper:
            window.console.error("Wrapper not found!")
            return
        
         
         
        
        # Build HTML string
        html = '<h1 class="big-Text">level selector</h1>'
         
        
        for category_name, level_nums in self.categories.items():
             
            html += f'<h2 class="smol-Text">{category_name}</h2>'
            
            for lvl_num in level_nums:
                 
                if lvl_num >= len(self.levels):
                     
                    continue
                
                btn_text = str(lvl_num + 1)
                if lvl_num in self.completed_levels:
                    btn_text = "✓"
                
                is_locked = self.is_locked(lvl_num)
                 
                
                disabled = "disabled" if is_locked else ""
                onclick = f"window.level_Setup.start_level_sync({lvl_num})" if not is_locked else ""
                
                button_html = f'<button class="Btn-Lvl" id="level-btn-{lvl_num}" {disabled} onclick="{onclick}">{btn_text}</button>'
                html += button_html
                 
        
         
        wrapper.innerHTML = html
         
         
    
    def start_level_sync(self, lvl_num):
        """Synchronous wrapper for onclick"""
        asyncio.ensure_future(self.start_lvl(lvl_num))


# Initialize
level_Setup = LevelSetup()

# Expose to window for onclick handlers
window.level_Setup = level_Setup

# Expose functions to window - these are the main entry points
def open_modal(event=None):
     
    level_Setup.open_modal()

def start_lvl(num):
     
    asyncio.ensure_future(level_Setup.start_lvl(num))

def next_lvl(event=None):
     
    asyncio.ensure_future(level_Setup.next_level())

def retry_lvl(event=None):
     
    asyncio.ensure_future(level_Setup.retry_level())

# Create proxies and attach to window
window.open_modal = create_proxy(open_modal)
window.start_lvl = create_proxy(start_lvl)
window.next_lvl = create_proxy(next_lvl)
window.retry_lvl = create_proxy(retry_lvl)

 
 

# TEST: Try to write to wrapper immediately
def test_wrapper():
     
    wrapper = document.getElementById("wrapper")
     
    if wrapper:
         
        wrapper.innerHTML = "<h1>TEST - CAN YOU SEE THIS?</h1><button>Test Button</button>"
         
    else:
        window.console.error("❌ WRAPPER NOT FOUND!")

# Run test after a short delay to ensure DOM is ready
import js
js.setTimeout(create_proxy(test_wrapper), 100)

# Also try calling render_levels directly after a delay
def test_render():
     
    level_Setup.render_levels()

js.setTimeout(create_proxy(test_render), 500)