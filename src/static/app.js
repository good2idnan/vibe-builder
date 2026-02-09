/**
 * VibeBuilder V2 - Professional Lovable/Replit Style
 * Optimized for high-level progress and concise reporting
 */

const API_BASE = window.location.origin;

// State
let currentCode = '';
let isBuilding = false;

// DOM Elements
const views = {
    welcome: document.getElementById('welcome-view'),
    building: document.getElementById('building-view')
};

const inputs = {
    idea: document.getElementById('idea-input'),
    refine: document.getElementById('refine-input')
};

const btns = {
    build: document.getElementById('build-btn'),
    back: document.getElementById('back-btn'),
    refine: document.getElementById('refine-btn'),
    download: document.getElementById('download-btn')
};

const display = {
    projectTitle: document.getElementById('project-title'),
    chat: document.getElementById('chat-container'),
    preview: document.getElementById('preview-frame'),
    code: document.getElementById('code-display'),
    codePanel: document.getElementById('code-panel'),
    statusPill: document.getElementById('status-pill'),
    statusText: document.getElementById('status-text')
};

// Agent Config
const agents = {
    'Researcher': { icon: '🔍', name: 'Researcher' },
    'Architect': { icon: '📐', name: 'Architect' },
    'Coder': { icon: '💻', name: 'Engineer' },
    'Tester': { icon: '🧪', name: 'Quality' },
    'Debugger': { icon: '🔧', name: 'Debugger' },
    'System': { icon: '✨', name: 'VibeAI' }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Event Listeners
    if(btns.build) btns.build.addEventListener('click', startBuild);
    if(btns.back) btns.back.addEventListener('click', goBack);
    if(btns.refine) btns.refine.addEventListener('click', applyRefine);
    if(btns.download) btns.download.addEventListener('click', downloadCode);

    // Inputs (Ctrl/Cmd + Enter for build, Enter for refine)
    if(inputs.idea) {
        inputs.idea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                startBuild();
            }
        });
    }
    
    if(inputs.refine) {
        inputs.refine.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                applyRefine();
            }
        });
    }

    // Chips
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            if(inputs.idea) {
                inputs.idea.value = chip.dataset.idea;
                startBuild();
            }
        });
    });

    // View Tabs
    document.querySelectorAll('.view-tab').forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab));
    });
});

// Build Process
async function startBuild() {
    const idea = inputs.idea ? inputs.idea.value.trim() : '';
    if (!idea || isBuilding) return;

    console.log('🚀 Starting build:', idea);
    switchView('building');
    resetState();
    isBuilding = true;
    
    if(display.projectTitle) {
        display.projectTitle.textContent = idea.substring(0, 35) + (idea.length > 35 ? '...' : '');
    }

    // Initial Status
    updateStatus('Initializing project...', true);

    try {
        const response = await fetch(`${API_BASE}/api/build`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ idea })
        });

        if (!response.ok) throw new Error(`Server connection failed`);
        await readStream(response);
    } catch (error) {
        addMessage('System', `Connection error: ${error.message}`, 'error');
        updateStatus('', false);
    }

    isBuilding = false;
    updateStatus('', false);
}

// Stream Reader (Shared)
async function readStream(response) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // Keep partial line in buffer

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                try {
                    const data = JSON.parse(line.slice(6));
                    handleUpdate(data);
                } catch (e) { console.warn('Stream parse warning'); }
            }
        }
    }
}

// Update Handler
function handleUpdate(data) {
    if (data.error) {
        addMessage('System', data.error, 'error');
        return;
    }

    const { step, phase, status, message, data: payload } = data;
    
    // Phase mapping to Agents
    let agentName = 'System';
    if (step === 1) agentName = 'Researcher';
    else if (step === 2) agentName = 'Architect';
    else if (step === 3) agentName = 'Coder';
    else if (step === 4) agentName = 'Tester';
    else if (step === 6) agentName = 'Debugger';
    else if (step === 7) agentName = 'Debugger'; // Refinement handled by Debugger/Coder team

    // LLM Chat Mode (Step 0)
    if (phase === 'chat') {
        addMessage('System', message, 'complete');
        return;
    }

    // Progress updates to Status Pill
    if (status === 'starting' && message) {
        updateStatus(message, true);
    }

    // Message rendering (Filter out noise, show high-level successes)
    if (message && (status === 'complete' || status === 'passed' || status === 'failed' || (status === 'starting' && step > 0))) {
        const msgType = (status === 'complete' || status === 'passed') ? 'success' : 
                        (status === 'failed') ? 'error' : 'working';
        
        // Don't repeat starting messages in chat if they are already in status pill, 
        // unless they have rich payload. Actually, per user request, keep it professional.
        if (status !== 'starting' || payload) {
            addMessage(agentName, message, msgType, payload);
        }
    }

    // Code Updates & Preview
    if (payload?.code || payload?.fixed_code || payload?.refined_code || data.final_code) {
        const newCode = payload?.code || payload?.fixed_code || payload?.refined_code || data.final_code;
        updatePreview(newCode);
        if (data.final_code && btns.download) btns.download.style.display = 'flex';
    }
}

