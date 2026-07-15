/* ============================================
   SpamShield AI — Vanilla ES6 SPA Logic
   Version: 1.0.0
   ============================================ */

// ============================================
// Constants & State
// ============================================
const API_URL = window.location.port === '5000' ? '' : 'http://127.0.0.1:5000';

const EXAMPLE_MESSAGES = [
    'Congratulations! You\'ve won a $1,000,000 prize! Click here to claim now: http://claim-prize.com',
    'Hey, are we still meeting for lunch tomorrow at 12?',
    'URGENT: Your bank account has been compromised. Verify your identity immediately at http://secure-bank-verify.com',
    'Hi Mom, I\'ll be home by 6pm. Do you need anything from the store?',
    'FREE entry to win an iPhone 15! Text WIN to 80085. T&Cs apply. Reply STOP to opt out.',
    'Your Amazon package #38291 is delayed. Update delivery preferences: http://amzn-delivery.xyz',
    'Meeting rescheduled to 3 PM. Please update your calendar.',
    'You have been selected for a $5000 government stimulus. Claim now with your SSN at gov-relief.net',
    'Can you pick up milk and bread on your way home?',
    'BITCOIN INVESTMENT: Get 500% returns guaranteed! Join our crypto group now!'
];

const THREAT_ICONS = {
    lottery_scam: '🎰',
    banking_fraud: '🏦',
    otp_fraud: '🔑',
    crypto_scam: '₿',
    investment_scam: '📈',
    job_scam: '💼',
    delivery_scam: '📦',
    govt_impersonation: '🏛️',
    tech_support_scam: '💻',
    gmail_phishing: '📧',
    default: '🚨'
};

const NLP_STAT_ICONS = {
    characters: '🔤',
    words: '📝',
    sentences: '📄',
    urls_found: '🔗',
    emails_found: '📧',
    phones_found: '📞',
    currency_symbols: '💰',
    stopwords_removed: '🚫',
    tokens_count: '🧩',
    lemmas_count: '🌿',
    avg_word_length: '📏',
    uppercase_ratio: '🔠'
};

const TEXT_STAT_ICONS = {
    char_count: '🔤',
    word_count: '📝',
    sentence_count: '📄',
    avg_word_length: '📏',
    uppercase_ratio: '🔠',
    special_char_ratio: '✳️'
};

let analysisHistory = JSON.parse(localStorage.getItem('spamHistory') || '[]');
let currentTheme = localStorage.getItem('theme') || 'light';

// ============================================
// Theme Management
// ============================================
function initTheme() {
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeIcon();
}

function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    localStorage.setItem('theme', currentTheme);
    updateThemeIcon();
}

function updateThemeIcon() {
    const icon = document.querySelector('.theme-icon');
    if (icon) {
        icon.textContent = currentTheme === 'light' ? '🌙' : '☀️';
    }
}

// ============================================
// Character Counter
// ============================================
function updateCharCount() {
    const input = document.getElementById('message-input');
    const counter = document.getElementById('char-count');
    const counterWrapper = input.closest('.textarea-wrapper').querySelector('.char-counter');
    const len = input.value.length;
    counter.textContent = len.toLocaleString();

    counterWrapper.classList.remove('warning', 'danger');
    if (len > 9000) {
        counterWrapper.classList.add('danger');
    } else if (len > 7500) {
        counterWrapper.classList.add('warning');
    }
}

// ============================================
// Analyzer Functions
// ============================================
async function analyzeMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();

    if (!message) {
        showToast('Please enter a message to analyze', 'warning');
        input.focus();
        return;
    }

    showLoading();
    const analyzeBtn = document.getElementById('analyze-btn');
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnSpinner = analyzeBtn.querySelector('.btn-spinner');
    btnText.textContent = 'Analyzing...';
    btnSpinner.classList.remove('hidden');
    analyzeBtn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        displayResults(data);
        addToHistory(message, data);
        showToast('Analysis complete!', 'success');
    } catch (error) {
        console.error('Analysis error:', error);
        showToast(`Analysis failed: ${error.message}`, 'error');
    } finally {
        hideLoading();
        btnText.textContent = 'Analyze';
        btnSpinner.classList.add('hidden');
        analyzeBtn.disabled = false;
    }
}

