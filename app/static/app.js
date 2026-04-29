/**
 * ChatDoctor Clinical Assistant — Frontend Logic
 * Vanilla JS, no dependencies.
 */

'use strict';

// ── State ─────────────────────────────────────────────────
const state = {
  token: localStorage.getItem('cd_token') || null,
  username: localStorage.getItem('cd_username') || null,
  userProfile: null,
  currentSessionId: null,
  isSending: false,
};

// ── API helpers ───────────────────────────────────────────
const API = {
  async request(path, options = {}) {
    const headers = { 'Content-Type': 'application/json', ...options.headers };
    if (state.token) headers['Authorization'] = `Bearer ${state.token}`;
    const res = await fetch(path, { ...options, headers });
    if (res.status === 429) { showToast('Rate limit reached. Please wait.', 'error'); throw new Error('rate_limit'); }
    if (res.status === 401) { logout(); throw new Error('unauthorized'); }
    return res;
  },

  async post(path, body) {
    return this.request(path, { method: 'POST', body: JSON.stringify(body) });
  },

  async get(path) {
    return this.request(path);
  },

  async del(path) {
    return this.request(path, { method: 'DELETE' });
  },
};

// ── Auth ──────────────────────────────────────────────────
function switchTab(tab) {
  document.getElementById('tab-login').classList.toggle('active', tab === 'login');
  document.getElementById('tab-register').classList.toggle('active', tab === 'register');
  document.getElementById('login-form').style.display = tab === 'login' ? '' : 'none';
  document.getElementById('register-form').style.display = tab === 'register' ? '' : 'none';
  document.getElementById('login-error').textContent = '';
  document.getElementById('reg-error').textContent = '';
}

