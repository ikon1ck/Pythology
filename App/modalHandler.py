from pyscript import window, document
from pyodide.ffi import create_proxy

modal = document.querySelector("#lvl-Selector")
wrapper = document.querySelector("#wrapper")

def open_modal(e=None): modal.showModal()

def close_modal(e):
    if not wrapper.contains(e.target): modal.close()


closer = create_proxy(close_modal)
opener = create_proxy(open_modal)

window.open_modal = opener
modal.addEventListener("click", closer)