function displayResults(data) {
    const resultsSection = document.getElementById('results');
    resultsSection.classList.remove('hidden');

    // Prediction badge
    const badge = document.getElementById('prediction-badge');
    const isSpam = data.prediction === 'Spam';
    badge.className = `prediction-badge ${isSpam ? 'spam' : 'ham'}`;
    badge.innerHTML = `<span>${isSpam ? '⚠️' : '🛡️'}</span> ${data.prediction}`;
    const label = document.getElementById('prediction-label');
    if (label) {
        label.textContent = isSpam
            ? 'This message appears to be spam'
            : 'This message appears to be safe';
    }

    // PDF Threat Report Card (Only for Spam)
    const reportCard = document.getElementById('spam-report-card');
    if (reportCard) {
        if (isSpam) {
            reportCard.classList.remove('hidden');
            
            // Scan ID
            const scanId = 'SCAN-' + Math.floor(Math.random() * 90000 + 10000);
            const reportScanId = document.getElementById('report-scan-id');
            if (reportScanId) reportScanId.textContent = scanId;
            
            // Severity
            const reportSeverity = document.getElementById('report-severity');
            if (reportSeverity) {
                reportSeverity.textContent = data.risk_level.toUpperCase();
                reportSeverity.style.color = data.risk_color;
            }
            
            // Confidence
            const reportConf = document.getElementById('report-confidence');
            if (reportConf) reportConf.textContent = data.confidence.toFixed(1) + '%';
            
            // Threat Pattern
            const patternStr = data.detected_threats && data.detected_threats.length > 0
                ? data.detected_threats.map(formatThreatName).join(', ')
                : 'Unspecified Spam';
            const reportPattern = document.getElementById('report-pattern');
            if (reportPattern) reportPattern.textContent = patternStr;
            
            // Words
            const reportWords = document.getElementById('report-words');
            if (reportWords) reportWords.textContent = data.nlp_stats ? data.nlp_stats.words : 0;
            
            // Tokens
            const reportTokens = document.getElementById('report-tokens');
            if (reportTokens) reportTokens.textContent = data.highlighted_words ? data.highlighted_words.length : 0;
            
            // Risk Level
            const reportRisk = document.getElementById('report-risk-level');
            if (reportRisk) {
                reportRisk.textContent = data.risk_level;
                reportRisk.style.color = data.risk_color;
            }
            
            // Message Transcript
            const originalText = document.getElementById('message-input').value;
            const reportTranscript = document.getElementById('report-transcript-text');
            if (reportTranscript) reportTranscript.textContent = originalText;
            
            // AI Security Explanation Summary
            const reportSummary = document.getElementById('report-summary-text');
            if (reportSummary) reportSummary.textContent = data.explanation;
            
            // Download Report PDF button hookup
            const downloadReportBtn = document.getElementById('download-report-pdf-btn');
            if (downloadReportBtn) {
                const newBtn = downloadReportBtn.cloneNode(true);
                downloadReportBtn.parentNode.replaceChild(newBtn, downloadReportBtn);
                newBtn.addEventListener('click', () => {
                    downloadSpamReportPdf(data, originalText);
                });
            }
        } else {
            reportCard.classList.add('hidden');
        }
    }

    const ring = document.getElementById('confidence-ring');
    const circumference = 2 * Math.PI * 54; // r = 54
    const offset = circumference - (data.confidence / 100) * circumference;
    ring.style.strokeDasharray = circumference;
    ring.style.strokeDashoffset = circumference;
    ring.style.stroke = isSpam ? 'var(--spam-color)' : 'var(--ham-color)';

    // Trigger animation after small delay
    requestAnimationFrame(() => {
        setTimeout(() => {
            ring.style.strokeDashoffset = offset;
        }, 100);
    });

    // Count-up confidence value
    const confValue = document.getElementById('confidence-value');
    animateCounter(confValue, data.confidence, 1500, '%');

    // Risk level
    const riskLabel = document.getElementById('risk-label');
    riskLabel.textContent = data.risk_level;
    riskLabel.style.color = data.risk_color;
    riskLabel.style.background = hexToRgba(data.risk_color, 0.12);

    // Risk bar
    const riskBar = document.getElementById('risk-bar');
    riskBar.style.width = '0%';
    riskBar.style.background = `linear-gradient(90deg, var(--ham-color), ${data.risk_color})`;
    setTimeout(() => {
        riskBar.style.width = `${data.spam_probability * 100}%`;
    }, 200);

    // Spam probability
    const spamProb = document.getElementById('spam-probability');
    animateCounter(spamProb, data.spam_probability * 100, 1200, '%');

    // Explanation
    const explanationText = document.getElementById('explanation-text');
    explanationText.textContent = data.explanation || 'No explanation available.';

    // Highlighted words
    const highlightedContainer = document.getElementById('highlighted-words');
    highlightedContainer.innerHTML = '';
    if (data.highlighted_words && data.highlighted_words.length > 0) {
        data.highlighted_words.forEach((word, i) => {
            const chip = document.createElement('span');
            chip.className = 'word-chip';
            chip.textContent = word;
            chip.style.animationDelay = `${i * 0.08}s`;
            chip.style.animation = 'fadeInUp 0.4s ease both';
            highlightedContainer.appendChild(chip);
        });
        document.getElementById('highlighted-section').classList.remove('hidden');
    } else {
        document.getElementById('highlighted-section').classList.add('hidden');
    }

    // Reasoning
    const reasoningList = document.getElementById('reasoning-list');
    reasoningList.innerHTML = '';
    if (data.reasoning && data.reasoning.length > 0) {
        data.reasoning.forEach((reason, i) => {
            const li = document.createElement('li');
            li.className = 'reasoning-item';
            li.style.animationDelay = `${i * 0.1}s`;
            li.style.animation = 'fadeInUp 0.4s ease both';
            li.innerHTML = `
                <span class="reasoning-icon">${isSpam ? '⚠️' : '✅'}</span>
                <span>${reason}</span>
            `;
            reasoningList.appendChild(li);
        });
        document.getElementById('reasoning-section').classList.remove('hidden');
    } else {
        document.getElementById('reasoning-section').classList.add('hidden');
    }

    // Detected threats
    const threatsContainer = document.getElementById('threats-container');
    threatsContainer.innerHTML = '';
    if (data.detected_threats && data.detected_threats.length > 0) {
        data.detected_threats.forEach((threat, i) => {
            const card = document.createElement('div');
            card.className = 'threat-card';
            card.style.animationDelay = `${i * 0.1}s`;
            card.style.animation = 'fadeInUp 0.4s ease both';

            const icon = THREAT_ICONS[threat] || THREAT_ICONS.default;
            const keywords = data.threat_details && data.threat_details[threat]
                ? data.threat_details[threat] : [];

            card.innerHTML = `
                <div class="threat-name">${icon} ${formatThreatName(threat)}</div>
                <div class="threat-keywords">
                    ${keywords.map(k => `<span class="threat-keyword">${k}</span>`).join('')}
                </div>
            `;
            threatsContainer.appendChild(card);
        });
        document.getElementById('threats-section').classList.remove('hidden');
    } else {
        document.getElementById('threats-section').classList.add('hidden');
    }

    // Suspicion scores
    const scoresContainer = document.getElementById('scores-container');
    scoresContainer.innerHTML = '';
    if (data.suspicion_scores) {
        Object.entries(data.suspicion_scores).forEach(([key, value], i) => {
            const row = document.createElement('div');
            row.className = 'score-row';
            const percentage = (value * 100).toFixed(0);
            const color = getScoreColor(value);

            row.innerHTML = `
                <span class="score-label">${key}</span>
                <div class="score-bar-bg">
                    <div class="score-bar-fill" style="background: ${color};" data-width="${percentage}%"></div>
                </div>
                <span class="score-value">${percentage}%</span>
            `;
            scoresContainer.appendChild(row);

            // Animate bar fill
            setTimeout(() => {
                row.querySelector('.score-bar-fill').style.width = `${percentage}%`;
            }, 300 + (i * 150));
        });
        document.getElementById('scores-section').classList.remove('hidden');
    } else {
        document.getElementById('scores-section').classList.add('hidden');
    }

    // NLP Statistics
    const nlpGrid = document.getElementById('nlp-stats-grid');
    nlpGrid.innerHTML = '';
    if (data.nlp_stats) {
        Object.entries(data.nlp_stats).forEach(([key, value], i) => {
            const card = document.createElement('div');
            card.className = 'stat-card';
            card.style.animationDelay = `${i * 0.05}s`;
            card.style.animation = 'fadeInUp 0.4s ease both';

            const icon = NLP_STAT_ICONS[key] || '📊';
            const displayValue = typeof value === 'number' && !Number.isInteger(value)
                ? value.toFixed(2) : value;

            card.innerHTML = `
                <div class="stat-card-icon">${icon}</div>
                <div class="stat-card-value">${displayValue}</div>
                <div class="stat-card-label">${formatStatLabel(key)}</div>
            `;
            nlpGrid.appendChild(card);
        });
        document.getElementById('nlp-stats-section').classList.remove('hidden');
    } else {
        document.getElementById('nlp-stats-section').classList.add('hidden');
    }

    // Text Statistics
    const textGrid = document.getElementById('text-stats-grid');
    textGrid.innerHTML = '';
    if (data.text_stats) {
        Object.entries(data.text_stats).forEach(([key, value], i) => {
            const card = document.createElement('div');
            card.className = 'stat-card';
            card.style.animationDelay = `${i * 0.05}s`;
            card.style.animation = 'fadeInUp 0.4s ease both';

            const icon = TEXT_STAT_ICONS[key] || '📊';
            const displayValue = typeof value === 'number' && !Number.isInteger(value)
                ? value.toFixed(2) : value;

            card.innerHTML = `
                <div class="stat-card-icon">${icon}</div>
                <div class="stat-card-value">${displayValue}</div>
                <div class="stat-card-label">${formatStatLabel(key)}</div>
            `;
            textGrid.appendChild(card);
        });
        document.getElementById('text-stats-section').classList.remove('hidden');
    } else {
        document.getElementById('text-stats-section').classList.add('hidden');
    }

    // Smooth scroll to results
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 200);
}

