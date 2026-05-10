Outreach Dashboard: A&R Scout Command Center

A music talent scouting dashboard designed for professional A&R teams. This tool automates the discovery of trending artists and generates personalized, data-driven outreach using local LLMs.

Setup

- Install Dependencies: pip install streamlit requests pandas

- Run Locally: streamlit run od.py

- Open localhost:8501

Core Features:
- Global Talent Radar: Dynamic Market Filtering: Real-time trending data across 15+ global markets (US, UK, etc.) using the Apple Music RSS API, including timeframe sensitivity.

- Deep "Track DNA" & Artist Analytics: 
    Multi-Source API Chaining: Seamlessly integrates data from iTunes (Metadata), Deezer (BPM, Fan Metrics, Audio Previews), and Wikipedia (Artist Biographies).
    Sonic Profiling: Instant visibility into a track's BPM, duration, and "Heat Score"—a custom metric derived from global streaming velocity.
    Brand Safety Monitoring: Automated detection of explicit content to ensure alignment with corporate sponsorship standards.

- AI-Powered Personalized Outreach
    Context-Aware Generation: Utilizing Ollama (Gemma/Llama) to draft outreach that considers the artist's genre, momentum, and exact release timeline.
    Smart Prompt Engineering: Python-side pre-processing calculates "Release Freshness" to ensure the AI avoids generic phrasing and placeholders like [Date].
    Custom Agency Profiles: Sidebar settings allow for persistence of Agency Name, Scout Name, and specific Outreach Objectives (e.g., Tour Booking vs. Label Signing).


Frontend: Streamlit (Custom CSS for Apple Glassmorphism/Bento-box UI).

Language: Python 3.14.2

APIs: iTunes RSS, Deezer Public API (Keyless), Wikipedia REST API.

LLM Orchestration: Ollama (Local gemma3:270M) & NVIDIA NIM (Cloud).

Data Handling: Requests for API ingestion, Pandas for transformation, and Datetime for historical filtering.
