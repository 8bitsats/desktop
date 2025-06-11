/**
 * Scrapybara Agent Integration for Solana Trading Dashboard
 * Handles UI interactions with Scrapybara API endpoints
 */

// Global state
let agentStatus = {
    active: false,
    running: false,
    lastCommand: null,
    lastResult: null
};

// Initialize scrapybara controls when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
    initScrapybaraControls();
    checkScrapybaraStatus();
});

/**
 * Initialize Scrapybara control panel UI elements
 */
function initScrapybaraControls() {
    // Check if agent control panel exists (it may be injected after DOM load)
    const setupInterval = setInterval(() => {
        const controlPanel = document.getElementById('agent-control-panel');
        if (controlPanel) {
            clearInterval(setupInterval);
            setupEventListeners();
        }
    }, 500);
}

/**
 * Set up event listeners for agent control buttons
 */
function setupEventListeners() {
    // Start button
    const startBtn = document.getElementById('agent-start-btn');
    if (startBtn) {
        startBtn.addEventListener('click', startAgent);
    }

    // Stop button
    const stopBtn = document.getElementById('agent-stop-btn');
    if (stopBtn) {
        stopBtn.addEventListener('click', stopAgent);
    }

    // Pause button
    const pauseBtn = document.getElementById('agent-pause-btn');
    if (pauseBtn) {
        pauseBtn.addEventListener('click', togglePauseAgent);
    }

    // Command form
    const commandForm = document.getElementById('agent-command-form');
    if (commandForm) {
        commandForm.addEventListener('submit', (e) => {
            e.preventDefault();
            sendAgentCommand();
        });
    }

    // Take screenshot button
    const screenshotBtn = document.getElementById('agent-screenshot-btn');
    if (screenshotBtn) {
        screenshotBtn.addEventListener('click', takeScreenshot);
    }
}

/**
 * Check Scrapybara instance status and update UI
 */
function checkScrapybaraStatus() {
    fetch('/api/scrapybara/status')
        .then(response => response.json())
        .then(data => {
            updateStatusDisplay(data);
            
            // Schedule periodic status checks
            setTimeout(checkScrapybaraStatus, 10000); // Check every 10 seconds
        })
        .catch(error => {
            console.error('Error checking Scrapybara status:', error);
            updateStatusDisplay({ active: false, message: 'API error' });
            
            // Retry after a delay
            setTimeout(checkScrapybaraStatus, 15000); // Retry after 15 seconds on error
        });
}

/**
 * Start Scrapybara agent
 */
function startAgent() {
    updateStatusDisplay({ active: false, message: 'Starting...' });
    
    fetch('/api/scrapybara/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            instance_type: 'browser',
            timeout_hours: 1
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Start response:', data);
        
        if (data.success) {
            updateStatusDisplay({ 
                active: true, 
                message: 'Agent started successfully',
                stream_url: data.stream_url
            });
            
            // Refresh the iframe with new stream URL if present
            if (data.stream_url) {
                const streamFrame = document.querySelector('#stream-container iframe');
                if (streamFrame) {
                    streamFrame.src = data.stream_url;
                }
            }
        } else {
            updateStatusDisplay({ active: false, message: data.message });
        }
    })
    .catch(error => {
        console.error('Error starting agent:', error);
        updateStatusDisplay({ active: false, message: 'Failed to start agent' });
    });
}

/**
 * Stop Scrapybara agent
 */
function stopAgent() {
    updateStatusDisplay({ active: true, message: 'Stopping...' });
    
    fetch('/api/scrapybara/stop', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        console.log('Stop response:', data);
        
        if (data.success) {
            updateStatusDisplay({ active: false, message: 'Agent stopped' });
        } else {
            updateStatusDisplay({ active: false, message: data.message });
        }
    })
    .catch(error => {
        console.error('Error stopping agent:', error);
        updateStatusDisplay({ active: false, message: 'Failed to stop agent' });
    });
}

/**
 * Toggle pause/resume for the agent
 */
function togglePauseAgent() {
    const pauseBtn = document.getElementById('agent-pause-btn');
    const isPaused = pauseBtn.classList.contains('paused');
    
    // Update button state
    if (isPaused) {
        pauseBtn.textContent = 'Pause';
        pauseBtn.classList.remove('paused');
    } else {
        pauseBtn.textContent = 'Resume';
        pauseBtn.classList.add('paused');
    }
    
    // In a real implementation, we would send a pause/resume command to the agent
    updateStatusDisplay({ 
        active: true, 
        message: isPaused ? 'Agent resumed' : 'Agent paused'
    });
}

