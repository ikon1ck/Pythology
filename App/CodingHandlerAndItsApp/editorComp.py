from js import ace
from pyscript import window, document
import sys

terminal = window.terminal

class AceEditorManager:
    def __init__(self, editor_element=None):
        if editor_element is None:
            editor_element = window.editor
        
        self.editor = window.ace.edit(editor_element)
        self._configure_editor()
        
    def _configure_editor(self):
        self.editor.session.setMode("ace/mode/python")
        
        self.editor.setOptions({
            "fontSize": "14px",
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


editor_manager = AceEditorManager("editor")


def run_code(event):
    code = editor_manager.get_code() # получаем код
    
    if not code.strip(): # если в редакторе нет кода
        return
    
    terminal.execute_code(code) # отправляем код


def clear_code(event):
    editor_manager.clear()


def clear_terminal(event):
    terminal.clear()

window.run_code = run_code
window.clear_code = clear_code
window.clear_terminal = clear_terminal