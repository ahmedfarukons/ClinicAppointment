import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  clearStoredAuth,
  deleteSession,
  getStoredAuth,
  listMessages,
  listSessions,
  login,
  register,
  saveStoredAuth,
  sendChatMessage,
} from "../services/aiAssistant";
import { ApiError } from "../services/api";

const QUICK_PROMPTS = [
  "When should I see a doctor for a headache?",
  "I want to book a cardiology appointment",
  "What should I watch for with high blood pressure?",
  "What are the symptoms of diabetes?",
];

const ROUTE_LABELS = {
  medical_info: "Medical information",
  appointment_request: "Appointment request",
  escalation: "Doctor escalation",
};

function errorText(error) {
  if (error instanceof ApiError && error.status === 401) {
    return "Your session has expired. Please sign in again.";
  }
  if (error instanceof ApiError && error.status === 429) {
    return "Too many requests. Please try again shortly.";
  }
  if (error instanceof ApiError && error.status === 400) {
    return error.message === "Username already exists"
      ? "This username is already registered. Choose a different username or sign in."
      : error.message;
  }
  if (error instanceof ApiError && error.status === 422) {
    return "Registration details are missing or too short. Username must be at least 3 characters and password at least 6 characters.";
  }
  return error?.message || "An unexpected error occurred.";
}

function routeLabel(route) {
  return ROUTE_LABELS[route] || "AI response";
}

function AuthPanel({ mode, setMode, onSubmit, loading, error }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const isRegister = mode === "register";

  function handleSubmit(event) {
    event.preventDefault();
    onSubmit({ username: username.trim(), password });
  }

  return (
    <div className="aiAuthCard">
      <div className="aiAuthHero">
        <div className="badge">AI Clinical Assistant</div>
        <h1 className="pageTitle">Ask your health questions to the smart assistant</h1>
        <p className="pageText">
          The ChatDoctor backend is integrated into the React interface with secure
          sessions, conversation history, source evidence, and explainable AI flow.
        </p>
      </div>

      <form className="form aiAuthForm" onSubmit={handleSubmit}>
        <div className="aiTabs" role="tablist" aria-label="AI assistant authentication mode">
          <button
            className={!isRegister ? "aiTab active" : "aiTab"}
            type="button"
            onClick={() => setMode("login")}
          >
            Sign In
          </button>
          <button
            className={isRegister ? "aiTab active" : "aiTab"}
            type="button"
            onClick={() => setMode("register")}
          >
            Create Account
          </button>
        </div>

        {error ? <div className="alert alertError">{error}</div> : null}

        <label className="field">
          <span className="label">Username</span>
          <input
            className="input"
            minLength={3}
            onChange={(event) => setUsername(event.target.value)}
            placeholder="ornek_kullanici"
            required
            type="text"
            value={username}
          />
        </label>
        <label className="field">
          <span className="label">Password</span>
          <input
            className="input"
            minLength={isRegister ? 6 : undefined}
            onChange={(event) => setPassword(event.target.value)}
            placeholder={isRegister ? "At least 6 characters" : "Your password"}
            required
            type="password"
            value={password}
          />
        </label>
        <button className="btn btnPrimary btnLarge" disabled={loading} type="submit">
          {loading ? "Connecting..." : isRegister ? "Create Account" : "Sign In"}
        </button>
      </form>
    </div>
  );
}

