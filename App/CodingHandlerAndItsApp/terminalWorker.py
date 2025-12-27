from pyscript import document, window
from js import ace, console
from pyodide.ffi import create_proxy
import sys
import asyncio

class AceTerminal:
    def __init__(self, terminal_element_id):
        self.terminal_id = terminal_element_id
        self.editor = None
        self.history = []
        self.history_index = -1
        self.current_prompt = ""
        self.waiting_for_input = False
        self.input_promise = None
        self.last_valid_content = ""
        self.is_updating = False
        self.last_output = ""  # Track last output
        self.execution_output = []  # Track all output from current execution
        
    def setup_ace(self):
        """Initialize Ace Editor as terminal"""
        try:
            element = document.getElementById(self.terminal_id)
            if not element:
                console.error(f"Element with id '{self.terminal_id}' not found!")
                return False
                
            self.editor = ace.edit(self.terminal_id)
            
            self.editor.setTheme("ace/theme/terminal")
            self.editor.session.setMode("ace/mode/python")
            
            options = {
                "fontSize": "14px",
                "showGutter": False,
                "showPrintMargin": False,
                "highlightActiveLine": False,
                "readOnly": False,
                "wrap": True
            }
            self.editor.setOptions(options)
            
            self.editor.setValue(self.current_prompt, -1)
            self.last_valid_content = self.current_prompt
            self.editor.navigateFileEnd()
            
            self.setup_event_listeners()
            
            return True
            
        except Exception as e:
            console.error(f"Error initializing terminal: {e}")
            return False
        
    def setup_event_listeners(self):
        """Setup event listeners on the text input"""
        textarea = self.editor.textInput.getElement()
        
        keydown_proxy = create_proxy(self.handle_keydown)
        textarea.addEventListener('keydown', keydown_proxy)
        
        change_proxy = create_proxy(self.handle_change)
        self.editor.on('change', change_proxy)
        
    def handle_change(self, delta, editor):
        """Prevent editing anything except current input line"""
        if self.is_updating:
            return
            
        content = self.editor.getValue()
        lines = content.split('\n')
        
        # Check if change was on a previous line
        if delta.start.row < len(lines) - 1:
            # Restore to last valid content
            self.is_updating = True
            self.editor.setValue(self.last_valid_content, -1)
            self.editor.navigateFileEnd()
            self.is_updating = False
            return
        
        # Update last valid content
        self.last_valid_content = content
        
        cursor = self.editor.getCursorPosition()
        
        # Force cursor to last line
        if cursor.row < len(lines) - 1:
            self.editor.navigateFileEnd()
        elif cursor.row == len(lines) - 1:
            prompt_length = len(self.current_prompt) if not self.waiting_for_input else 0
            if cursor.column < prompt_length:
                self.editor.moveCursorTo(cursor.row, prompt_length)
                
    def handle_keydown(self, event):
        """Handle all keyboard events"""
        key = event.key
        cursor = self.editor.getCursorPosition()
        content = self.editor.getValue()
        lines = content.split('\n')
        selection = self.editor.getSelectionRange()
        
        # Prevent backspace from deleting previous lines
        if key == "Backspace":
            prompt_length = len(self.current_prompt) if not self.waiting_for_input else 0
            if cursor.row == len(lines) - 1 and cursor.column <= prompt_length:
                event.preventDefault()
                return
            if cursor.row < len(lines) - 1:
                event.preventDefault()
                return
            # Check if selection includes previous lines
            if selection.start.row < len(lines) - 1:
                event.preventDefault()
                return
    
        # Prevent Delete key from deleting previous lines
        if key == "Delete":
            if cursor.row < len(lines) - 1:
                event.preventDefault()
                return
            if selection.start.row < len(lines) - 1:
                event.preventDefault()
                return
        
        # Prevent typing on previous lines
        if len(key) == 1 or key == "Space":  # Regular character keys
            if cursor.row < len(lines) - 1:
                event.preventDefault()
                return
        
        # Prevent cut operation on previous lines
        if (key == "x" or key == "X") and (event.ctrlKey or event.metaKey):
            if selection.start.row < len(lines) - 1:
                event.preventDefault()
                return
            
        if key == "Enter":
            event.preventDefault()
            self.handle_enter()
        elif key == "ArrowUp":
            if cursor.row == len(lines) - 1:
                event.preventDefault()
                self.handle_up()
        elif key == "ArrowDown":
            if cursor.row == len(lines) - 1:
                event.preventDefault()
                self.handle_down()

    def handle_enter(self):
        content = self.editor.getValue()
        lines = content.split('\n')
        last_line = lines[-1]
        
        # If waiting for input, resolve the promise
        if self.waiting_for_input:
            user_input = last_line
            self.is_updating = True
            self.editor.insert('\n')
            self.last_valid_content = self.editor.getValue()
            self.is_updating = False
            
            if self.input_promise:
                self.input_promise.set_result(user_input)
                self.input_promise = None
                self.waiting_for_input = False
            return
        
        # Normal command execution
        command = last_line[len(self.current_prompt):]
        
        self.is_updating = True
        self.editor.insert('\n')
        self.last_valid_content = self.editor.getValue()
        self.is_updating = False
        
        if command.strip():
            self.add_to_history(command)
            
            if command.strip() == "clear":
                self.clear()
                return
            elif command.strip() == "next_lvl":
                self.clear()
                window.next_lvl()
                return
            elif command.strip() == "retry_lvl":
                self.clear()
                window.retry_lvl()
                return
            else:
                self.execute_code(command)
            
    def handle_up(self):
        """Navigate command history backwards"""
        if self.waiting_for_input:
            return
            
        if self.history and self.history_index > 0:
            self.history_index -= 1
            self.replace_current_line(self.current_prompt + self.history[self.history_index])
        elif len(self.history) > 0 and self.history_index == -1:
            self.history_index = len(self.history) - 1
            self.replace_current_line(self.current_prompt + self.history[self.history_index])
            
    def handle_down(self):
        """Navigate command history forwards"""
        if self.waiting_for_input:
            return
            
        if self.history_index < len(self.history) - 1 and self.history_index != -1:
            self.history_index += 1
            self.replace_current_line(self.current_prompt + self.history[self.history_index])
        else:
            self.history_index = len(self.history)
            self.replace_current_line(self.current_prompt)
            
    def replace_current_line(self, new_line):
        """Replace the current input line"""
        content = self.editor.getValue()
        lines = content.split('\n')
        lines[-1] = new_line
        
        self.is_updating = True
        self.editor.setValue('\n'.join(lines), -1)
        self.last_valid_content = self.editor.getValue()
        self.editor.navigateFileEnd()
        self.is_updating = False
        
    def write(self, text):
        if not self.editor:
            return
            
        if not text.strip():
            return
        
        self.last_output = str(text)

        self.execution_output.append(str(text))
        
        content = self.editor.getValue()
        lines = content.split('\n')
        
        current_input = lines[-1]
        lines = lines[:-1]
        
        lines.append(str(text))
        
        lines.append(current_input)
        
        self.is_updating = True
        self.editor.setValue('\n'.join(lines), -1)
        self.last_valid_content = self.editor.getValue()
        self.editor.navigateFileEnd()
        self.is_updating = False
        
    def write_error(self, text):
        """Write error text"""
        self.write(f"Error: {text}")
        
    def clear(self):
        """Clear terminal"""
        if self.editor:
            self.is_updating = True
            self.editor.setValue(self.current_prompt, -1)
            self.last_valid_content = self.current_prompt
            self.editor.navigateFileEnd()
            self.is_updating = False
        
    def add_to_history(self, command):
        """Add command to history"""
        if command.strip():
            self.history.append(command)
            self.history_index = len(self.history)
    
    def get_last_output(self):
        """Get the last output text"""
        return self.last_output
    
    def get_execution_output(self):
        """Get all output from current execution"""
        return '\n'.join(self.execution_output)
    
    def clear_execution_output(self):
        """Clear the execution output buffer"""
        self.execution_output = []
    
    async def custom_input(self, prompt_text=""):
        """Async input implementation"""
        if prompt_text:
            self.write(prompt_text)
        
        self.input_promise = asyncio.Future()
        self.waiting_for_input = True
        
        result = await self.input_promise
        return result
            
    def execute_code(self, code):
        if not code.strip():
            self.write("No code to execute")
            return
        
        self.clear_execution_output()
        
        async def run():
            try:
                modified_code = code.replace('input(', 'await terminal.custom_input(')
                
                code_obj = compile(
                    f"async def __exec_wrapper():\n" + 
                    "\n".join(f"    {line}" for line in modified_code.split('\n')) +
                    "\n",
                    '<terminal>',
                    'exec'
                )
                
                exec_globals = globals().copy()
                exec(code_obj, exec_globals)
                
                await exec_globals['__exec_wrapper']()
                    
            except Exception as e:
                import traceback
                self.write_error(f"{type(e).__name__}: {e}")
                console.error(traceback.format_exc())
        
        asyncio.create_task(run())


# Initialize terminal
terminal = AceTerminal("terminal")

async def init_terminal():
    await asyncio.sleep(0.1)
    if terminal.setup_ace():
        class TerminalWriter:
            def __init__(self, terminal, is_error=False):
                self.terminal = terminal
                self.is_error = is_error
                
            def write(self, text):
                if text.strip():
                    if self.is_error:
                        self.terminal.write_error(text.strip())
                    else:
                        self.terminal.write(text.strip())
                        
            def flush(self):
                pass

        sys.stdout = TerminalWriter(terminal)
        sys.stderr = TerminalWriter(terminal, is_error=True)

        terminal.write("Pythology terminal is ready to use!!!")
        terminal.write("You can type 'clear' to clear terminal.")
        
        # Expose terminal to window after setup
        window.terminal = terminal
    else:
        console.error("Failed to initialize terminal!")

asyncio.create_task(init_terminal())