/**
 * Send a command to the Scrapybara agent
 */
function sendAgentCommand() {
    const commandInput = document.getElementById('agent-command-input');
    if (!commandInput || !commandInput.value.trim()) {
        return;
    }
    
    const command = commandInput.value.trim();
    commandInput.value = '';
    
    // Update status
    updateStatusDisplay({ active: true, message: 'Executing command...' });
    addToCommandHistory('You: ' + command);
    
    // Send command to API
    fetch('/api/scrapybara/agent', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            prompt: command,
            tools: ['computer', 'browser']
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Command response:', data);
        
        if (data.success) {
            // Store the result in state
            agentStatus.lastCommand = command;
            agentStatus.lastResult = data.result;
            
            // Add response to history
            if (data.result && data.result.response) {
                addToCommandHistory('Agent: ' + data.result.response);
            } else {
                addToCommandHistory('Agent: Command executed');
            }
            
            updateStatusDisplay({ active: true, message: 'Command completed' });
        } else {
            addToCommandHistory('Error: ' + data.message);
            updateStatusDisplay({ active: true, message: data.message });
        }
    })
    .catch(error => {
        console.error('Error sending command:', error);
        addToCommandHistory('Error: Failed to send command');
        updateStatusDisplay({ active: true, message: 'Command failed' });
    });
}

/**
 * Take a screenshot of the current browser state
 */
function takeScreenshot() {
    updateStatusDisplay({ active: true, message: 'Taking screenshot...' });
    
    fetch('/api/scrapybara/screenshot')
        .then(response => response.json())
        .then(data => {
            console.log('Screenshot response:', data);
            
            if (data.success && data.image) {
                // Show screenshot in a modal or new window
                const screenshotWindow = window.open('', '_blank');
                if (screenshotWindow) {
                    screenshotWindow.document.write(`
                        <html>
                            <head><title>Scrapybara Screenshot</title></head>
                            <body style="margin: 0; display: flex; justify-content: center; align-items: center;">
                                <img src="data:image/png;base64,${data.image}" style="max-width: 100%; max-height: 100%;">
                            </body>
                        </html>
                    `);
                }
                updateStatusDisplay({ active: true, message: 'Screenshot taken' });
            } else {
                updateStatusDisplay({ active: true, message: data.message || 'Failed to take screenshot' });
            }
        })
        .catch(error => {
            console.error('Error taking screenshot:', error);
            updateStatusDisplay({ active: true, message: 'Failed to take screenshot' });
        });
}

/**
 * Add a message to the command history display
 */
function addToCommandHistory(message) {
    const history = document.getElementById('agent-command-history');
    if (history) {
        const messageEl = document.createElement('div');
        messageEl.className = 'history-item';
        messageEl.textContent = message;
        history.appendChild(messageEl);
        
        // Scroll to bottom
        history.scrollTop = history.scrollHeight;
        
        // Limit history length
        while (history.children.length > 50) {
            history.removeChild(history.firstChild);
        }
    }
}

/**
 * Update the status display in the control panel
 */
function updateStatusDisplay(status) {
    // Update global state
    agentStatus.active = status.active;
    
    // Update status indicator
    const statusIndicator = document.getElementById('agent-status-indicator');
    if (statusIndicator) {
        statusIndicator.className = status.active ? 'status-active' : 'status-inactive';
    }
    
    // Update status message
    const statusMessage = document.getElementById('agent-status-message');
    if (statusMessage) {
        statusMessage.textContent = status.message || (status.active ? 'Active' : 'Inactive');
    }
    
    // Update button states
    const startBtn = document.getElementById('agent-start-btn');
    const stopBtn = document.getElementById('agent-stop-btn');
    const pauseBtn = document.getElementById('agent-pause-btn');
    const commandInput = document.getElementById('agent-command-input');
    const commandBtn = document.getElementById('agent-command-btn');
    const screenshotBtn = document.getElementById('agent-screenshot-btn');
    
    if (startBtn) startBtn.disabled = status.active;
    if (stopBtn) stopBtn.disabled = !status.active;
    if (pauseBtn) pauseBtn.disabled = !status.active;
    if (commandInput) commandInput.disabled = !status.active;
    if (commandBtn) commandBtn.disabled = !status.active;
    if (screenshotBtn) screenshotBtn.disabled = !status.active;
}
