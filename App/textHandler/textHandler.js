class TextHandler {
    constructor(dialogueKey = "tutorial") {
        this.currentIndex = 0;
        this.isTyping = false;
        this.typewriterTimeout = null;
        this.currentText = "";
        this.textIndex = 0;
        
        // Typewriter settings
        this.typingSpeed = 50; // milliseconds per character
        this.punctuationPause = 300; // pause after punctuation
        
        // Load JSON data
        const jsonElement = document.getElementById("dialogueData");
        this.data = JSON.parse(jsonElement.textContent);
        
        // Select dialogue sequence
        this.texts = this.data[dialogueKey] || [];
        
        // Make this globally accessible for PyScript
        window.textHandler = this;
        
        this.updateDisplay();
    }
    
    updateDisplay() {
        const progressElem = document.getElementById("progress");
        
        if (this.currentIndex < this.texts.length) {
            const current = this.texts[this.currentIndex];
            
            // Start typewriter effect for text
            this.currentText = current.text || "";
            this.textIndex = 0;
            this.isTyping = true;
            this.typeWriter();
            
            // Update progress
            progressElem.innerHTML = `Step ${this.currentIndex + 1} of ${this.texts.length}`;
        } else {
            this.currentText = "🎉 Tutorial complete! You're ready to start coding!";
            this.textIndex = 0;
            this.isTyping = true;
            this.typeWriter();
            progressElem.innerHTML = "All done!";
        }
    }
    
    typeWriter() {
        const textElem = document.getElementById("textContent");
        
        if (this.textIndex < this.currentText.length) {
            // Get current character
            const char = this.currentText.charAt(this.textIndex);
            
            // Handle HTML tags - add entire tag at once
            if (char === '<') {
                const closingBracket = this.currentText.indexOf('>', this.textIndex);
                if (closingBracket !== -1) {
                    textElem.innerHTML = this.currentText.substring(0, closingBracket + 1);
                    this.textIndex = closingBracket + 1;
                    this.typewriterTimeout = setTimeout(() => this.typeWriter(), 0);
                    return;
                }
            }
            
            // Add character
            textElem.innerHTML = this.currentText.substring(0, this.textIndex + 1);
            this.textIndex++;
            
            // Check for punctuation and add pause
            let delay = this.typingSpeed;
            if (char === '.' || char === '!' || char === '?') {
                delay = this.punctuationPause;
            } else if (char === ',') {
                delay = this.typingSpeed * 2;
            }
            
            this.typewriterTimeout = setTimeout(() => this.typeWriter(), delay);
        } else {
            // Typing complete
            this.isTyping = false;
        }
    }
    
    completeTyping() {
        // Stop current typing
        if (this.typewriterTimeout) {
            clearTimeout(this.typewriterTimeout);
            this.typewriterTimeout = null;
        }
        
        // Show full text immediately
        const textElem = document.getElementById("textContent");
        textElem.innerHTML = this.currentText;
        this.isTyping = false;
    }
    
    nextText() {
        // If currently typing, complete it first
        if (this.isTyping) {
            this.completeTyping();
        } else {
            // Move to next text
            this.currentIndex++;
            this.updateDisplay();
        }
    }
    
    loadSequence(dialogueKey) {
        // Stop any ongoing typing
        this.completeTyping();
        
        this.texts = this.data[dialogueKey] || [];
        this.currentIndex = 0;
        this.updateDisplay();
    }
    
    // Load from external JSON file
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
    
    // Control typewriter speed
    setTypingSpeed(speed) {
        this.typingSpeed = speed;
    }
    
    setPunctuationPause(pause) {
        this.punctuationPause = pause;
    }
}

// Initialize
const handler = new TextHandler("tutorial");

// Click event
document.getElementById("textBox").addEventListener("click", () => {
    handler.nextText();
});