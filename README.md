# 🧭 TalentScout Hiring Assistant

An intelligent AI-powered chatbot for candidate screening, built with Streamlit and Groq LLM.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red.svg)
![LLM](https://img.shields.io/badge/LLM-Groq%20Llama%203.3-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Features](#-features)
- [Demo](#-demo)
- [Installation](#-installation)
- [Usage Guide](#-usage-guide)
- [Technical Architecture](#-technical-architecture)
- [Prompt Design](#-prompt-design)
- [Data Handling & Privacy](#-data-handling--privacy)
- [Challenges & Solutions](#-challenges--solutions)
- [Future Enhancements](#-future-enhancements)

---

## 🎯 Project Overview

**TalentScout** is an intelligent hiring assistant chatbot designed for a fictional tech recruitment agency. It streamlines the initial candidate screening process by:

1. **Gathering candidate information** — Name, email, phone, experience, desired roles, location, and tech stack
2. **Generating tailored technical questions** — Based on the candidate's declared technologies
3. **Providing interactive assessments** — Candidates can answer questions directly in the app
4. **Maintaining conversation context** — Seamless, coherent chat experience

### Why TalentScout?

- ⚡ **Fast screening** — Automates repetitive information gathering
- 🎯 **Relevant questions** — Tech-stack specific assessments
- 🔒 **Privacy-first** — No data leaves your machine without explicit API calls
- 💰 **Cost-effective** — Uses free Groq API with offline fallback

---

## ✨ Features

### Core Functionality

| Feature | Description |
|---------|-------------|
| **Smart Greeting** | Warm, professional introduction with purpose explanation |
| **Information Capture** | Collects 7 key fields via chat or form |
| **Auto-extraction** | Parses emails, phones, experience from free text |
| **Tech Stack Detection** | Identifies technologies from conversation |
| **Dynamic Questions** | Generates 3-5 questions per tech stack |
| **Context Awareness** | Never re-asks for captured information |
| **Graceful Exit** | Detects exit keywords and closes conversation |
| **Fallback Mode** | Works offline with rule-based responses |

### Interactive Elements

- 🎯 **Quick reply buttons** — One-click conversation starters
- 📝 **Expandable Q&A** — Answer technical questions in-app
- 💾 **Auto-save answers** — Responses saved to session
- 🎈 **Celebrations** — Balloons when all fields complete
- 📊 **Progress tracking** — Visual progress bar in sidebar
- 🔄 **Session reset** — Start new screening without refresh

### UI/UX

- 🌙 **Dark mode design** — Modern glassmorphism aesthetic
- ✨ **Smooth animations** — Fade-in messages, hover effects
- 📱 **Responsive layout** — Works on desktop and tablet
- 🎨 **Custom styling** — Space Grotesk font, accent colors

---

## 🎬 Demo

### Quick Start
```bash
# Clone and run
git clone <your-repo-url>
cd Hiring-Assistant-chatbot
pip install -r requirements.txt
streamlit run app.py
```

### Screenshots

**Main Interface:**
- Hero section with quick tips
- Quick reply buttons for easy start
- Chat interface with custom avatars
- Sidebar with captured details and progress

**Technical Assessment:**
- Expandable question cards
- Text area for answers
- Save button with word count
- Completion celebration

---

## 🛠 Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Step 1: Clone Repository

```bash
git clone <your-repo-url>
cd Hiring-Assistant-chatbot
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure API Key (Optional but Recommended)

Get a free API key from [console.groq.com](https://console.groq.com)

**Option A: Streamlit Secrets (Recommended)**
```bash
# Edit .streamlit/secrets.toml
OPENAI_API_KEY = "gsk_your_key_here"
```

**Option B: Environment Variable**
```bash
export OPENAI_API_KEY=gsk_your_key_here
```

**Option C: Sidebar Input**
- Paste key directly in the app's sidebar

### Step 4: Run the App

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📖 Usage Guide

### For Candidates

1. **Start the conversation** — Click a quick reply or type a message
2. **Share your details** — Use the form or chat naturally
3. **Declare your tech stack** — Mention technologies you know
4. **Answer questions** — Expand question cards and type answers
5. **Complete screening** — Type "bye" to finish

### Information Collected

| Field | Example | Auto-detected |
|-------|---------|---------------|
| Full Name | John Doe | ❌ |
| Email Address | john@example.com | ✅ |
| Phone Number | +1 555-123-4567 | ✅ |
| Years of Experience | 5 years | ✅ |
| Desired Position(s) | Senior Developer | ❌ |
| Current Location | New York, USA | ❌ |
| Tech Stack | Python, Django, React | ✅ |

### Exit Keywords

Type any of these to end the conversation:
- `bye`
- `exit`
- `quit`
- `stop`
- `thanks`

---

## 🏗 Technical Architecture

### Project Structure

```
Hiring-Assisment-chatbot/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This documentation
├── .gitignore            # Git ignore rules
├── .env.example          # Environment template
└── .streamlit/
    └── secrets.toml      # API keys (gitignored)
```

### Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Streamlit | UI framework |
| **LLM** | Groq (Llama 3.3 70B) | Conversation AI |
| **API Client** | OpenAI Python SDK | Groq compatibility |
| **Styling** | Custom CSS | Dark mode theme |

### Data Flow

```
User Input → Extract Info → Update State → Generate Response
     ↓              ↓              ↓              ↓
  Chat UI    Regex Patterns   Session State   LLM / Fallback
                                    ↓
                            Tech Stack Match
                                    ↓
                           Question Generation
```

### Key Functions

| Function | Purpose |
|----------|---------|
| `init_state()` | Initialize session state variables |
| `extract_info_from_text()` | Parse email, phone, experience from text |
| `normalize_stack()` | Clean and deduplicate tech stack items |
| `pick_questions()` | Select relevant questions from bank |
| `run_llm()` | Call Groq API with error handling |
| `respond()` | Build prompt with context and get response |
| `render_sidebar()` | Display settings and captured details |

---

## 🎨 Prompt Design

### System Prompt Strategy

The system prompt is designed to:

1. **Define persona** — Friendly, professional hiring assistant
2. **Set boundaries** — Stay on-purpose, no off-topic responses
3. **Enable context** — Acknowledge captured information
4. **Handle edge cases** — Fallback for unclear inputs

```python
SYSTEM_PROMPT = """
You are TalentScout, a friendly hiring assistant for a tech recruitment agency. Goals:
- Be warm, encouraging, and conversational — use emojis sparingly.
- Greet, collect candidate details (name, email, phone, years of experience, 
  desired roles, current location, tech stack).
- After tech stack is provided, generate tailored technical questions (3-5 total).
- Celebrate small wins (e.g., "Great, got your email! ✓").
- Keep context of prior messages; stay on-purpose.
- Exit and thank the candidate when they send an exit keyword.
- If input is unclear, ask for clarification.
"""
```

### Context Injection

Captured candidate details are appended to the system prompt:

```
[ALREADY CAPTURED - do NOT ask for these again]
- Full Name: John Doe
- Email Address: john@example.com
- Tech Stack: Python, Django
```

This prevents the LLM from re-asking for information.

### Question Generation

**Rule-based approach** for reliability:

1. Parse tech stack into normalized list
2. Match against question bank (20+ technologies)
3. Select top 2 questions per technology
4. Cap at 5 questions total
5. Fallback to generic questions if no matches

**Supported Technologies:**
- Languages: Python, JavaScript, TypeScript, Java
- Frameworks: Django, Flask, FastAPI, React, Node, Spring
- Databases: SQL, PostgreSQL, MongoDB, Redis
- Cloud: AWS, GCP, Azure
- DevOps: Docker, Kubernetes, Git

---

## 🔒 Data Handling & Privacy

### Data Storage

| Data Type | Storage | Persistence |
|-----------|---------|-------------|
| Candidate Info | Session State | Browser session only |
| Chat History | Session State | Browser session only |
| Technical Answers | Session State | Browser session only |
| API Key | Secrets/Env | Server-side only |

### Privacy Measures

1. **No database** — All data lives in session state
2. **No logging** — Conversations not stored server-side
3. **Local-first** — Works offline without API calls
4. **Gitignore** — Secrets excluded from version control
5. **GDPR-ready** — Data deleted on session end

### API Security

- API key stored in `.streamlit/secrets.toml` (gitignored)
- Password-masked input in sidebar
- Key never exposed in frontend code

---

## 🧩 Challenges & Solutions

### Challenge 1: LLM Availability

**Problem:** API calls can fail or be rate-limited.

**Solution:** Implemented dual-mode response system:
- Primary: Groq LLM for natural conversation
- Fallback: Rule-based responses for reliability

```python
def respond(user_text: str) -> str:
    llm_reply = run_llm(messages)
    if llm_reply:
        return llm_reply
    # Fallback logic
    missing = [f for f in INFO_FIELDS if not candidate_info.get(f)]
    return f"Got it! I still need: {', '.join(missing)}."
```

### Challenge 2: Context Management

**Problem:** LLM kept asking for already-provided information.

**Solution:** Inject captured details into system prompt with explicit instruction not to re-ask.

### Challenge 3: Tech Stack Parsing

**Problem:** Users express tech stacks in varied formats.

**Solution:** Flexible regex parsing with normalization:
- Split by comma, slash, "and", "&", newline
- Lowercase and deduplicate
- Match partial strings (e.g., "nodejs" → "node")

### Challenge 4: Token Limits

**Problem:** Long conversations exceed context window.

**Solution:** Rolling window of last 8 messages:
```python
for msg in st.session_state.messages[-8:]:
    messages.append({"role": msg["role"], "content": msg["content"]})
```

### Challenge 5: UI Responsiveness

**Problem:** Streamlit reruns on every interaction.

**Solution:** 
- Efficient state management
- Minimal re-renders with `st.rerun()`
- CSS animations for perceived performance

---

## 🚀 Future Enhancements

### Planned Features

- [ ] **Sentiment Analysis** — Gauge candidate confidence/stress
- [ ] **Multilingual Support** — Hindi, Spanish, French
- [ ] **Resume Upload** — Parse PDF/DOCX for auto-fill
- [ ] **Email Integration** — Send summary to recruiters
- [ ] **Analytics Dashboard** — Track screening metrics
- [ ] **Voice Input** — Speech-to-text for accessibility

### Deployment Options

- **Streamlit Cloud** — Free hosting with secrets management
- **AWS/GCP** — Containerized deployment
- **Heroku** — One-click deploy

---

## 📄 License

MIT License — Free for personal and commercial use.

---

## 👤 Author

Built for TalentScout AI/ML Intern Assignment

---

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io) — Amazing Python UI framework
- [Groq](https://groq.com) — Fast, free LLM inference
- [Llama 3.3](https://ai.meta.com/llama/) — Powerful open-source model
