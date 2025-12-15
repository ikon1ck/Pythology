from pyscript import window, document
from pyodide.ffi import create_proxy
import asyncio

set_goal = window.set_goal

class LevelSetup:
    def __init__(self):
        self.current_level = 0
        self.completed_levels = set()
        self.categories = {
            "Chapter 1: First Steps": [0, 1, 2, 3],
        }
        self.levels = [
            {
                "name": "Level 1: Hello World",
                "code": None,
                "output": "10",
                "variables": None,
                "must_have": ["print"],
                "tutorial": "level1",
                "completion": "level1_complete"
            },

            {
                "name": "Level 1: Hello World",
                "code": None,
                "output": "10",
                "variables": None,
                "must_have": ["print"],
                "tutorial": "level1",
                "completion": "level1_complete"
            },
        ]
        
        # Hook into goal tracker to detect completion
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
        original_check = window.goal_tracker.check_match
        
        def wrapped_check(code, output):
            result = original_check(code, output)
            if result:
                # Goal was completed!
                self.on_level_complete()
            return result
        
        window.goal_tracker.check_match = create_proxy(wrapped_check)
    
    def on_level_complete(self):
        """Called when current level is completed"""
        window.console.log(f"🎉 Level {self.current_level + 1} completed!")
        self.completed_levels.add(self.current_level)
        self.render_levels()
        
        # Show completion dialogue if it exists
        level = self.levels[self.current_level]
        if "completion" in level and level["completion"]:
            import asyncio
            asyncio.ensure_future(window.show_tutorial(level["completion"]))
        
        # Write to terminal
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
                await self.start_lvl(next_lvl)  # Add await here
        else:
            self.terminal_write("No more levels available!")
    
    async def retry_level(self):
        """Retry current level"""
        self.terminal_write(f"🔄 Retrying Level {self.current_level + 1}")
        # Reset goal tracker so it can be completed again
        window.goal_tracker.goal_completed = False
        await self.start_lvl(self.current_level)  # Add await here
    
    async def start_lvl(self, lvl_num):
        if self.is_locked(lvl_num):
            window.console.log(f"🔒 Level {lvl_num + 1} is locked!")
            self.terminal_write(f"🔒 Level {lvl_num + 1} is locked! Complete previous levels first.")
            return
        
        self.current_level = lvl_num
        level = self.levels[lvl_num]
        
        # Show tutorial if it exists
        if "tutorial" in level and level["tutorial"]:
            await window.show_tutorial(level["tutorial"])
        
        # Write to terminal
        self.terminal_write("=" * 50)
        self.terminal_write(f"🎮 LEVEL {lvl_num + 1}: {level['name']}")
        self.terminal_write("=" * 50)
        self.terminal_write(f"Expected output: {level['output']}")
        if level['must_have']:
            self.terminal_write(f"Must use: {', '.join(level['must_have'])}")
        self.terminal_write("Good luck!")
        self.terminal_write("")
        
        window.console.log(f"🎮 Starting {level['name']}")

        set_goal(
            level["code"],
            level["output"],
            level["variables"],
            level["must_have"]
        )
        
        self.close_modal()
        self.render_levels()
    
    def is_locked(self, lvl_num):
        # Level 0 is always unlocked
        if lvl_num == 0:
            return False
        # Check if previous level is completed
        return (lvl_num - 1) not in self.completed_levels
    
    def open_modal(self):
        modal = document.getElementById("lvl-Selector")
        modal.showModal()
        self.render_levels()
    
    def close_modal(self):
        modal = document.getElementById("lvl-Selector")
        modal.close()
    
    def render_levels(self):
        wrapper = document.getElementById("wrapper")
        wrapper.innerHTML = ""
        
        # Title
        title = document.createElement("h1")
        title.className = "big-Text"
        title.textContent = "level selector"
        wrapper.appendChild(title)
        
        # Render categories
        for category_name, level_nums in self.categories.items():
            # Category header
            category_header = document.createElement("h2")
            category_header.className = "smol-Text"
            category_header.textContent = category_name
            wrapper.appendChild(category_header)
            
            # Level buttons container
            for lvl_num in level_nums:
                if lvl_num >= len(self.levels):
                    continue
                    
                btn = document.createElement("button")
                btn.className = "Btn-Lvl"
                btn.id = str(lvl_num)
                
                # Set button text with completion marker
                btn_text = str(lvl_num + 1)
                if lvl_num in self.completed_levels:
                    btn_text = "✓"
                elif self.is_locked(lvl_num):
                    btn_text = btn_text
                
                btn.textContent = btn_text
                
                if not self.is_locked(lvl_num):
                    btn.onclick = create_proxy(lambda e, num=lvl_num: start_lvl(num))  # Uses the wrapper function
                
                wrapper.appendChild(btn)


# Initialize
level_Setup = LevelSetup()

# Expose functions to window for py-click
def open_modal(event=None):
    level_Setup.open_modal()

def start_lvl(num):
    asyncio.ensure_future(level_Setup.start_lvl(num))

def next_lvl(event=None):
    """Command to go to next level"""
    asyncio.ensure_future(level_Setup.next_level())  # Wrap in ensure_future

def retry_lvl(event=None):
    """Command to retry current level"""
    asyncio.ensure_future(level_Setup.retry_level())  # Wrap in ensure_future

# Create proxies
open_modal_proxy = create_proxy(open_modal)
start_lvl_proxy = create_proxy(start_lvl)
next_lvl_proxy = create_proxy(next_lvl)
retry_lvl_proxy = create_proxy(retry_lvl)

# Attach to window
window.open_modal = open_modal_proxy
window.start_lvl = start_lvl_proxy
window.next_lvl = next_lvl_proxy
window.retry_lvl = retry_lvl_proxy

window.console.log("🎮 Level System Ready!")
window.console.log("Commands: next_lvl, retry_lvl")