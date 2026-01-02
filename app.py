import os
import re
import time
from typing import Dict, List, Optional

import streamlit as st

try:
    from openai import OpenAI  # type: ignore
except ImportError:  # pragma: no cover
    OpenAI = None

SYSTEM_PROMPT = """
You are TalentScout, a friendly hiring assistant for a tech recruitment agency. Goals:
- Be warm, encouraging, and conversational — use emojis sparingly.
- Greet, collect candidate details (name, email, phone, years of experience, desired roles, current location, tech stack).
- After tech stack is provided, generate tailored technical questions (3-5 total) across the declared stack.
- Celebrate small wins (e.g., "Great, got your email! ✓").
- Keep context of prior messages; stay on-purpose. If unsure, ask a clarifying question.
- Exit and thank the candidate when they send a conversation-ending keyword: bye, exit, quit, stop, thanks.
- If input is unclear, respond with a short fallback asking for clarification.
"""

EXIT_KEYWORDS = {"bye", "exit", "quit", "stop", "thanks", "thank you"}
INFO_FIELDS = [
    "Full Name",
    "Email Address",
    "Phone Number",
    "Years of Experience",
    "Desired Position(s)",
    "Current Location",
    "Tech Stack",
]

BASIC_QUESTION_BANK = {
    "python": [
        "Explain list vs tuple trade-offs.",
        "How do you manage virtual environments and dependencies?",
        "Describe a time you optimized Python code for performance.",
    ],
    "django": [
        "How do middleware and signals differ?",
        "When would you use select_related vs prefetch_related?",
    ],
    "flask": [
        "How do you structure a large Flask app with blueprints?",
        "Explain Flask's application and request context.",
    ],
    "fastapi": [
        "How does dependency injection work in FastAPI?",
        "Explain async endpoints vs sync endpoints performance.",
    ],
    "react": [
        "How do you handle state normalization across complex components?",
        "What are the trade-offs between context and Redux?",
    ],
    "javascript": [
        "Explain closures and where you'd use them.",
        "How does the event loop differ between browser and Node?",
    ],
    "typescript": [
        "How do you use generics to create reusable components?",
        "Explain utility types like Partial, Pick, and Omit.",
    ],
    "node": [
        "How do you manage async error handling in Express?",
        "Explain event loop phases relevant to timers and I/O callbacks.",
    ],
    "java": [
        "Explain the difference between checked and unchecked exceptions.",
        "How does the JVM garbage collector work at a high level?",
    ],
    "spring": [
        "How does dependency injection work in Spring Boot?",
        "Explain the request lifecycle in a Spring MVC app.",
    ],
    "sql": [
        "How do you detect and fix N+1 query issues?",
        "Describe how you would design indexes for a write-heavy table.",
    ],
    "postgresql": [
        "When would you use JSONB vs a normalized schema?",
        "Explain MVCC and its impact on concurrent transactions.",
    ],
    "mongodb": [
        "How do you design schemas for embedded vs referenced documents?",
        "Explain indexing strategies for large collections.",
    ],
    "redis": [
        "When would you use Redis Streams vs Pub/Sub?",
        "Explain data eviction policies in Redis.",
    ],
    "aws": [
        "Explain when to choose SQS vs SNS.",
        "How do you secure IAM roles for least privilege?",
    ],
    "gcp": [
        "Compare Cloud Run and GKE for a microservice.",
        "How do you design VPC Service Controls for data exfiltration protection?",
    ],
    "azure": [
        "Compare Azure Functions consumption vs premium plans.",
        "How do you implement managed identities for secure access?",
    ],
    "docker": [
        "How do you keep images small and reproducible?",
        "What is the difference between CMD and ENTRYPOINT?",
    ],
    "kubernetes": [
        "How do you handle pod disruption budgets in production?",
        "What signals would trigger a custom HPA policy?",
    ],
    "git": [
        "How do you resolve a complex merge conflict?",
        "Explain rebase vs merge and when to use each.",
    ],
}


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600&display=swap');
        :root {
            --bg: radial-gradient(circle at 20% 20%, #0f172a 0, #0b1220 35%, #060b18 70%, #040813 100%);
            --bg-soft: linear-gradient(135deg, rgba(56,189,248,0.08), rgba(14,165,233,0.05));
            --card: rgba(255, 255, 255, 0.06);
            --card-strong: rgba(255, 255, 255, 0.10);
            --border: rgba(255, 255, 255, 0.10);
            --pill: rgba(255, 255, 255, 0.12);
            --input: rgba(255, 255, 255, 0.08);
            --accent: #7dd3fc;
            --accent-strong: #38bdf8;
            --success: #4ade80;
            --text: #e2e8f0;
            --muted: #94a3b8;
        }
        html, body, [class*="main"], .stApp {
            background: var(--bg);
            color: var(--text);
            font-family: 'Space Grotesk', 'Inter', system-ui, -apple-system, sans-serif;
            background-attachment: fixed;
        }
        [data-testid="stSidebar"] { background: rgba(8, 12, 22, 0.85); border-right: 1px solid var(--border); }
        [data-testid="stSidebar"] .block-container { padding-top: 1.2rem; }
        .stChatMessage { border: 1px solid var(--border); background: var(--card); border-radius: 14px; animation: fadeIn 0.3s ease-out; }
        [data-testid="stChatInput"] textarea { background: var(--input); border: 1px solid var(--border); color: var(--text); }
        [data-testid="stTextInput"] input { background: var(--input); border: 1px solid var(--border); color: var(--text); }
        [data-testid="stTextInput"] input:focus { border: 1px solid var(--accent-strong); box-shadow: 0 0 0 2px rgba(56,189,248,0.25); }
        [data-testid="stForm"] { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 8px 10px; }
        .st-emotion-cache-13ln4jf { background: transparent; }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        @keyframes celebrate {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 999px;
            background: var(--pill);
            color: var(--text);
            font-weight: 600;
            font-size: 0.85rem;
            border: 1px solid var(--border);
            transition: all 0.2s ease;
            cursor: pointer;
        }
        .pill:hover { background: rgba(255,255,255,0.18); transform: translateY(-1px); }
        
        .quick-reply {
            display: inline-block;
            padding: 8px 16px;
            margin: 4px;
            border-radius: 20px;
            background: var(--pill);
            color: var(--text);
            font-size: 0.9rem;
            border: 1px solid var(--border);
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .quick-reply:hover { background: var(--accent); color: #0f172a; }
        
        .glass-card {
            padding: 16px 18px;
            border-radius: 16px;
            border: 1px solid var(--border);
            background: var(--card);
            box-shadow: 0 20px 40px rgba(0,0,0,0.25);
            backdrop-filter: blur(12px);
        }
        .question-card {
            padding: 14px 16px;
            margin-bottom: 10px;
            border-radius: 12px;
            border: 1px solid var(--border);
            background: var(--bg-soft);
            color: var(--text);
            transition: all 0.2s ease;
            cursor: pointer;
        }
        .question-card:hover { border-color: var(--accent); transform: translateX(4px); }
        
        .hero { border: 1px solid var(--border); background: var(--card-strong); border-radius: 18px; padding: 18px 20px; box-shadow: 0 12px 30px rgba(0,0,0,0.35); }
        .muted { color: var(--muted); }
        
        .typing-indicator { display: flex; gap: 4px; padding: 8px 12px; }
        .typing-dot { 
            width: 8px; height: 8px; 
            background: var(--accent); 
            border-radius: 50%; 
            animation: pulse 1s infinite; 
        }
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        
        .celebration { animation: celebrate 0.5s ease; }
        .field-complete { color: var(--success); }
        
        .answer-area {
            background: var(--input);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 10px;
            margin-top: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "candidate" not in st.session_state:
        st.session_state.candidate = {}
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "ended" not in st.session_state:
        st.session_state.ended = False
    if "current_q" not in st.session_state:
        st.session_state.current_q = 0  # Track current question being answered
    if "answers" not in st.session_state:
        st.session_state.answers = {}  # Store technical answers
    if "api_key" not in st.session_state:
        # Check env var or Streamlit secrets
        st.session_state.api_key = (
            os.getenv("OPENAI_API_KEY")
            or st.secrets.get("OPENAI_API_KEY", "")
        )


def validate_email(email: str) -> bool:
    """Basic email format check."""
    return bool(re.match(r"^[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}$", email))


def validate_phone(phone: str) -> bool:
    """Accept 10+ digits with optional country code/dashes."""
    digits = re.sub(r"\D", "", phone)
    return 10 <= len(digits) <= 15


def extract_info_from_text(text: str) -> Dict[str, str]:
    """Try to parse name, email, phone from free text."""
    found: Dict[str, str] = {}
    # Email
    email_match = re.search(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}", text)
    if email_match:
        found["Email Address"] = email_match.group()
    # Phone (10+ digits)
    phone_match = re.search(r"(\+?\d[\d\s\-]{8,}\d)", text)
    if phone_match:
        found["Phone Number"] = phone_match.group().strip()
    # Years of experience
    exp_match = re.search(r"(\d{1,2})\s*(?:\+)?\s*(?:years?|yrs?)", text, re.IGNORECASE)
    if exp_match:
        found["Years of Experience"] = exp_match.group(1)
    return found


def normalize_stack(raw_stack: str) -> List[str]:
    parts = re.split(r"[,/]| and | & |\n", raw_stack, flags=re.IGNORECASE)
    clean = [p.strip().lower() for p in parts if p.strip()]
    seen = []
    for item in clean:
        if item not in seen:
            seen.append(item)
    return seen


def pick_questions(stack_items: List[str]) -> List[str]:
    picked: List[str] = []
    for item in stack_items:
        if item in BASIC_QUESTION_BANK:
            pool = BASIC_QUESTION_BANK[item]
            picked.extend(pool[:2])
    if not picked:
        picked.append("Walk me through a recent project that best shows your expertise in this stack.")
        picked.append("What trade-offs did you consider when choosing these tools?")
    return picked[:5]


def run_llm(messages: List[Dict[str, str]], model: str = "llama-3.3-70b-versatile") -> Optional[str]:
    """Call Groq API (OpenAI-compatible). Returns None if unavailable."""
    api_key = st.session_state.get("api_key", "")
    if not api_key or OpenAI is None:
        return None
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        completion = client.chat.completions.create(model=model, messages=messages, temperature=0.3)
        return completion.choices[0].message.content
    except Exception:
        return None


def respond(user_text: str) -> str:
    # Build context with captured candidate info
    candidate_info = st.session_state.candidate
    context_block = ""
    if candidate_info:
        details = "\n".join(f"- {k}: {v}" for k, v in candidate_info.items() if v)
        context_block = f"\n\n[ALREADY CAPTURED - do NOT ask for these again]\n{details}\n"
    
    system_with_context = SYSTEM_PROMPT + context_block
    
    messages = [{"role": "system", "content": system_with_context}]
    for msg in st.session_state.messages[-8:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_text})
    llm_reply = run_llm(messages)
    if llm_reply:
        return llm_reply
    
    # Fallback: check what's missing
    missing = [f for f in INFO_FIELDS if not candidate_info.get(f)]
    if missing:
        return f"Got it! I still need: {', '.join(missing)}. Could you share those?"
    return "Great, I have all your details! Check the technical questions below, or type 'bye' when done."


def ensure_questions() -> None:
    stack = st.session_state.candidate.get("Tech Stack", "")
    if not stack or st.session_state.questions:
        return
    items = normalize_stack(stack)
    st.session_state.questions = pick_questions(items)


def render_sidebar() -> None:
    # API key section
    st.sidebar.header("⚙️ Settings")
    key_input = st.sidebar.text_input(
        "Groq API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="gsk_...",
        help="Free key from console.groq.com — or set OPENAI_API_KEY env var.",
    )
    if key_input != st.session_state.api_key:
        st.session_state.api_key = key_input
    if st.session_state.api_key:
        st.sidebar.success("API key set ✓")
    else:
        st.sidebar.warning("No API key — using fallback responses.")
    st.sidebar.divider()

    # Candidate details section
    st.sidebar.header("📋 Captured details")
    filled = sum(1 for f in INFO_FIELDS if st.session_state.candidate.get(f))
    
    # Celebration when all fields complete
    if filled == len(INFO_FIELDS):
        st.sidebar.markdown("<div class='celebration'>🎉 All fields complete!</div>", unsafe_allow_html=True)
        st.sidebar.balloons()
    else:
        st.sidebar.progress(filled / len(INFO_FIELDS), text=f"{filled}/{len(INFO_FIELDS)} fields")
    
    if not st.session_state.candidate:
        st.sidebar.info("Share details in the form or chat.")
    else:
        for k, v in st.session_state.candidate.items():
            icon = "✓" if v else "○"
            st.sidebar.markdown(f"<span class='field-complete'>{icon}</span> **{k}:** {v}", unsafe_allow_html=True)
    
    st.sidebar.divider()
    
    # Quick stats
    if st.session_state.answers:
        st.sidebar.header("📝 Answers submitted")
        st.sidebar.write(f"{len(st.session_state.answers)}/{len(st.session_state.questions)} questions")
    
    st.sidebar.divider()
    st.sidebar.caption("Exit keywords: bye, exit, quit, stop, thanks")


def render_form() -> None:
    with st.expander("Provide your details"):
        with st.form("candidate_form"):
            entries = {}
            for field in INFO_FIELDS:
                placeholder = "" if field != "Tech Stack" else "e.g., Python, Django, React, PostgreSQL"
                entries[field] = st.text_input(field, value=st.session_state.candidate.get(field, ""), placeholder=placeholder)
            submitted = st.form_submit_button("Save")
            if submitted:
                st.session_state.candidate.update({k: v.strip() for k, v in entries.items() if v.strip()})
                ensure_questions()
                st.success("Details saved.")


def add_message(role: str, content: str) -> None:
    st.session_state.messages.append({"role": role, "content": content})


def main() -> None:
    st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🧭", layout="wide")
    inject_styles()
    init_state()

    hero = st.container()
    with hero:
        st.markdown("<div class='hero'>", unsafe_allow_html=True)
        c1, c2 = st.columns([1.4, 1])
        with c1:
            st.markdown("### 🧭 TalentScout Hiring Assistant")
            st.markdown(
                "Tailored screening with smart prompts, offline-safe fallbacks, and tech-stack driven questions."
            )
            st.markdown(
                "<div class='pill'>⚡ Context aware</div> <div class='pill'>🔒 Local-first</div> <div class='pill'>🧠 LLM-ready</div>",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                "<div class='glass-card'><strong>💡 Quick tips</strong><br><span class='muted'>• Share info via chat or form<br>• Mention your tech stack<br>• Answer questions below<br>• Type 'bye' when done</span></div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    render_form()
    render_sidebar()
    
    # Quick reply suggestions when no messages
    if not st.session_state.messages and not st.session_state.ended:
        st.markdown("### 👋 Let's get started!")
        st.markdown("Click a quick reply or type your own message:")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("👤 Share my info", use_container_width=True):
                add_message("user", "I'd like to share my details")
                reply = respond("I'd like to share my details")
                add_message("assistant", reply)
                st.rerun()
        with col2:
            if st.button("💻 My tech stack", use_container_width=True):
                add_message("user", "Let me tell you about my tech stack")
                reply = respond("Let me tell you about my tech stack")
                add_message("assistant", reply)
                st.rerun()
        with col3:
            if st.button("❓ What do you need?", use_container_width=True):
                add_message("user", "What information do you need from me?")
                reply = respond("What information do you need from me?")
                add_message("assistant", reply)
                st.rerun()

    # Display chat messages with animations
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🧭" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

    if st.session_state.ended:
        st.success("✅ Conversation complete! Refresh the page to start a new session.")
        if st.button("🔄 Start New Session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    else:
        user_input = st.chat_input("Type here to chat... 💬")
        if user_input:
            if user_input.strip().lower() in EXIT_KEYWORDS:
                farewell = "Thanks for your time! 🎉 We will review your profile and reach out soon. Best of luck!"
                add_message("user", user_input)
                add_message("assistant", farewell)
                st.session_state.ended = True
                st.rerun()

            add_message("user", user_input)

            # Smart extraction from free text
            extracted = extract_info_from_text(user_input)
            for k, v in extracted.items():
                st.session_state.candidate.setdefault(k, v)

            # Tech stack detection
            tech_match = re.search(r"tech stack[:\s-]*(.+)", user_input, re.IGNORECASE)
            if tech_match:
                st.session_state.candidate["Tech Stack"] = tech_match.group(1).strip()

            reply = respond(user_input)
            add_message("assistant", reply)

            ensure_questions()
            st.rerun()

    # Interactive technical questions section
    if st.session_state.questions:
        st.markdown("---")
        st.subheader("📝 Technical Assessment")
        st.markdown("Answer these questions to showcase your skills. Your responses are saved automatically.")
        
        for idx, q in enumerate(st.session_state.questions):
            q_key = f"q_{idx}"
            answered = q_key in st.session_state.answers
            
            with st.expander(f"{'✅' if answered else '📌'} Question {idx + 1}", expanded=not answered):
                st.markdown(f"**{q}**")
                
                # Answer input
                answer = st.text_area(
                    "Your answer:",
                    value=st.session_state.answers.get(q_key, ""),
                    key=f"answer_{idx}",
                    height=100,
                    placeholder="Type your answer here...",
                )
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("💾 Save", key=f"save_{idx}"):
                        if answer.strip():
                            st.session_state.answers[q_key] = answer.strip()
                            st.success("Saved! ✓")
                            st.rerun()
                        else:
                            st.warning("Please enter an answer first.")
                with col2:
                    if answered:
                        st.markdown(f"<span style='color: #4ade80;'>✓ Answered ({len(answer.split())} words)</span>", unsafe_allow_html=True)
        
        # Summary when all questions answered
        if len(st.session_state.answers) == len(st.session_state.questions):
            st.success("🎉 All questions answered! Type 'bye' in the chat to complete your screening.")


if __name__ == "__main__":
    main()
