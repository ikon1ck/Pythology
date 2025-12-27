from js import ace
from pyscript import window, document
from pyodide.ffi import create_proxy
import sys
import asyncio

class GoalTracker:
    def __init__(self):
        self.goal_code = ""
        self.goal_output = ""
        self.goal_variables = {}  # Track expected variables with values
        self.must_have = []  # Required code patterns
        self.checking_enabled = True
        self.goal_completed = False  # Track if current goal is completed
        self.goal_set = False  # Track if any goal has been set
        
    def set_goal(self, code, expected_output, variables=None, must_have=None):
        """
        Set the goal code and expected output
        
        Args:
            code: Expected code (or None to skip code checking)
            expected_output: Expected output
            variables: Dict of {value: description} for flexible variable names
                      Example: {5: "a number", "hello": "a greeting"}
            must_have: List of required patterns/keywords in code
                      Example: ["for", "range", "if"] or ["def ", "return"]
        """
        self.goal_code = code.strip() if code else ""
        self.goal_output = expected_output.strip()
        self.goal_variables = variables or {}
        self.must_have = must_have or []
        self.goal_completed = False  # Reset completion status
        self.goal_set = True  # Mark that a goal has been set
        
        window.console.log("✅ Goal set!")
        if self.goal_code:
            window.console.log(f"Expected code: {self.goal_code}")
        window.console.log(f"Expected output: {self.goal_output}")
        if self.goal_variables:
            window.console.log(f"Expected variables with values: {self.goal_variables}")
        if self.must_have:
            window.console.log(f"Must contain: {self.must_have}")
    
    def check_match(self, current_code, current_output):
        """Check if current code and output match the goal (case-insensitive)"""
        # Don't check if no goal has been set yet
        if not self.goal_set:
            return False
            
        # Don't check if goal is already completed
        if self.goal_completed:
            window.console.log("⏸️ Goal already completed! Set a new goal to continue.")
            return False
            
        if not self.checking_enabled:
            return False
        
        # Check code match (if goal_code is set)
        code_match = True
        if self.goal_code:
            code_match = current_code.strip().lower() == self.goal_code.lower()
        
        # Check output match (case-insensitive)
        output_match = current_output.strip().lower() == self.goal_output.lower()
        
        # Check variables (if any are specified)
        variables_match = True
        if self.goal_variables:
            variables_match = self._check_variables(current_code)
        
        # Check must_have patterns
        must_have_match = True
        if self.must_have:
            must_have_match = self._check_must_have(current_code)
        
        if code_match and output_match and variables_match and must_have_match:
            window.console.log("🎉 SUCCESS! Everything is correct!")
            if self.goal_code:
                window.console.log("✓ Code matches goal")
            window.console.log("✓ Output matches goal")
            if self.goal_variables:
                window.console.log("✓ Variables match goal")
            if self.must_have:
                window.console.log("✓ Required patterns found")
            
            # Mark goal as completed
            self.goal_completed = True
            window.console.log("🏁 Goal completed! Set a new goal to continue.")
            return True
        else:
            if not code_match:
                window.console.log("❌ Code doesn't match goal")
                window.console.log(f"Current: '{current_code.strip()}'")
                window.console.log(f"Expected: '{self.goal_code}'")
            if not output_match:
                window.console.log("❌ Output doesn't match goal")
                window.console.log(f"Current: '{current_output.strip()}'")
                window.console.log(f"Expected: '{self.goal_output}'")
            if not variables_match:
                window.console.log("❌ Variables don't match goal")
            if not must_have_match:
                window.console.log("❌ Required patterns not found")
            return False
    
    def _check_must_have(self, code):
        """Check if code contains all required patterns"""
        code_lower = code.lower()
        missing = []
        
        for pattern in self.must_have:
            if pattern.lower() not in code_lower:
                missing.append(pattern)
                window.console.log(f"✗ Missing required pattern: '{pattern}'")
            else:
                window.console.log(f"✓ Found required pattern: '{pattern}'")
        
        return len(missing) == 0
    
    def _check_variables(self, code):
        """Check if code creates variables with expected values"""
        try:
            # Create a clean namespace to execute code
            namespace = {}
            exec(code, namespace)
            
            # Check if any variable has the expected values
            for expected_value, description in self.goal_variables.items():
                found = False
                for var_name, var_value in namespace.items():
                    # Skip built-in variables
                    if var_name.startswith('__'):
                        continue
                    
                    # Check if value matches (handle both string and number comparisons)
                    if self._values_match(var_value, expected_value):
                        found = True
                        window.console.log(f"✓ Found variable '{var_name}' = {var_value} ({description})")
                        break
                
                if not found:
                    window.console.log(f"✗ No variable found with value {expected_value} ({description})")
                    return False
            
            return True
            
        except Exception as e:
            window.console.error(f"Error checking variables: {e}")
            return False
    
    def _values_match(self, actual, expected):
        """Compare two values (handles strings case-insensitively)"""
        # If both are strings, compare case-insensitively
        if isinstance(actual, str) and isinstance(expected, str):
            return actual.lower() == expected.lower()
        # Otherwise compare directly
        return actual == expected
    
    def enable_checking(self):
        self.checking_enabled = True
        window.console.log("Goal checking enabled")
    
    def disable_checking(self):
        self.checking_enabled = False
        window.console.log("Goal checking disabled")