function Explainability({ xai, structuredAnswer }) {
  const [open, setOpen] = useState(false);
  if (!xai) return null;

  const confidence = Math.round((xai.confidence || 0) * 100);
  const sources = xai.sources || [];
  const steps = xai.decision_path || [];
  const followUps = structuredAnswer?.follow_up_questions || [];

  return (
    <div className="xaiBox">
      <button className="xaiButton" type="button" onClick={() => setOpen((value) => !value)}>
        Explainable AI: {confidence}% confidence · {sources.length} sources
      </button>
      {open ? (
        <div className="xaiContent">
          <div className="xaiConfidence">
            <span>Confidence score</span>
            <strong>%{confidence}</strong>
          </div>
          <div className="confidenceTrack">
            <div className="confidenceFill" style={{ width: `${confidence}%` }} />
          </div>

          {xai.rationale ? (
            <div className="xaiSection">
              <div className="xaiLabel">Rationale</div>
              <p>{xai.rationale}</p>
            </div>
          ) : null}

          {steps.length ? (
            <div className="xaiSection">
              <div className="xaiLabel">Decision steps</div>
              <div className="xaiSteps">
                {steps.map((step, index) => (
                  <div className="xaiStep" key={`${step.step}-${index}`}>
                    <strong>{step.step}</strong>
                    <span>{step.outcome}</span>
                    <small>{step.detail}</small>
                  </div>
                ))}
              </div>
            </div>
          ) : null}

          {sources.length ? (
            <div className="xaiSection">
              <div className="xaiLabel">Sources</div>
              <div className="sourceList">
                {sources.map((source) => (
                  <div className="sourceItem" key={source.id}>
                    <strong>{source.title}</strong>
                    <span>{source.source_type} · score {source.score}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : null}

          {followUps.length ? (
            <div className="xaiSection">
              <div className="xaiLabel">Follow-up questions</div>
              <div className="followUpList">
                {followUps.map((question) => (
                  <span className="chip chipSoft" key={question}>
                    {question}
                  </span>
                ))}
              </div>
            </div>
          ) : null}

          {xai.safety_note ? <p className="xaiSafety">{xai.safety_note}</p> : null}
        </div>
      ) : null}
    </div>
  );
}

function MessageList({ messages, sending }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, sending]);

  if (!messages.length && !sending) {
    return (
      <div className="aiWelcome">
        <div className="aiWelcomeIcon">+</div>
        <h2>How can I help?</h2>
        <p>
          Ask about symptoms, appointment requests, or clinical information. In
          emergencies, contact emergency services or the nearest healthcare facility.
        </p>
      </div>
    );
  }

  return (
    <div className="aiMessages" aria-live="polite">
      {messages.map((message) => (
        <article className={`aiMessage ${message.role}`} key={message.id}>
          <div className="aiAvatar">{message.role === "user" ? "Siz" : "AI"}</div>
          <div className="aiBubbleWrap">
            {message.route ? (
              <span className={`routePill ${message.route}`}>{routeLabel(message.route)}</span>
            ) : null}
            <div className="aiBubble">{message.content}</div>
            <Explainability xai={message.xai} structuredAnswer={message.structured_answer} />
          </div>
        </article>
      ))}
      {sending ? (
        <article className="aiMessage assistant">
          <div className="aiAvatar">AI</div>
          <div className="aiBubbleWrap">
            <div className="aiBubble typingBubble">
              <span />
              <span />
              <span />
            </div>
          </div>
        </article>
      ) : null}
      <div ref={bottomRef} />
    </div>
  );
}

export function AIAssistant() {
  const [{ token, username }, setAuth] = useState(() => getStoredAuth());
  const [authMode, setAuthMode] = useState("login");
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState("");
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState("");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [appError, setAppError] = useState("");

  const activeSession = useMemo(
    () => sessions.find((session) => session.id === activeSessionId),
    [activeSessionId, sessions]
  );

  const logout = useCallback(() => {
    clearStoredAuth();
    setAuth({ token: "", username: "" });
    setSessions([]);
    setMessages([]);
    setActiveSessionId("");
  }, []);

  const refreshSessions = useCallback(async () => {
    if (!token) return;
    try {
      setSessions(await listSessions(token));
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) logout();
      else setAppError(errorText(error));
    }
  }, [logout, token]);

  useEffect(() => {
    refreshSessions();
  }, [refreshSessions]);

  async function handleAuthSubmit({ username: submittedUsername, password }) {
    setAuthLoading(true);
    setAuthError("");
    if (submittedUsername.length < 3) {
      setAuthError("Username must be at least 3 characters.");
      setAuthLoading(false);
      return;
    }
    if (authMode === "register" && password.length < 6) {
      setAuthError("Password must be at least 6 characters for registration.");
      setAuthLoading(false);
      return;
    }
    try {
      const result =
        authMode === "register"
          ? await register(submittedUsername, password)
          : await login(submittedUsername, password);
      const nextAuth = { token: result.access_token, username: submittedUsername };
      saveStoredAuth(nextAuth);
      setAuth(nextAuth);
    } catch (error) {
      setAuthError(errorText(error));
    } finally {
      setAuthLoading(false);
    }
  }

  async function handleOpenSession(sessionId) {
    setAppError("");
    setActiveSessionId(sessionId);
    try {
      const history = await listMessages(token, sessionId);
      setMessages(
        history.map((message) => ({
          id: message.id,
          role: message.role,
          content: message.content,
          route: message.route,
        }))
      );
    } catch (error) {
      setAppError(errorText(error));
    }
  }

  function handleNewChat() {
    setActiveSessionId("");
    setMessages([]);
    setAppError("");
  }

  async function handleDeleteSession(event, sessionId) {
    event.stopPropagation();
    try {
      await deleteSession(token, sessionId);
      if (activeSessionId === sessionId) handleNewChat();
      await refreshSessions();
    } catch (error) {
      setAppError(errorText(error));
    }
  }

  async function handleSend(event) {
    event.preventDefault();
    const text = input.trim();
    if (!text || sending) return;

    setSending(true);
    setInput("");
    setAppError("");

    const userMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: text,
    };
    setMessages((current) => [...current, userMessage]);

    try {
      const result = await sendChatMessage(token, {
        message: text,
        sessionId: activeSessionId,
      });
      setActiveSessionId(result.session_id || activeSessionId);
      setMessages((current) => [
        ...current,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: result.answer,
          route: result.route,
          xai: result.xai,
          structured_answer: result.structured_answer,
        },
      ]);
      await refreshSessions();
    } catch (error) {
      setAppError(errorText(error));
      setMessages((current) => [
        ...current,
        {
          id: `assistant-error-${Date.now()}`,
          role: "assistant",
          content: "No response was received. Check that the backend service is running and the API keys are valid.",
          route: "escalation",
        },
      ]);
    } finally {
      setSending(false);
    }
  }

  if (!token) {
    return (
      <div className="page aiPage">
        <div className="container">
          <AuthPanel
            error={authError}
            loading={authLoading}
            mode={authMode}
            onSubmit={handleAuthSubmit}
            setMode={setAuthMode}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="page aiPage">
      <div className="container">
        <div className="pageHead aiHead">
          <div>
            <div className="badge">ChatDoctor + Blue Clinic</div>
            <h1 className="pageTitle">AI Clinical Assistant</h1>
            <p className="pageText">
              The backend AI module now runs inside the React frontend with conversation
              history, sources, and explainable decision steps.
            </p>
          </div>
          <button className="btn btnGhost" type="button" onClick={logout}>
            Sign Out ({username})
          </button>
        </div>

        {appError ? <div className="alert alertError aiAlert">{appError}</div> : null}

        <div className="aiLayout">
          <aside className="aiSidebar" aria-label="Conversations">
            <button className="btn btnPrimary aiNewChat" type="button" onClick={handleNewChat}>
              New Chat
            </button>
            <div className="aiSessionList">
              {sessions.length ? (
                sessions.map((session) => (
                  <div
                    className={
                      activeSessionId === session.id ? "aiSession active" : "aiSession"
                    }
                    key={session.id}
                  >
                    <button type="button" onClick={() => handleOpenSession(session.id)}>
                      <span>{session.title}</span>
                      <small>{new Date(session.updated_at).toLocaleString("en-US")}</small>
                    </button>
                    <button
                      className="aiDeleteSession"
                      type="button"
                      onClick={(event) => handleDeleteSession(event, session.id)}
                    >
                      Delete
                    </button>
                  </div>
                ))
              ) : (
                <div className="emptyText">No saved conversations yet.</div>
              )}
            </div>
          </aside>

          <section className="aiChatCard" aria-label="AI asistan sohbeti">
            <div className="aiChatTop">
              <div>
                <div className="panelTitle">
                  {activeSession?.title || "New conversation"}
                </div>
                <div className="hint">Responses are served through the FastAPI /chat endpoint.</div>
              </div>
              {activeSessionId ? (
                <span className="chip chipSoft">Session active</span>
              ) : (
                <span className="chip">New session</span>
              )}
            </div>

            <MessageList messages={messages} sending={sending} />

            <div className="quickPrompts">
              {QUICK_PROMPTS.map((prompt) => (
                <button
                  className="quickPrompt"
                  key={prompt}
                  type="button"
                  onClick={() => setInput(prompt)}
                >
                  {prompt}
                </button>
              ))}
            </div>

            <form className="aiComposer" onSubmit={handleSend}>
              <textarea
                aria-label="Write a message to the AI assistant"
                maxLength={1500}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Write your question..."
                rows={2}
                value={input}
              />
              <button className="btn btnPrimary" disabled={sending || !input.trim()} type="submit">
                Send
              </button>
            </form>
          </section>
        </div>
      </div>
    </div>
  );
}