async function handleLogin(e) {
  e.preventDefault();
  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;
  const errEl = document.getElementById('login-error');
  const btn = document.getElementById('login-btn');
  if (!username || !password) { errEl.textContent = 'Please fill all fields.'; return; }

  btn.disabled = true; btn.textContent = 'Signing in…';
  try {
    const res = await API.post('/auth/login', { username, password });
    const data = await res.json();
    if (!res.ok) { errEl.textContent = data.detail || 'Login failed.'; return; }
    saveAuth(data.access_token, username);
    initApp();
  } catch (err) {
    if (err.message !== 'rate_limit') errEl.textContent = 'Network error. Try again.';
  } finally {
    btn.disabled = false; btn.textContent = 'Sign In';
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const username = document.getElementById('reg-username').value.trim();
  const password = document.getElementById('reg-password').value;
  const errEl = document.getElementById('reg-error');
  const btn = document.getElementById('reg-btn');
  if (!username || !password) { errEl.textContent = 'Please fill all fields.'; return; }
  if (password.length < 6) { errEl.textContent = 'Password must be at least 6 characters.'; return; }

  btn.disabled = true; btn.textContent = 'Creating…';
  try {
    const res = await API.post('/auth/register', { username, password });
    const data = await res.json();
    if (!res.ok) { errEl.textContent = data.detail || 'Registration failed.'; return; }
    saveAuth(data.access_token, username);
    showToast('Account created! Welcome.', 'success');
    initApp();
  } catch (err) {
    if (err.message !== 'rate_limit') errEl.textContent = 'Network error. Try again.';
  } finally {
    btn.disabled = false; btn.textContent = 'Create Account';
  }
}

function saveAuth(token, username) {
  state.token = token;
  state.username = username;
  state.userProfile = null;
  localStorage.setItem('cd_token', token);
  localStorage.setItem('cd_username', username);
}

function logout() {
  state.token = null; state.username = null; state.userProfile = null; state.currentSessionId = null;
  localStorage.removeItem('cd_token'); localStorage.removeItem('cd_username');
  document.getElementById('auth-overlay').classList.remove('hidden');
  closeProfileMenu();
  document.getElementById('sessions-list').innerHTML = '';
  clearMessages();
}

// ── App init ──────────────────────────────────────────────
async function initApp() {
  if (!state.token) { document.getElementById('auth-overlay').classList.remove('hidden'); return; }
  document.getElementById('auth-overlay').classList.add('hidden');

  renderProfile();

  await loadProfile();
  await loadSessions();
}

async function loadProfile() {
  try {
    const res = await API.get('/auth/me');
    if (!res.ok) return;
    state.userProfile = await res.json();
    state.username = state.userProfile.username;
    localStorage.setItem('cd_username', state.username);
    renderProfile();
  } catch (err) {
    if (err.message !== 'unauthorized') renderProfile();
  }
}

function renderProfile() {
  const profile = state.userProfile || {};
  const username = profile.username || state.username || 'User';
  const initials = username.slice(0, 2).toUpperCase();
  const isActive = profile.is_active !== false;

  document.getElementById('user-avatar').textContent = initials;
  document.getElementById('profile-avatar').textContent = initials;
  document.getElementById('user-name-display').textContent = username;
  document.getElementById('profile-name').textContent = username;
  document.getElementById('profile-status').textContent = isActive ? 'Active account' : 'Inactive account';
  document.getElementById('profile-status').style.color = isActive ? 'var(--success)' : 'var(--danger)';
  document.getElementById('profile-session-count').textContent = profile.session_count ?? '—';
  document.getElementById('profile-appointment-count').textContent = profile.appointment_count ?? '—';
  document.getElementById('profile-created-at').textContent = formatDate(profile.created_at);
}

function toggleProfileMenu() {
  const panel = document.getElementById('profile-panel');
  const btn = document.getElementById('profile-btn');
  const isOpen = panel.classList.toggle('hidden') === false;
  btn.setAttribute('aria-expanded', String(isOpen));
}

function closeProfileMenu() {
  const panel = document.getElementById('profile-panel');
  const btn = document.getElementById('profile-btn');
  if (!panel || !btn) return;
  panel.classList.add('hidden');
  btn.setAttribute('aria-expanded', 'false');
}

// ── Sessions ──────────────────────────────────────────────
async function loadSessions() {
  try {
    const res = await API.get('/sessions');
    if (!res.ok) return;
    const sessions = await res.json();
    renderSessions(sessions);
  } catch (_) {}
}

function renderSessions(sessions) {
  const list = document.getElementById('sessions-list');
  list.innerHTML = '';
  if (sessions.length === 0) {
    list.innerHTML = '<div style="padding:12px;font-size:12px;color:var(--text-muted);text-align:center;">No sessions yet</div>';
    return;
  }
  sessions.forEach(s => {
    const item = document.createElement('div');
    item.className = 'session-item' + (s.id === state.currentSessionId ? ' active' : '');
    item.setAttribute('role', 'listitem');
    item.dataset.id = s.id;
    item.innerHTML = `
      <span class="session-title" title="${escHtml(s.title)}">${escHtml(s.title)}</span>
      <span class="session-delete" onclick="deleteSession(event,'${s.id}')" title="Delete" role="button" aria-label="Delete session">✕</span>
    `;
    item.addEventListener('click', (e) => {
      if (!e.target.classList.contains('session-delete')) openSession(s.id, s.title);
    });
    list.appendChild(item);
  });
}

async function openSession(sessionId, title) {
  state.currentSessionId = sessionId;
  document.getElementById('chat-title').textContent = title || 'Chat';
  clearMessages();
  document.getElementById('welcome-screen')?.remove();

  // Mark active
  document.querySelectorAll('.session-item').forEach(el => {
    el.classList.toggle('active', el.dataset.id === sessionId);
  });

  try {
    const res = await API.get(`/sessions/${sessionId}/messages`);
    if (!res.ok) return;
    const msgs = await res.json();
    msgs.forEach(m => {
      if (m.role === 'user') appendUserMessage(m.content);
      else appendAssistantMessage(m.content, m.route, null);
    });
    scrollToBottom();
  } catch (_) {}
}

async function newChat() {
  state.currentSessionId = null;
  clearMessages();
  document.getElementById('chat-title').textContent = 'New Conversation';
  document.getElementById('route-badge').style.display = 'none';

  // Re-add welcome screen
  const msgs = document.getElementById('messages');
  msgs.innerHTML = `
    <div class="welcome" id="welcome-screen">
      <div class="welcome-icon">🩺</div>
      <h2>How can I help you?</h2>
      <p>Ask a medical question, request an appointment, or get clinical information.</p>
      <div class="quick-prompts">
        <button class="quick-prompt" onclick="usePrompt(this)">What are symptoms of diabetes?</button>
        <button class="quick-prompt" onclick="usePrompt(this)">Book a cardiology appointment</button>
        <button class="quick-prompt" onclick="usePrompt(this)">How to manage high blood pressure?</button>
        <button class="quick-prompt" onclick="usePrompt(this)">What is hypertension?</button>
      </div>
    </div>`;

  document.querySelectorAll('.session-item').forEach(el => el.classList.remove('active'));
}

async function deleteSession(e, sessionId) {
  e.stopPropagation();
  try {
    await API.del(`/sessions/${sessionId}`);
    if (state.currentSessionId === sessionId) newChat();
    await loadSessions();
    showToast('Session deleted', 'info');
  } catch (_) {
    showToast('Failed to delete', 'error');
  }
}

// ── Messaging ─────────────────────────────────────────────
async function sendMessage() {
  if (state.isSending) return;
  const input = document.getElementById('message-input');
  const text = input.value.trim();
  if (!text) return;

  state.isSending = true;
  input.value = '';
  autoResize(input);
  updateCharCount(0);
  document.getElementById('send-btn').disabled = true;

  // Remove welcome
  document.getElementById('welcome-screen')?.remove();

  appendUserMessage(text);
  const typingEl = appendTyping();
  scrollToBottom();

  try {
    const body = { message: text };
    if (state.currentSessionId) body.session_id = state.currentSessionId;

    const res = await API.post('/chat', body);
    typingEl.remove();

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      appendAssistantMessage(`⚠️ ${err.detail || 'Something went wrong.'}`, 'escalation', null);
      return;
    }

    const data = await res.json();

    // Update session
    if (data.session_id && !state.currentSessionId) {
      state.currentSessionId = data.session_id;
      await loadSessions();
      // Mark active
      document.querySelectorAll('.session-item').forEach(el => {
        el.classList.toggle('active', el.dataset.id === data.session_id);
      });
    }

    // Update route badge
    const badge = document.getElementById('route-badge');
    badge.textContent = (data.route || '').replace('_', ' ');
    badge.className = `route-badge ${data.route}`;
    badge.style.display = 'inline-flex';

    appendAssistantMessage(data.answer, data.route, data.xai, data.structured_answer);
    scrollToBottom();
  } catch (err) {
    typingEl.remove();
    if (err.message !== 'rate_limit' && err.message !== 'unauthorized') {
      appendAssistantMessage('⚠️ Network error. Please try again.', 'escalation', null);
    }
  } finally {
    state.isSending = false;
    document.getElementById('send-btn').disabled = false;
    input.focus();
  }
}

