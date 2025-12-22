class TextHandler {
    constructor() {
        this.currentIndex = 0;
        this.isTyping = false;
        this.typewriterTimeout = null;
        this.currentText = "";
        this.textIndex = 0;
        this.data = null;
        this.texts = [];
        
        this.typingSpeed = 50;
        this.punctuationPause = 300;
        
        // Scripted sequence properties
        this.isWaitingForAction = false;
        this.currentHighlight = null;
        this.actionCallback = null;
        this.isInDelay = false;
        this.overlayElement = null;
        this.originalStyles = new Map(); // Store original styles for restoration
        
        window.textHandler = this;
    }
    
    updateDisplay() {
        const progressElem = document.getElementById("progress");
        const indicatorElem = document.querySelector(".indicator");
        
        indicatorElem.classList.add("hidden");
        
        if (this.currentIndex < this.texts.length) {
            const current = this.texts[this.currentIndex];
            
            this.currentText = current.text || "";
            this.textIndex = 0;
            this.isTyping = true;
            
            const dialog = document.querySelector("#textDialog");
            if (!this.isInDelay) {
                if (dialog && !dialog.open) {
                    dialog.showModal();
                }
                this.typeWriter();
            }
            
            progressElem.innerHTML = `Step ${this.currentIndex + 1} of ${this.texts.length}`;
            
            if (current.action) {
                this.scheduleAction(current.action);
            }
        } else {
            this.clearHighlight();
            const dialog = document.querySelector("#textDialog");
            if (dialog && dialog.open) {
                dialog.close();
            }
        }
    }
    
    typeWriter() {
        const textElem = document.getElementById("textContent");
        
        if (this.textIndex < this.currentText.length) {
            const char = this.currentText.charAt(this.textIndex);
            
            if (char === '<') {
                const closingBracket = this.currentText.indexOf('>', this.textIndex);
                if (closingBracket !== -1) {
                    textElem.innerHTML = this.currentText.substring(0, closingBracket + 1);
                    this.textIndex = closingBracket + 1;
                    this.typewriterTimeout = setTimeout(() => this.typeWriter(), 0);
                    return;
                }
            }
            
            textElem.innerHTML = this.currentText.substring(0, this.textIndex + 1);
            this.textIndex++;
            
            let delay = this.typingSpeed;
            if (char === '.' || char === '!' || char === '?') {
                delay = this.punctuationPause;
            } else if (char === ',') {
                delay = this.typingSpeed * 2;
            }
            
            this.typewriterTimeout = setTimeout(() => this.typeWriter(), delay);
        } else {
            this.isTyping = false;
            
            const current = this.texts[this.currentIndex];
            if (!current.action || current.action.type !== 'waitForButton') {
                const indicatorElem = document.querySelector(".indicator");
                indicatorElem.classList.remove("hidden");
            }
        }
    }
    
    scheduleAction(action) {
        // Available for future use
    }
    
    executeAction(action) {
        switch (action.type) {
            case 'waitForButton':
                this.waitForButton(action.selector, action.delayAfter || 0);
                break;
                
            case 'waitForInput':
                this.waitForInput(action.selector, action.expectedValue, action.delayAfter || 0);
                break;
                
            case 'delay':
                this.delayNext(action.duration || 1000);
                break;
                
            case 'autoNext':
                this.autoNext(action.duration || 1000);
                break;
                
            case 'highlight':
                this.justHighlight(action.selector, action.duration || 0);
                break;
        }
    }
    
    createOverlay() {
        if (this.overlayElement) {
            return this.overlayElement;
        }
        
        const overlay = document.createElement('div');
        overlay.className = 'tutorial-overlay';
        document.body.appendChild(overlay);
        this.overlayElement = overlay;
        
        return overlay;
    }
    
    removeOverlay() {
        if (this.overlayElement) {
            this.overlayElement.remove();
            this.overlayElement = null;
        }
    }
    
    highlightElement(element) {
        if (!element) return;
        
        // Store original styles
        this.originalStyles.set(element, {
            position: element.style.position,
            zIndex: element.style.zIndex
        });
        
        // Create overlay
        this.createOverlay();
        
        // Add highlight class
        element.classList.add('tutorial-highlight');
        this.currentHighlight = element;
        
        console.log(`Highlighted element: ${element.tagName}#${element.id || ''}.${element.className}`);
    }
    
    clearHighlight() {
        // Remove highlight from current element
        if (this.currentHighlight) {
            this.currentHighlight.classList.remove('tutorial-highlight');
            
            // Restore original styles
            const original = this.originalStyles.get(this.currentHighlight);
            if (original) {
                this.currentHighlight.style.position = original.position;
                this.currentHighlight.style.zIndex = original.zIndex;
                this.originalStyles.delete(this.currentHighlight);
            }
            
            this.currentHighlight = null;
        }
        
        // Remove overlay
        this.removeOverlay();
        
        // Remove event listeners
        if (this.actionCallback) {
            this.actionCallback.cleanup?.();
            this.actionCallback = null;
        }
    }
    
    waitForButton(selector, delayAfter = 0) {
        this.isWaitingForAction = true;
        
        const element = document.querySelector(selector);
        if (!element) {
            console.error(`Button not found: ${selector}`);
            console.log('Available elements:', document.querySelectorAll('button, [id]'));
            return;
        }
        
        console.log(`Waiting for button click: ${selector}`, element);
        
        // Highlight the element
        this.highlightElement(element);
        
        // Close the dialog to allow interaction with the button
        const dialog = document.querySelector("#textDialog");
        const wasOpen = dialog && dialog.open;
        if (dialog && wasOpen) {
            dialog.close();
        }
        
        // Store original onclick to restore later
        const originalOnClick = element.onclick;
        
        const clickHandler = (event) => {
            console.log(`Tutorial: Button clicked: ${selector}, delay: ${delayAfter}ms`);
            
            event.stopImmediatePropagation();
            event.preventDefault();
            
            element.removeEventListener('click', clickHandler, true);
            element.onclick = null;
            
            this.clearHighlight();
            
            if (delayAfter > 0) {
                console.log(`Tutorial: Waiting ${delayAfter}ms before showing next text...`);
                this.isInDelay = true;
                this.isWaitingForAction = false;
                
                if (dialog && dialog.open) {
                    dialog.close();
                }
                
                setTimeout(() => {
                    console.log('Tutorial: Delay finished, showing next text');
                    this.isInDelay = false;
                    element.onclick = originalOnClick;
                    this.currentIndex++;
                    this.updateDisplay();
                }, delayAfter);
            } else {
                this.isWaitingForAction = false;
                element.onclick = originalOnClick;
                this.currentIndex++;
                this.updateDisplay();
            }
        };
        
        element.addEventListener('click', clickHandler, true);
        
        this.actionCallback = {
            cleanup: () => {
                element.removeEventListener('click', clickHandler, true);
                element.onclick = originalOnClick;
                this.isInDelay = false;
                if (dialog && wasOpen && !dialog.open) {
                    this.isWaitingForAction = false;
                    dialog.showModal();
                }
            }
        };
        
        const indicatorElem = document.querySelector(".indicator");
        indicatorElem.classList.add("hidden");
    }
    
    waitForInput(selector, expectedValue, delayAfter = 0) {
        this.isWaitingForAction = true;
        
        const element = document.querySelector(selector);
        if (!element) {
            console.error(`Input element not found: ${selector}`);
            return;
        }
        
        // Highlight the input element
        this.highlightElement(element);
        
        const checkInput = () => {
            const value = element.value.trim();
            
            if (this.matchesExpected(value, expectedValue)) {
                element.removeEventListener('input', checkInput);
                this.clearHighlight();
                
                setTimeout(() => {
                    this.isWaitingForAction = false;
                    this.currentIndex++;
                    this.updateDisplay();
                }, delayAfter);
            }
        };
        
        element.addEventListener('input', checkInput);
        
        this.actionCallback = {
            cleanup: () => {
                element.removeEventListener('input', checkInput);
            }
        };
        
        const indicatorElem = document.querySelector(".indicator");
        indicatorElem.classList.add("hidden");
    }
    
    matchesExpected(value, expected) {
        if (typeof expected === 'string') {
            return value.toLowerCase().includes(expected.toLowerCase());
        } else if (expected instanceof RegExp) {
            return expected.test(value);
        } else if (typeof expected === 'function') {
            return expected(value);
        }
        return value === expected;
    }
    
    delayNext(duration) {
        this.isWaitingForAction = true;
        
        const indicatorElem = document.querySelector(".indicator");
        indicatorElem.classList.add("hidden");
        
        setTimeout(() => {
            this.isWaitingForAction = false;
            this.currentIndex++;
            this.updateDisplay();
        }, duration);
    }
    
    autoNext(duration) {
        setTimeout(() => {
            if (!this.isWaitingForAction && !this.isTyping) {
                this.currentIndex++;
                this.updateDisplay();
            }
        }, duration);
    }
    
    justHighlight(selector, duration = 0) {
        // Just highlight an element without requiring interaction
        const element = document.querySelector(selector);
        if (!element) {
            console.error(`Element not found for highlighting: ${selector}`);
            return;
        }
        
        console.log(`Highlighting element: ${selector}`);
        
        // Highlight the element
        this.highlightElement(element);
        
        // If duration is specified, auto-clear highlight and proceed to next
        if (duration > 0) {
            this.isWaitingForAction = true;
            setTimeout(() => {
                this.clearHighlight();
                this.isWaitingForAction = false;
                this.currentIndex++;
                this.updateDisplay();
            }, duration);
        }
        // If duration is 0, highlight stays until user clicks to next text
    }
    
    completeTyping() {
        if (this.typewriterTimeout) {
            clearTimeout(this.typewriterTimeout);
            this.typewriterTimeout = null;
        }
        
        const textElem = document.getElementById("textContent");
        textElem.innerHTML = this.currentText;
        this.isTyping = false;
        
        if (this.currentIndex < this.texts.length) {
            const current = this.texts[this.currentIndex];
            
            if (!current.action || current.action.type !== 'waitForButton') {
                const indicatorElem = document.querySelector(".indicator");
                indicatorElem.classList.remove("hidden");
            }
        } else {
            const indicatorElem = document.querySelector(".indicator");
            indicatorElem.classList.remove("hidden");
        }
    }
    
    nextText() {
        if (this.isWaitingForAction) {
            console.log("Waiting for required action...");
            return;
        }
        
        if (this.isTyping) {
            this.completeTyping();
        } else {
            const current = this.texts[this.currentIndex];
            if (current && current.action) {
                const actions = Array.isArray(current.action) ? current.action : [current.action];
                this.executeActions(actions);
            } else {
                this.clearHighlight();
                this.currentIndex++;
                this.updateDisplay();
            }
        }
    }
    
    executeActions(actions) {
        actions.forEach(action => {
            this.executeAction(action);
        });
    }
    
    loadSequence(dialogueKey) {
        this.completeTyping();
        this.clearHighlight();
        
        this.texts = this.data[dialogueKey] || [];
        this.currentIndex = 0;
        this.isWaitingForAction = false;
        
        console.log(`Loading sequence: ${dialogueKey}`);
        console.log(`Found ${this.texts.length} text entries`);
        console.log('First entry:', this.texts[0]);
        
        this.updateDisplay();
    }
    
    async loadFromFile(filename) {
        try {
            const response = await fetch(filename);
            this.data = await response.json();
            return true;
        } catch (error) {
            console.error("Error loading JSON:", error);
            return false;
        }
    }
    
    setTypingSpeed(speed) {
        this.typingSpeed = speed;
    }
    
    setPunctuationPause(pause) {
        this.punctuationPause = pause;
    }
}

window.TextHandler = TextHandler;