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
            this.typeWriter();
            
            progressElem.innerHTML = `Step ${this.currentIndex + 1} of ${this.texts.length}`;
        } else {
            // Reached the end - close dialog
            const dialog = document.querySelector("#textDialog");
            if (dialog) {
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
            const indicatorElem = document.querySelector(".indicator");
            indicatorElem.classList.remove("hidden");
        }
    }
    
    completeTyping() {
        if (this.typewriterTimeout) {
            clearTimeout(this.typewriterTimeout);
            this.typewriterTimeout = null;
        }
        
        const textElem = document.getElementById("textContent");
        textElem.innerHTML = this.currentText;
        this.isTyping = false;
        
        const indicatorElem = document.querySelector(".indicator");
        indicatorElem.classList.remove("hidden");
    }
    
    nextText() {
        if (this.isTyping) {
            this.completeTyping();
        } else {
            this.currentIndex++;
            this.updateDisplay();
        }
    }
    
    loadSequence(dialogueKey) {
        this.completeTyping();
        
        this.texts = this.data[dialogueKey] || [];
        this.currentIndex = 0;
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

// REMOVE THESE LINES - they're outside the class and will run immediately
// const handler = new TextHandler("tutorial");
// document.getElementById("textBox").addEventListener("click", () => {
//     handler.nextText();
// });