function appendUserMessage(text) {
  const msgs = document.getElementById('messages');
  const el = document.createElement('div');
  el.className = 'message user';
  el.innerHTML = `
    <div class="msg-avatar">👤</div>
    <div class="msg-content">
      <div class="msg-bubble">${escHtml(text)}</div>
    </div>`;
  msgs.appendChild(el);
}

function appendAssistantMessage(text, route, xai, structured) {
  const msgs = document.getElementById('messages');
  const el = document.createElement('div');
  el.className = `message assistant${route === 'escalation' ? ' escalation' : ''}`;

  let xaiHtml = '';
  if (xai) {
    const conf = Math.round((xai.confidence || 0) * 100);
    const stepsHtml = (xai.decision_path || []).map(s =>
      `<div class="step-item"><div class="step-dot"></div><div class="step-text"><span class="step-outcome">${escHtml(s.step)}</span>: ${escHtml(s.outcome)} — ${escHtml(s.detail)}</div></div>`
    ).join('');

    const sourcesHtml = (xai.sources || []).map(s =>
      `<div class="source-tag"><span class="source-type-badge ${s.source_type || 'chatdoctor'}">${escHtml(s.source_type || 'chatdoctor')}</span><span>${escHtml(s.title)} (${s.score})</span></div>`
    ).join('');

    // Follow-up questions from structured output
    const fuHtml = structured && structured.follow_up_questions && structured.follow_up_questions.length
      ? `<div class="xai-section">
           <div class="xai-label">💬 Follow-up Questions</div>
           <div class="follow-up-list">
             ${structured.follow_up_questions.map(q => `<div class="follow-up-item" onclick="useFollowUp(this)" title="Click to ask">${escHtml(q)}</div>`).join('')}
           </div>
         </div>`
      : '';

    xaiHtml = `
      <div class="xai-toggle" onclick="toggleXAI(this)" role="button" tabindex="0" aria-expanded="false">
        <span class="chevron">▶</span>
        <span>Explainability · ${conf}% confidence · ${(xai.sources || []).length} sources</span>
      </div>
      <div class="xai-panel">
        <div class="xai-section">
          <div class="xai-label">Confidence</div>
          <div>${conf}%</div>
          <div class="confidence-bar"><div class="confidence-fill" style="width:${conf}%"></div></div>
        </div>
        <div class="xai-section">
          <div class="xai-label">Decision Path</div>
          <div class="step-list">${stepsHtml || '<span style="color:var(--text-muted)">No steps</span>'}</div>
        </div>
        ${sourcesHtml ? `<div class="xai-section"><div class="xai-label">Sources</div><div class="source-list">${sourcesHtml}</div></div>` : ''}
        ${fuHtml}
        <div class="xai-section" style="border-top:1px solid var(--border);padding-top:8px;margin-top:8px;">
          <div style="font-size:11px;color:var(--text-muted)">${escHtml(xai.safety_note || '')}</div>
        </div>
      </div>`;
  }

  el.innerHTML = `
    <div class="msg-avatar">🏥</div>
    <div class="msg-content">
      <div class="msg-bubble">${escHtml(text)}</div>
      ${xaiHtml}
    </div>`;
  msgs.appendChild(el);
}