class AceEditorManager:
    def __init__(self, editor_element=None):
        if editor_element is None:
            editor_element = window.editor
        
        self.editor = window.ace.edit(editor_element)
        self._configure_editor()
        
    def _configure_editor(self):
        self.editor.session.setMode("ace/mode/python")
        
        self.editor.setOptions({
            'enableBasicAutocompletion': True,
            'enableLiveAutocompletion': True,
        })

        self.editor.setValue("print('Hello from Ace and PyScript!')", -1)
        
    def get_code(self):
        return self.editor.getValue()
    
    def set_code(self, code):
        self.editor.setValue(code, -1)
        
    def clear(self):
        self.editor.setValue("", -1)


# Initialize components
editor_manager = AceEditorManager("editor")
goal_tracker = GoalTracker()


def run_code(event):
    """Execute code from editor in terminal"""
    code = editor_manager.get_code()
    window.console.log("Executing code in terminal:", code)
    
    # Get terminal directly from window
    try:
        terminal_obj = window.terminal
    except Exception as e:
        window.console.error(f"Cannot access terminal: {e}")
        return
    
    # Execute the code
    try:
        terminal_obj.execute_code(code)
        window.console.log("Code sent to terminal")
    except Exception as e:
        window.console.error(f"Error calling execute_code: {e}")
        return
    
    # Check goal after execution using asyncio instead of setTimeout
    async def check_goal_async():
        await asyncio.sleep(0.6)  # Wait for output
        try:
            # Get all execution output instead of just last line
            current_output = terminal_obj.get_execution_output()
            goal_tracker.check_match(code, current_output)
        except Exception as e:
            window.console.error(f"Error checking goal: {e}")
    
    asyncio.create_task(check_goal_async())


def clear_code(event):
    editor_manager.clear()
    window.console.log("Editor cleared")


def clear_terminal(event):
    try:
        window.terminal.clear()
        window.console.log("Terminal cleared")
    except Exception as e:
        window.console.error(f"Error clearing terminal: {e}")


def set_goal(code, expected_output, variables=None, must_have=None):
    """
    Function to set a new goal - call this from console or code
    
    Args:
        code: Expected code (or None to allow any code)
        expected_output: Expected output
        variables: Dict of {value: description} for flexible variable names
                  Example: {5: "a number", "hello": "a greeting"}
        must_have: List of required patterns/keywords in code
                  Example: ["for", "range"] or ["def ", "return"]
    """
    goal_tracker.set_goal(code, expected_output, variables, must_have)

# Expose functions globally
window.run_code = run_code
window.clear_code = clear_code
window.clear_terminal = clear_terminal
window.set_goal = set_goal
window.goal_tracker = goal_tracker
window.editor_manager = editor_manager

# Wait for terminal to be ready
async def wait_for_terminal():
    """Wait for terminal to initialize before showing ready message"""
    for i in range(50):  # Try for 5 seconds
        await asyncio.sleep(0.1)
        try:
            if hasattr(window, 'terminal') and window.terminal is not None:
                terminal_obj = window.terminal
                if hasattr(terminal_obj, 'execute_code'):
                    window.console.log("📝 Use: set_goal(code, output) to set a goal")
                    break
        except:
            pass
    else:
        window.console.warn("⚠️ Terminal not fully initialized. Waiting...")

asyncio.create_task(wait_for_terminal())

# Example usage (uncomment to test):
# Example 1: Simple goal with specific code
# set_goal("print('Hello World')", "Hello World")

# Example 2: Goal with flexible variable names
# set_goal(None, "10", variables={5: "a number five", 10: "result of calculation"})
# This will accept: x = 5; y = 10 OR num1 = 5; result = 10, etc.

# Example 3: Must use a for loop with range
# set_goal(None, "0\n1\n2\n3\n4", must_have=["for", "range"])
# User MUST write: for i in range(5): print(i)

# Example 4: Must use specific function
# set_goal(None, "25", must_have=["def ", "return"])
# User must define a function and return a value

# Example 5: Combine all requirements
# set_goal(None, "15", variables={15: "sum result"}, must_have=["for", "range", "+="])
# User must: use for loop with range, accumulate with +=, result in variable = 15