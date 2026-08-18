const input = document.getElementById('message-input');
const button = document.getElementById('analyze-btn');
const status = document.getElementById('status');
const result = document.getElementById('result');
const riskBadge = document.getElementById('risk-badge');
const scoreValue = document.getElementById('score-value');
const indicatorList = document.getElementById('indicator-list');
const xaiList = document.getElementById('xai-list');
const attackType = document.getElementById('attack-type');
const knowledgeText = document.getElementById('knowledge-text');
const recommendation = document.getElementById('recommendation');

async function analyze() {
  const text = input.value.trim();
  if (!text) {
    status.textContent = 'Paste a message or URL to analyze.';
    return;
  }

  status.textContent = 'Analyzing...';
  button.disabled = true;
  result.classList.add('hidden');

  try {
    const payload = { text, url: '' };
    const data = await analyzeRequest(payload);

    renderResult(data);
    status.textContent = 'Analysis complete.';
  } catch (error) {
    status.textContent = 'Backend unavailable. Please start the FastAPI server.';
  } finally {
    button.disabled = false;
  }
}

function renderResult(data) {
  result.classList.remove('hidden');
  const score = Number(data.risk_score || 0);
  const severity = (data.severity || 'LOW').toUpperCase();
  riskBadge.textContent = severity === 'LOW' ? 'Low Risk' : severity === 'MEDIUM' ? 'Suspicious — Verify' : severity === 'HIGH' ? 'High Risk' : 'Likely Phishing';
  riskBadge.style.background = severity === 'LOW' ? '#184f3b' : severity === 'MEDIUM' ? '#6b4b00' : severity === 'HIGH' ? '#6d2a2a' : '#4f1d2c';
  scoreValue.textContent = score;

  indicatorList.innerHTML = '';
  (data.indicators || []).forEach((indicator) => {
    const item = document.createElement('li');
    item.textContent = `🔴 ${indicator}`;
    indicatorList.appendChild(item);
  });

  if (!data.indicators || data.indicators.length === 0) {
    const item = document.createElement('li');
    item.textContent = 'No significant phishing indicators detected.';
    indicatorList.appendChild(item);
  }

  xaiList.innerHTML = '';
  (data.xai || []).forEach((feature) => {
    const row = document.createElement('div');
    row.className = 'xai-item';
    row.innerHTML = `
      <div class="xai-label-row">
        <span>${feature.feature}</span>
        <span>${feature.impact}</span>
      </div>
      <div class="bar"><span class="bar-fill" style="width: ${Math.max(10, feature.impact * 100)}%"></span></div>
    `;
    xaiList.appendChild(row);
  });

  if (!data.xai || data.xai.length === 0) {
    const row = document.createElement('div');
    row.className = 'card-value';
    row.textContent = 'No strong model features identified.';
    xaiList.appendChild(row);
  }

  attackType.textContent = data.attack_type || 'General Phishing';

  const knowledgeItems = data.knowledge && data.knowledge.results ? data.knowledge.results : [];
  if (knowledgeItems.length > 0) {
    knowledgeText.innerHTML = knowledgeItems.map((item) => `<strong>${item.title}</strong><br>${item.content.substring(0, 220)}...`).join('<br><br>');
  } else {
    knowledgeText.textContent = 'No additional local cybersecurity context available.';
  }

  recommendation.textContent = data.recommendation || 'Verify using official channels.';
}

button.addEventListener('click', analyze);

document.querySelectorAll('.feedback-btn').forEach((buttonEl) => {
  buttonEl.addEventListener('click', () => {
    status.textContent = `Feedback recorded: ${buttonEl.dataset.feedback}`;
  });
});