function appendTyping() {
  const msgs = document.getElementById('messages');
  const el = document.createElement('div');
  el.className = 'message assistant';
  el.innerHTML = `
    <div class="msg-avatar">🏥</div>
    <div class="msg-content">
      <div class="msg-bubble">
        <div class="typing"><span></span><span></span><span></span></div>
      </div>
    </div>`;
  msgs.appendChild(el);
  return el;
}

function toggleXAI(el) {
  const panel = el.nextElementSibling;
  const isOpen = panel.classList.toggle('open');
  el.classList.toggle('open', isOpen);
  el.setAttribute('aria-expanded', isOpen);
}

function usePrompt(btn) {
  const input = document.getElementById('message-input');
  input.value = btn.textContent;
  autoResize(input);
  updateCharCount(input.value.length);
  document.getElementById('send-btn').disabled = false;
  input.focus();
}

function useFollowUp(el) {
  const input = document.getElementById('message-input');
  input.value = el.textContent.replace('?', '') + '?';
  autoResize(input);
  updateCharCount(input.value.length);
  document.getElementById('send-btn').disabled = false;
  input.focus();
}

// ── Input handling ────────────────────────────────────────
function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function handleInput() {
  const input = document.getElementById('message-input');
  autoResize(input);
  updateCharCount(input.value.length);
  document.getElementById('send-btn').disabled = input.value.trim().length === 0;
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 160) + 'px';
}

function updateCharCount(n) {
  const el = document.getElementById('char-count');
  el.textContent = `${n} / 1000`;
  el.style.color = n > 900 ? 'var(--danger)' : n > 700 ? 'var(--warning)' : 'var(--text-muted)';
}

// ── Utils ─────────────────────────────────────────────────
function clearMessages() {
  document.getElementById('messages').innerHTML = '';
}

function scrollToBottom() {
  const msgs = document.getElementById('messages');
  requestAnimationFrame(() => { msgs.scrollTop = msgs.scrollHeight; });
}

function escHtml(str) {
  return String(str || '')
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function formatDate(value) {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '—';
  return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
}

function showToast(msg, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.3s'; setTimeout(() => toast.remove(), 300); }, 3000);
}

// ── Boot ──────────────────────────────────────────────────
document.addEventListener('click', (e) => {
  if (!document.getElementById('profile-menu')?.contains(e.target)) closeProfileMenu();
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeProfileMenu();
});
initApp();