function clearAnalyzer() {
    const input = document.getElementById('message-input');
    input.value = '';
    updateCharCount();
    document.getElementById('results').classList.add('hidden');
    showToast('Analyzer cleared', 'info');
}

function loadExample() {
    const input = document.getElementById('message-input');
    const randomIndex = Math.floor(Math.random() * EXAMPLE_MESSAGES.length);
    input.value = EXAMPLE_MESSAGES[randomIndex];
    updateCharCount();
    showToast('Example message loaded', 'info');
    input.focus();
}

async function pasteFromClipboard() {
    try {
        const text = await navigator.clipboard.readText();
        if (text) {
            document.getElementById('message-input').value = text;
            updateCharCount();
            showToast('Text pasted from clipboard', 'success');
        } else {
            showToast('Clipboard is empty', 'warning');
        }
    } catch (err) {
        showToast('Unable to access clipboard. Check browser permissions.', 'error');
    }
}

// ============================================
// Count-Up Animation
// ============================================
function animateCounter(element, target, duration = 1500, suffix = '%') {
    const start = 0;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        const current = start + (target - start) * eased;
        element.textContent = current.toFixed(1) + suffix;
        if (progress < 1) requestAnimationFrame(update);
    }

    requestAnimationFrame(update);
}

// ============================================
// Helper Functions
// ============================================
function formatThreatName(name) {
    return name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function formatStatLabel(key) {
    return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function getScoreColor(value) {
    if (value >= 0.7) return 'var(--spam-color)';
    if (value >= 0.4) return 'var(--warning-color)';
    return 'var(--ham-color)';
}

function hexToRgba(hex, alpha) {
    if (!hex || !hex.startsWith('#')) return `rgba(128, 128, 128, ${alpha})`;
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function formatTimestamp(ts) {
    const date = new Date(ts);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString('en-US', {
        month: 'short', day: 'numeric', year: 'numeric'
    });
}

// ============================================
// History Management
// ============================================
function addToHistory(message, result) {
    const entry = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        message: message.substring(0, 500),
        preview: message.substring(0, 100),
        prediction: result.prediction,
        confidence: result.confidence,
        risk_level: result.risk_level,
        risk_color: result.risk_color,
        result: result
    };

    analysisHistory.unshift(entry);

    // Keep only last 100 entries
    if (analysisHistory.length > 100) {
        analysisHistory = analysisHistory.slice(0, 100);
    }

    saveHistory();
    renderHistory();
}

function renderHistory(filter = '') {
    const list = document.getElementById('history-list');
    const empty = document.getElementById('history-empty');
    list.innerHTML = '';

    const filtered = filter
        ? analysisHistory.filter(item =>
            item.message.toLowerCase().includes(filter.toLowerCase()) ||
            item.prediction.toLowerCase().includes(filter.toLowerCase()))
        : analysisHistory;

    if (filtered.length === 0) {
        empty.classList.remove('hidden');
        list.classList.add('hidden');
        return;
    }

    empty.classList.add('hidden');
    list.classList.remove('hidden');

    filtered.forEach((item, i) => {
        const card = document.createElement('div');
        const isSpam = item.prediction === 'Spam';
        card.className = `history-card ${isSpam ? 'spam-card' : 'ham-card'}`;
        card.style.animationDelay = `${i * 0.05}s`;
        card.style.animation = 'fadeInUp 0.3s ease both';

        card.innerHTML = `
            <span class="history-badge ${isSpam ? 'badge-spam' : 'badge-ham'}">
                ${isSpam ? '⚠️' : '🛡️'} ${item.prediction}
            </span>
            <div class="history-info">
                <div class="history-message">${escapeHtml(item.preview)}</div>
                <div class="history-meta">
                    <span>🕐 ${formatTimestamp(item.timestamp)}</span>
                    <span>📊 ${item.confidence.toFixed(1)}% confidence</span>
                </div>
            </div>
            <button class="history-delete" onclick="event.stopPropagation(); deleteHistoryItem(${item.id})" title="Delete">
                ✕
            </button>
        `;

        // Click to re-display results
        card.addEventListener('click', () => {
            if (item.result) {
                document.getElementById('message-input').value = item.message;
                updateCharCount();
                displayResults(item.result);
            }
        });

        list.appendChild(card);
    });
}

function deleteHistoryItem(id) {
    analysisHistory = analysisHistory.filter(item => item.id !== id);
    saveHistory();
    renderHistory(document.getElementById('history-search').value);
    showToast('Entry deleted', 'info');
}

function clearHistory() {
    if (analysisHistory.length === 0) {
        showToast('History is already empty', 'info');
        return;
    }

    if (!confirm('Are you sure you want to clear all analysis history?')) return;

    analysisHistory = [];
    saveHistory();
    renderHistory();
    showToast('History cleared', 'success');
}

function searchHistory(query) {
    renderHistory(query);
}

function saveHistory() {
    localStorage.setItem('spamHistory', JSON.stringify(analysisHistory));
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// Export Functions
// ============================================
function exportHistory(format) {
    closeExportMenu();

    if (analysisHistory.length === 0) {
        showToast('No history to export', 'warning');
        return;
    }

    switch (format) {
        case 'txt': exportAsTxt(); break;
        case 'json': exportAsJson(); break;
        case 'pdf': exportAsPdf(); break;
        default: showToast('Unknown format', 'error');
    }
}

function exportAsTxt() {
    let content = '═══════════════════════════════════════\n';
    content += '   SpamShield AI — Analysis History\n';
    content += `   Exported: ${new Date().toLocaleString()}\n`;
    content += '═══════════════════════════════════════\n\n';

    analysisHistory.forEach((item, i) => {
        content += `─── Entry #${i + 1} ───────────────────────\n`;
        content += `Prediction: ${item.prediction}\n`;
        content += `Confidence: ${item.confidence.toFixed(1)}%\n`;
        content += `Risk Level: ${item.risk_level}\n`;
        content += `Timestamp:  ${new Date(item.timestamp).toLocaleString()}\n`;
        content += `Message:    ${item.message}\n\n`;
    });

    content += `\nTotal entries: ${analysisHistory.length}\n`;
    downloadFile(content, 'spamshield-history.txt', 'text/plain');
    showToast('History exported as TXT', 'success');
}

function exportAsJson() {
    const data = {
        exported_at: new Date().toISOString(),
        total_entries: analysisHistory.length,
        history: analysisHistory
    };
    const content = JSON.stringify(data, null, 2);
    downloadFile(content, 'spamshield-history.json', 'application/json');
    showToast('History exported as JSON', 'success');
}

function exportAsPdf() {
    try {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        // Title
        doc.setFontSize(20);
        doc.setTextColor(108, 92, 231);
        doc.text('SpamShield AI — Analysis History', 20, 25);

        doc.setFontSize(10);
        doc.setTextColor(100, 100, 100);
        doc.text(`Exported: ${new Date().toLocaleString()}`, 20, 33);
        doc.text(`Total entries: ${analysisHistory.length}`, 20, 39);

        doc.setLineWidth(0.5);
        doc.setDrawColor(108, 92, 231);
        doc.line(20, 43, 190, 43);

        let y = 52;

        analysisHistory.forEach((item, i) => {
            if (y > 260) {
                doc.addPage();
                y = 20;
            }

            // Prediction color
            if (item.prediction === 'Spam') {
                doc.setTextColor(255, 23, 68);
            } else {
                doc.setTextColor(0, 200, 83);
            }
            doc.setFontSize(12);
            doc.text(`#${i + 1} — ${item.prediction}`, 20, y);

            doc.setTextColor(60, 60, 60);
            doc.setFontSize(9);
            doc.text(`Confidence: ${item.confidence.toFixed(1)}% | Risk: ${item.risk_level}`, 20, y + 6);
            doc.text(`Date: ${new Date(item.timestamp).toLocaleString()}`, 20, y + 11);

            doc.setTextColor(80, 80, 80);
            const msgLines = doc.splitTextToSize(`Message: ${item.message}`, 165);
            doc.text(msgLines, 20, y + 17);

            y += 20 + (msgLines.length * 4) + 8;

            doc.setDrawColor(200, 200, 200);
            doc.setLineWidth(0.2);
            doc.line(20, y - 4, 190, y - 4);
        });

        doc.save('spamshield-history.pdf');
        showToast('History exported as PDF', 'success');
    } catch (err) {
        console.error('PDF export error:', err);
        showToast('PDF export failed. Please try TXT or JSON.', 'error');
    }
}

function downloadSpamReportPdf(data, message) {
    try {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        const scanId = document.getElementById('report-scan-id').textContent;
        const timestamp = new Date().toLocaleString();

        // 1. Header decoration (Red threat bar)
        doc.setFillColor(255, 23, 68); // #ff1744
        doc.rect(0, 0, 210, 15, 'F');

        doc.setFontSize(10);
        doc.setTextColor(255, 255, 255);
        doc.setFont('Helvetica', 'bold');
        doc.text('SPAMSHIELD AI — CYBERSECURITY THREAT ADVISORY', 20, 10);

        // 2. Report metadata
        doc.setFontSize(22);
        doc.setTextColor(26, 26, 46);
        doc.text('Threat Analysis Certificate', 20, 32);

        doc.setFontSize(10);
        doc.setTextColor(100, 100, 100);
        doc.setFont('Helvetica', 'normal');
        doc.text(`Scan Reference: ${scanId}`, 20, 40);
        doc.text(`Generated: ${timestamp}`, 20, 46);
        doc.text(`Risk Status: ${data.risk_level.toUpperCase()} THREAT`, 20, 52);

        // 3. Grid box - Threat Assessment Summary
        doc.setDrawColor(255, 23, 68);
        doc.setLineWidth(0.8);
        doc.setFillColor(255, 240, 240);
        doc.rect(20, 60, 170, 45, 'FD');

        doc.setFontSize(12);
        doc.setTextColor(255, 23, 68);
        doc.setFont('Helvetica', 'bold');
        doc.text('THREAT ASSESSMENT SUMMARY', 25, 68);

        doc.setFontSize(10);
        doc.setTextColor(50, 50, 50);
        doc.setFont('Helvetica', 'normal');
        
        doc.text(`Classification:`, 25, 76);
        doc.setFont('Helvetica', 'bold');
        doc.text(`SPAM`, 55, 76);
        
        doc.setFont('Helvetica', 'normal');
        doc.text(`AI Confidence:`, 25, 82);
        doc.setFont('Helvetica', 'bold');
        doc.text(`${data.confidence.toFixed(1)}%`, 55, 82);

        doc.setFont('Helvetica', 'normal');
        doc.text(`Risk Level:`, 25, 88);
        doc.setFont('Helvetica', 'bold');
        // Parse hex color for jsPDF text color
        const hex = data.risk_color || '#ff1744';
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        doc.setTextColor(r, g, b);
        doc.text(`${data.risk_level}`, 55, 88);
        
        doc.setTextColor(50, 50, 50);
        doc.setFont('Helvetica', 'normal');
        doc.text(`Detected Threats:`, 25, 94);
        doc.setFont('Helvetica', 'bold');
        const threatStr = data.detected_threats && data.detected_threats.length > 0 
            ? data.detected_threats.map(formatThreatName).join(', ') 
            : 'Unspecified Spam';
        doc.text(threatStr, 60, 94);

        // Y positioning setup
        doc.setFontSize(12);
        doc.setTextColor(26, 26, 46);
        doc.setFont('Helvetica', 'bold');
        doc.text('MESSAGE TRANSCRIPT', 20, 120);
        
        doc.setDrawColor(200, 200, 200);
        doc.setLineWidth(0.2);
        doc.line(20, 123, 190, 123);

        doc.setFontSize(9);
        doc.setTextColor(80, 80, 80);
        doc.setFont('Courier', 'normal');
        const msgLines = doc.splitTextToSize(message, 165);
        doc.text(msgLines, 20, 129);

        let currentY = 129 + (msgLines.length * 4.5) + 10;

        doc.setFontSize(12);
        doc.setTextColor(26, 26, 46);
        doc.setFont('Helvetica', 'bold');
        doc.text('AI SECURITY EXPLANATION', 20, currentY);
        doc.line(20, currentY + 3, 190, currentY + 3);

        doc.setFontSize(10);
        doc.setTextColor(70, 70, 70);
        doc.setFont('Helvetica', 'normal');
        const explanationLines = doc.splitTextToSize(data.explanation || 'No detailed analysis provided.', 165);
        doc.text(explanationLines, 20, currentY + 9);

        currentY = currentY + 9 + (explanationLines.length * 5) + 10;

        if (currentY > 230) {
            doc.addPage();
            currentY = 20;
        }

        doc.setFontSize(12);
        doc.setTextColor(26, 26, 46);
        doc.setFont('Helvetica', 'bold');
        doc.text('SUSPICION METRICS', 20, currentY);
        doc.line(20, currentY + 3, 190, currentY + 3);

        doc.setFontSize(9);
        doc.setTextColor(60, 60, 60);
        let scoreY = currentY + 10;

        if (data.suspicion_scores) {
            Object.entries(data.suspicion_scores).forEach(([key, val]) => {
                doc.setFont('Helvetica', 'bold');
                doc.text(key.toUpperCase(), 20, scoreY);
                doc.setFont('Helvetica', 'normal');
                
                // Draw tiny chart bar
                doc.setDrawColor(220, 220, 220);
                doc.rect(70, scoreY - 3, 80, 4);
                doc.setFillColor(255, 23, 68);
                doc.rect(70, scoreY - 3, 80 * val, 4, 'F');
                
                doc.text(`${(val * 100).toFixed(0)}%`, 160, scoreY);
                scoreY += 7;
            });
        }

        doc.setFontSize(8);
        doc.setTextColor(150, 150, 150);
        doc.setFont('Helvetica', 'normal');
        doc.text('Report generated automatically by SpamShield AI engine.', 20, 285);
        doc.text('Confidential — For User Reference Only', 130, 285);

        doc.save(`spamshield-threat-report-${scanId}.pdf`);
        showToast('Spam Threat Report PDF downloaded!', 'success');
    } catch (err) {
        console.error('PDF report download error:', err);
        showToast('Failed to download PDF report', 'error');
    }
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// ============================================
// Export Dropdown
// ============================================
function toggleExportMenu() {
    const menu = document.getElementById('export-menu');
    menu.classList.toggle('show');
}

function closeExportMenu() {
    const menu = document.getElementById('export-menu');
    menu.classList.remove('show');
}

// ============================================
// Toast Notifications
// ============================================
function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };

    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
        <div class="toast-progress" style="animation-duration: ${duration}ms"></div>
    `;

    container.appendChild(toast);

    // Trigger slide-in
    requestAnimationFrame(() => {
        setTimeout(() => toast.classList.add('toast-show'), 10);
    });

    // Auto dismiss
    setTimeout(() => {
        toast.classList.remove('toast-show');
        setTimeout(() => {
            if (toast.parentElement) toast.remove();
        }, 350);
    }, duration);
}

// ============================================
// Loading Overlay
// ============================================
function showLoading() {
    document.getElementById('loading-overlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.add('hidden');
}

// ============================================
// Navigation
// ============================================
function toggleMobileMenu() {
    const navLinks = document.getElementById('nav-links');
    const hamburger = document.getElementById('hamburger');
    navLinks.classList.toggle('show');
    hamburger.classList.toggle('active');
}

function setupNavigation() {
    // Smooth scroll for nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            const targetEl = document.getElementById(targetId);
            if (targetEl) {
                targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
            // Close mobile menu
            document.getElementById('nav-links').classList.remove('show');
            document.getElementById('hamburger').classList.remove('active');
        });
    });

    // Active link on scroll with IntersectionObserver
    const sections = document.querySelectorAll('section[id]');
    const observerOptions = {
        root: null,
        rootMargin: '-30% 0px -70% 0px',
        threshold: 0
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.getAttribute('id');
                document.querySelectorAll('.nav-link').forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${id}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }, observerOptions);

    sections.forEach(section => observer.observe(section));

    // Navbar scroll effect
    window.addEventListener('scroll', () => {
        const navbar = document.getElementById('navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// ============================================
// Close menus on outside click
// ============================================
function setupOutsideClicks() {
    document.addEventListener('click', (e) => {
        // Close export menu
        const exportDropdown = document.querySelector('.export-dropdown');
        if (exportDropdown && !exportDropdown.contains(e.target)) {
            closeExportMenu();
        }

        // Close mobile menu on outside click
        const navbar = document.getElementById('navbar');
        const hamburger = document.getElementById('hamburger');
        if (!navbar.contains(e.target) && !hamburger.contains(e.target)) {
            document.getElementById('nav-links').classList.remove('show');
            hamburger.classList.remove('active');
        }
    });
}

// ============================================
// Keyboard Shortcuts
// ============================================
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Enter to analyze
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            analyzeMessage();
        }
        // Escape to clear
        if (e.key === 'Escape') {
            hideLoading();
            closeExportMenu();
        }
    });
}

// ============================================
// DOMContentLoaded — Initialize Application
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize theme
    initTheme();

    // Render history
    renderHistory();

    // Attach event listeners — Analyzer
    document.getElementById('analyze-btn').addEventListener('click', analyzeMessage);
    document.getElementById('clear-btn').addEventListener('click', clearAnalyzer);
    document.getElementById('example-btn').addEventListener('click', loadExample);
    document.getElementById('paste-btn').addEventListener('click', pasteFromClipboard);
    document.getElementById('message-input').addEventListener('input', updateCharCount);

    // Theme toggle
    document.getElementById('theme-toggle').addEventListener('click', toggleTheme);

    // Hamburger menu
    document.getElementById('hamburger').addEventListener('click', toggleMobileMenu);

    // History controls
    document.getElementById('clear-history-btn').addEventListener('click', clearHistory);
    document.getElementById('history-search').addEventListener('input', (e) => searchHistory(e.target.value));

    // Export controls
    document.getElementById('export-toggle').addEventListener('click', (e) => {
        e.stopPropagation();
        toggleExportMenu();
    });
    document.getElementById('export-txt').addEventListener('click', () => exportHistory('txt'));
    document.getElementById('export-json').addEventListener('click', () => exportHistory('json'));
    document.getElementById('export-pdf').addEventListener('click', () => exportHistory('pdf'));

    // Setup navigation
    setupNavigation();

    // Setup outside click handlers
    setupOutsideClicks();

    // Setup keyboard shortcuts
    setupKeyboardShortcuts();

    // Textarea auto-resize hint
    const textarea = document.getElementById('message-input');
    textarea.addEventListener('focus', () => {
        textarea.closest('.textarea-wrapper').style.boxShadow = '0 0 0 3px rgba(108, 92, 231, 0.1)';
    });
    textarea.addEventListener('blur', () => {
        textarea.closest('.textarea-wrapper').style.boxShadow = 'none';
    });
});