// UI Helpers
async function typeWriter(el, text, speed = 10) {
    if (!el || !text) return;
    el.innerHTML = '';
    el.classList.add('typing');
    
    // Support basic bold/br formatting in typewriter
    const formatted = formatText(text);
    const temp = document.createElement('div');
    temp.innerHTML = formatted;
    const nodes = Array.from(temp.childNodes);
    
    for (const node of nodes) {
        if (node.nodeType === Node.TEXT_NODE) {
            for (const char of node.textContent) {
                el.innerHTML += char;
                await new Promise(r => setTimeout(r, speed));
            }
        } else {
            // Instant append for HTML tags like <b> or <br>
            el.appendChild(node.cloneNode(true));
        }
    }
    el.classList.remove('typing');
}

async function addMessage(agent, text, type, data = null) {
    if(!display.chat) return;

    const config = agents[agent] || agents['System'];
    const id = `msg-${Date.now()}`;
    
    const div = document.createElement('div');
    div.className = `msg-group ${type}`;
    div.id = id;
    
    let detailsHtml = '';
    if (data) {
        if (data.thinking) {
            detailsHtml += `
                <div class="msg-detail-block">
                    <span class="detail-tag">Insight</span>
                    <span class="detail-content insight-text"></span>
                </div>`;
        }
        if (data.findings || (data.components && data.components.length > 0)) {
            const items = data.components || [];
            detailsHtml += `
                <div class="msg-detail-block">
                    <span class="detail-tag">Details</span>
                    <div class="pill-group">
                        ${items.map(i => `<span class="mini-pill">${i}</span>`).join('')}
                    </div>
                </div>`;
        }
        if (data.features && data.features.length > 0) {
            detailsHtml += `
                <div class="msg-detail-block">
                    <div class="pill-group">
                        ${data.features.map(f => `<span class="mini-pill success">${f}</span>`).join('')}
                    </div>
                </div>`;
        }
    }

    div.innerHTML = `
        <div class="msg-header">
            <span class="agent-icon">${config.icon}</span>
            <span class="agent-name">${config.name}</span>
        </div>
        <div class="msg-body main-text"></div>
        ${detailsHtml}
    `;
    
    display.chat.appendChild(div);
    display.chat.scrollTop = display.chat.scrollHeight;

    // Start typing animations
    const mainTextEl = div.querySelector('.main-text');
    const insightTextEl = div.querySelector('.insight-text');

    if (mainTextEl) await typeWriter(mainTextEl, text, 8);
    if (insightTextEl && data.thinking) await typeWriter(insightTextEl, data.thinking, 5);
}

function updateStatus(text, show) {
    if (!display.statusPill) return;
    display.statusPill.style.display = show ? 'flex' : 'none';
    if (text && display.statusText) display.statusText.textContent = text;
}

function updatePreview(code) {
    if (!code || code === currentCode) return;
    currentCode = code;

    if (display.preview) {
        display.preview.style.display = 'block';
        const doc = display.preview.contentWindow.document;
        doc.open();
        doc.write(code);
        doc.close();
    }
    if (display.code) display.code.textContent = code;
}

// Navigation / Views
function switchView(name) {
    Object.values(views).forEach(v => v?.classList.remove('active'));
    if (views[name]) views[name].classList.add('active');
}

function resetState() {
    currentCode = '';
    if (display.chat) display.chat.innerHTML = '';
    if (display.preview) {
        const doc = display.preview.contentWindow.document;
        doc.open(); doc.write(''); doc.close();
    }
    updateStatus('', false);
    if(btns.download) btns.download.style.display = 'none';
}

function goBack() {
    if (isBuilding && !confirm('Discard current build?')) return;
    switchView('welcome');
    resetState();
}

// Refinement
async function applyRefine() {
    const feedback = inputs.refine ? inputs.refine.value.trim() : '';
    if (!feedback || !currentCode || isBuilding) return;

    if(inputs.refine) inputs.refine.value = '';
    updateStatus('Acknowledging request...', true);

    try {
        const response = await fetch(`${API_BASE}/api/refine`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: currentCode, feedback })
        });
        await readStream(response);
    } catch (e) {
        addMessage('System', 'Failed to update code', 'error');
    } finally {
        updateStatus('', false);
    }
}

// Tabs
function switchTab(el) {
    if (!el) return;
    document.querySelectorAll('.view-tab').forEach(t => t.classList.remove('active'));
    el.classList.add('active');

    const isCode = el.dataset.tab === 'code';
    if (display.codePanel) display.codePanel.classList.toggle('visible', isCode);
    if (display.preview) display.preview.style.display = isCode ? 'none' : 'block';
}

function downloadCode() {
    if (!currentCode) return;
    const blob = new Blob([currentCode], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'vibe-app.html';
    a.click();
}

function formatText(t) {
    if (!t) return '';
    return t.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
}
