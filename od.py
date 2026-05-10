import streamlit as st
import streamlit.components.v1 as components
import time
import requests
import re
import uuid
import ollama
import openai
import urllib.parse
from datetime import datetime, timedelta
from email.message import EmailMessage

COUNTRIES = {
    "United States": "us", "United Kingdom": "gb", "Argentina": "ar", "Brazil": "br", 
    "Japan": "jp", "South Korea": "kr", "Germany": "de", "France": "fr", 
    "Mexico": "mx", "Spain": "es", "Canada": "ca", "Australia": "au", "India": "in"
}

# ──────────────────────────────────────────────
# 1. PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Outreach Dashboard",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# 2. CUSTOM CSS — Apple Music Dark-Mode Clone
# ──────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Import SF-style fallback font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ── Root variables ── */
    :root {
        --bg-main:       #262626;
        --bg-sidebar:    #1c1c1e;
        --bg-surface:    #1c1c1e;
        --bg-hover:      #2c2c2e;
        --text-primary:  #ffffff;
        --text-secondary:#a1a1a6;
        --accent:        #fa586a;
        --radius:        12px;
        --font-stack:    "SF Pro Display", "SF Pro Text", system-ui, Inter,
                         -apple-system, BlinkMacSystemFont, "Segoe UI",
                         Roboto, Helvetica, Arial, sans-serif;
    }


    /* ── Global resets ── */
    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stApp"] {
        background-color: var(--bg-main) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-stack) !important;
    }

    /* ── Hide Streamlit chrome safely ── */
    #MainMenu, footer, .stDeployButton, [data-testid="stAppDeployButton"] {
        display: none !important;
    }

    /* Make header & toolbar transparent but keep sidebar toggle alive */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        background: transparent !important;
    }
    [data-testid="stToolbar"] {
        display: flex !important;
        background: transparent !important;
        pointer-events: none;
    }
    /* Hide the toolbar action buttons (share, star, etc.) */
    [data-testid="stToolbarActions"] {
        display: none !important;
    }

    /* ── Force Sidebar Expand Button Visibility ── */
    [data-testid="stExpandSidebarButton"] {
        display: flex !important;
        visibility: visible !important;
        pointer-events: auto !important;
        z-index: 999999 !important;
        background-color: transparent !important;
    }
    [data-testid="stExpandSidebarButton"] svg,
    [data-testid="stExpandSidebarButton"] * {
        color: #ffffff !important;
        fill: #ffffff !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child {
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid #2c2c2e;
    }

    [data-testid="stSidebar"] {
        color: var(--text-primary) !important;
        font-family: var(--font-stack) !important;
    }

    /* Sidebar radio buttons */
    [data-testid="stSidebar"] .stRadio label {
        color: var(--text-secondary) !important;
        font-weight: 500;
        transition: color 0.2s ease;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        color: var(--text-primary) !important;
    }

    /* ── Text inputs ── */
    [data-testid="stTextInput"] input,
    .stTextInput input {
        background-color: var(--bg-surface) !important;
        color: var(--text-primary) !important;
        border: 1px solid #3a3a3c !important;
        border-radius: var(--radius) !important;
        padding: 0.65rem 1rem !important;
        font-size: 1rem !important;
        font-family: var(--font-stack) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    [data-testid="stTextInput"] input:focus,
    .stTextInput input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(250, 88, 106, 0.25) !important;
        outline: none !important;
    }
    [data-testid="stTextInput"] input::placeholder {
        color: var(--text-secondary) !important;
        opacity: 0.7;
    }

    /* ── Labels ── */
    label, .stTextInput label, .stRadio label,
    [data-testid="stWidgetLabel"] {
        color: var(--text-secondary) !important;
        font-family: var(--font-stack) !important;
        font-weight: 500 !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background-color: var(--accent) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: var(--radius) !important;
        padding: 0.55rem 1.6rem !important;
        font-weight: 600 !important;
        font-family: var(--font-stack) !important;
        transition: opacity 0.2s ease, transform 0.15s ease;
        cursor: pointer;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    .stButton > button:hover {
        opacity: 0.85;
        transform: scale(1.02);
    }
    .stButton > button:active {
        transform: scale(0.98);
    }

    /* ── Divider ── */
    [data-testid="stHorizontalBlock"] hr,
    hr {
        border-color: #2c2c2e !important;
        opacity: 0.6;
    }

    /* ── Scrollbar (Webkit) ── */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: var(--bg-main);
    }
    ::-webkit-scrollbar-thumb {
        background: #3a3a3c;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #48484a;
    }

    /* ── Custom containers (if used later) ── */
    [data-testid="stExpander"],
    [data-testid="stForm"],
    .element-container .stMarkdown div[data-testid] {
        border-radius: var(--radius) !important;
    }

    /* ── Main area top padding tweak ── */
    .block-container {
        padding-top: 2rem !important;
    }

    /* ── Premium Card Styling ── */
    .album-card {
        background: transparent;
        border: none;
        padding: 0;
        margin-bottom: 1.5rem;
        display: flex;
        flex-direction: column;
    }
    .album-card img {
        width: 100%;
        aspect-ratio: 1 / 1;
        object-fit: cover;
        border-radius: 8px; /* Standard radius */
        margin-bottom: 0.5rem;
        box-shadow: 0 6px 16px rgba(0,0,0,0.4);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .album-card img:hover {
        transform: scale(1.03); /* Slight zoom on hover */
        box-shadow: 0 10px 24px rgba(0,0,0,0.6);
    }
    .album-card .card-album {
        color: var(--text-primary);
        font-size: 0.9rem;
        font-weight: 600;
        line-height: 1.2;
        margin-bottom: 0.1rem;
        display: -webkit-box;
        -webkit-line-clamp: 1; /* Force single line with ellipsis */
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .album-card .card-artist {
        color: var(--text-secondary);
        font-size: 0.8rem;
        font-weight: 400;
        display: -webkit-box;
        -webkit-line-clamp: 1; /* Force single line with ellipsis */
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    /* Hide the genre badge to keep it perfectly clean */
    .album-card .card-genre {
        display: none;
    }

    /* ── FIX: Restore Material Icons for Streamlit UI ── */
    .material-symbols-rounded,
    .material-icons,
    [data-testid="stSidebarCollapseButton"] *,
    [data-testid="stExpandSidebarButton"] * {
        font-family: "Material Symbols Rounded", "Material Icons" !important;
    }
    /* ── Sleek Metric Cards ── */
    .scout-metric-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-bottom: 20px;
    }
    .scout-metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 16px;
        border-radius: 14px;
    }
    .scout-metric-label {
        color: #8e8e93;
        text-transform: uppercase;
        font-size: 0.65rem;
        letter-spacing: 0.5px;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .scout-metric-value {
        color: #ffffff;
        font-size: 1.5rem;
        font-weight: 700;
    }
    /* ── Sleek Tracklist ── */
    .scout-track-item {
        display: flex;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .scout-track-num {
        color: #8e8e93;
        width: 35px;
        font-size: 1.5rem;
        font-weight: 700;
    }
    .scout-track-name {
        color: #ffffff;
        font-size: 1.5rem;
        font-weight: 700;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    /* ── Dark Dialog Override ── */
    div[role="dialog"] {
        background-color: var(--bg-surface) !important;
        color: var(--text-primary) !important;
    }
    div[role="dialog"] button[aria-label="Close"] {
        color: var(--text-secondary) !important;
    }
    div[role="dialog"] button[aria-label="Close"]:hover {
        color: var(--text-primary) !important;
    }
    /* ── Rounded Artist Image in Dialog ── */
    div[role="dialog"] .artist-portrait img {
        border-radius: 14px !important;
        object-fit: cover;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# 3. SIDEBAR — Configuration
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<h2 style='margin-bottom:0.2rem; font-weight:700; "
        "letter-spacing:-0.02em;'>Configuration</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#a1a1a6; font-size:0.85rem; margin-top:0;'>"
        "Select your AI backend</p>",
        unsafe_allow_html=True,
    )

    ai_engine = st.radio(
        "AI Engine",
        options=[
            "Local",
            "Cloud",
        ],
        help="**Local**: Runs Gemma 3 270m entirely on your machine via Ollama.\n\n**Cloud**: Uses the NVIDIA NIM API to run Llama 3.1 70B.",
        index=0,
        label_visibility="visible",
    )

    nvidia_key = ""
    if ai_engine == "Local":
        # ── Check local model availability ──
        ollama_running = False
        model_ready = False
        try:
            installed = [m.model for m in ollama.list().models]
            ollama_running = True
            model_ready = any(
                "gemma3" in name and "270m-it-qat" in name
                for name in installed
            )
        except Exception:
            pass

        if not ollama_running:
            st.error("Ollama is not running.")
            if st.button("Start Ollama Service", use_container_width=True):
                with st.spinner("Starting Ollama background service..."):
                    try:
                        import subprocess
                        import os
                        import time
                        kwargs = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {}
                        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kwargs)
                        time.sleep(3)  # Wait a moment for the server to bind to the port
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to start Ollama automatically: {e}")
        elif model_ready:
            st.success("Local model ready")
        else:
            st.warning("Local model not found")
            if st.button("Download Local Model", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                status_text.text("Starting download…")

                try:
                    for chunk in ollama.pull("gemma3:270m-it-qat", stream=True):
                        completed = chunk.get("completed", 0)
                        total = chunk.get("total", 0)
                        if completed and total:
                            pct = completed / total
                            progress_bar.progress(min(pct, 1.0))
                            status_text.text(f"Downloading… {int(pct * 100)}%")

                    progress_bar.progress(1.0)
                    status_text.success("Download Complete! You can now generate pitches.")
                except Exception as e:
                    status_text.error(f"Download failed: {e}")
                
                # Small delay to let user see success/error before rerun if needed, or just rerun on success
                import time
                time.sleep(1)
                st.rerun()

    elif ai_engine == "Cloud":
        nvidia_key = st.text_input(
            "NVIDIA API Key",
            type="password",
            placeholder="nvapi-…",
        )

    st.markdown("### Outreach Settings")
    with st.expander("Pitch Customization", expanded=True):
        st.text_input("Agency Name", value="", key="agency_name")
        st.text_input("Scout Name", key="scout_name")
        st.selectbox(
            "Outreach Objective",
            options=["Live Booking & Tours", "Brand Partnerships", "Record Label Signing", "General Networking", "Other (Custom)"],
            key="outreach_objective_sel"
        )
        if st.session_state.get("outreach_objective_sel") == "Other (Custom)":
            st.text_input("Custom Objective", key="outreach_objective_custom")
            
        st.selectbox(
            "Pitch Tone",
            options=["Professional & Direct", "Casual & Enthusiastic", "Industry Standard", "Other (Custom)"],
            key="pitch_tone_sel"
        )
        if st.session_state.get("pitch_tone_sel") == "Other (Custom)":
            st.text_input("Custom Tone", key="pitch_tone_custom")

# ──────────────────────────────────────────────
# 4. MAIN CANVAS — Search
# ──────────────────────────────────────────────
st.markdown(
    "<h1 style='font-weight:700; font-size:2rem; "
    "letter-spacing:-0.03em; margin-bottom:0.25rem;'>"
    "Outreach Dashboard</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#a1a1a6; margin-top:0; font-size:1rem;'>"
    "Discover artists & genres, then craft personalized outreach.</p>",
    unsafe_allow_html=True,
)

if "search_input" not in st.session_state:
    st.session_state.search_input = ""

def clear_search():
    st.session_state.search_input = ""

search_col, clear_col = st.columns([15, 1])
with search_col:
    search_query = st.text_input(
        "Search",
        key="search_input",
        placeholder="Search artists or tracks...",
        label_visibility="collapsed",
    )

with clear_col:
    if st.session_state.search_input:
        st.button("✖", on_click=clear_search, use_container_width=False)

st.divider()


# ──────────────────────────────────────────────
# 5. DATA FETCHING
# ──────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_trending_albums(country_code="us", timeframe="All Time", genre_filter="All Genres"):
    """Fetch top 150 albums from the iTunes RSS feed, filtered by timeframe."""
    url = f"https://itunes.apple.com/{country_code}/rss/topalbums/limit=150/json"
    
    # Calculate cutoff date based on timeframe
    cutoff = None
    if timeframe == "Last 7 Days":
        cutoff = datetime.now() - timedelta(days=7)
    elif timeframe == "Last 30 Days":
        cutoff = datetime.now() - timedelta(days=30)
    elif timeframe == "Last 6 Months":
        cutoff = datetime.now() - timedelta(days=182)
    elif timeframe == "Last Year":
        cutoff = datetime.now() - timedelta(days=365)
    
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        entries = data.get("feed", {}).get("entry", [])
        albums = []
        for entry in entries:
            # Parse release date for filtering
            if cutoff is not None:
                raw_date = entry.get("im:releaseDate", {}).get("label", "")
                try:
                    release_dt = datetime.fromisoformat(raw_date.replace("Z", "+00:00")).replace(tzinfo=None)
                except (ValueError, AttributeError):
                    continue  # Skip entries with unparseable dates
                if release_dt < cutoff:
                    continue
            
            item_genre = entry.get("category", {}).get("attributes", {}).get("label", "—")
            
            if genre_filter != "All Genres" and genre_filter.lower() not in item_genre.lower():
                continue
            
            albums.append(
                {
                    "artist": entry.get("im:artist", {}).get("label", "Unknown"),
                    "album": entry.get("im:name", {}).get("label", "Unknown"),
                    "genre": entry.get("category", {}).get("attributes", {}).get("label", "—"),
                    "image": re.sub(r'\.png|\.webp', '.jpg', re.sub(r'\d+x\d+bb', '300x300bb', entry.get("im:image", [{}])[-1].get("label", ""))),
                }
            )
        return albums
    except Exception as e:
        st.error(f"Failed to fetch trending albums: {e}")
        return []


@st.cache_data(show_spinner=False, ttl=3600)
def get_artist_bio(artist_name):
    """Two-step Wikipedia lookup: Search API → Summary API."""
    _wiki_headers = {
        "User-Agent": "OutreachDashboard/1.0 (contact: dev@example.com)"
    }
    try:
        # Step 1: Search for the correct article title
        search_url = (
            f"https://en.wikipedia.org/w/api.php?action=query&list=search"
            f"&srsearch={urllib.parse.quote(artist_name)}&format=json&origin=*"
        )
        search_resp = requests.get(search_url, headers=_wiki_headers, timeout=5)
        if search_resp.status_code == 200:
            search_data = search_resp.json()
            results = search_data.get("query", {}).get("search", [])
            if results:
                # Step 2: Use the true title from the first result
                true_title = results[0]["title"].replace(" ", "_")
                summary_url = (
                    f"https://en.wikipedia.org/api/rest_v1/page/summary/"
                    f"{urllib.parse.quote(true_title)}"
                )
                resp = requests.get(summary_url, headers=_wiki_headers, timeout=5)
                if resp.status_code == 200:
                    extract = resp.json().get("extract", "")
                    if extract and "may refer to" not in extract.lower():
                        return extract
    except Exception:
        pass
    return "Biography currently unavailable."

@st.cache_data(show_spinner=False, ttl=3600)
def get_artist_insights(artist_name: str, album_name: str) -> dict:
    """Fetch and calculate analytics using chained Deezer API calls."""
    # Sanitize artist name to prevent "N/A" results for multi-artist strings
    clean_artist = re.split(r'(?i),|&|feat\.', artist_name)[0].strip()
    
    data = {
        "fans": "N/A", "albums": "N/A", "algo_radio": "No", 
        "heat_score": "N/A", "top_track": "N/A", "top_tracks": [], "preview_url": "", "preview_track_id": None, "brand_safety": "N/A", "deezer_link": "#",
        "label": "Independent", "related": [], "bpm": "N/A", "duration": "N/A", "release_date": "N/A"
    }
    try:
        
        # 1. First Call: Basic Artist Metadata
        search_url = f"https://api.deezer.com/search/artist?q={clean_artist}"
        resp = requests.get(search_url, timeout=5)
        if resp.status_code == 200 and resp.json().get("data"):
            artist = resp.json()["data"][0]
            artist_id = artist["id"]
            data["fans"] = f"{artist.get('nb_fan', 0):,}"
            data["albums"] = str(artist.get("nb_album", 0))
            data["algo_radio"] = "Yes" if artist.get("radio") else "No"
            data["deezer_link"] = artist.get("link", "#")
            data["artist_image"] = artist.get("picture_xl", artist.get("picture_medium", ""))

            # Fetch genres
            try:
                artist_resp = requests.get(f"https://api.deezer.com/artist/{artist_id}", timeout=3)
                if artist_resp.status_code == 200:
                    data["genres"] = [g["name"] for g in artist_resp.json().get("genres", {}).get("data", [])]
            except Exception:
                pass

            # 1.5. Call: Related Artists
            try:
                rel_url = f"https://api.deezer.com/artist/{artist_id}/related?limit=3"
                rel_resp = requests.get(rel_url, timeout=3)
                if rel_resp.status_code == 200 and rel_resp.json().get("data"):
                    data["related"] = [
                        {"name": r["name"], "picture": r.get("picture_medium", "")} 
                        for r in rel_resp.json()["data"]
                    ]
            except Exception:
                pass

            # 2. Second Call: Track Velocity (Heat)
            top_url = f"https://api.deezer.com/artist/{artist_id}/top?limit=3"
            top_resp = requests.get(top_url, timeout=5)
            if top_resp.status_code == 200 and top_resp.json().get("data"):
                tracks = top_resp.json()["data"]
                if tracks:
                    # 1. Grab Top 3 Track Names
                    data["top_tracks"] = [t["title"] for t in tracks[:3]]
                    # 2. Grab Audio Preview for the #1 Track (Fallback)
                    for t in tracks:
                        if t.get("preview"):
                            data["preview_url"] = t["preview"]
                            data["preview_track_title"] = t["title"]
                            data["preview_track_id"] = t.get("id")
                            break
                    # 3. Check for Explicit Lyrics across top tracks (Brand Safety)
                    is_explicit = any(t.get("explicit_lyrics", False) for t in tracks)
                    data["brand_safety"] = "Explicit" if is_explicit else "Clean / Radio-Safe"
                    
                    # 4. Third Call: Targeted Album Audio Preview
                    found_preview = False
                    
                    # Clean the album name for better matching (remove - Single, - EP, Remastered, etc.)
                    clean_album = re.sub(r'(?i)(\s*-\s*single|\s*-\s*ep|\(remastered.*?\)|\(deluxe.*?\))', '', album_name).strip()
                    
                    # Try Primary: Strict track search
                    strict_query = urllib.parse.quote(f"artist:\"{clean_artist}\" track:\"{clean_album}\"")
                    strict_url = f"https://api.deezer.com/search/track?q={strict_query}"
                    strict_resp = requests.get(strict_url, timeout=5)
                    if strict_resp.status_code == 200 and strict_resp.json().get("data"):
                        strict_tracks = strict_resp.json()["data"]
                        
                        # 1. Exact match with the text on the card AND artist
                        for t in strict_tracks:
                            t_title = t.get("title", "").lower()
                            t_artist = t.get("artist", {}).get("name", "").lower()
                            is_artist_match = clean_artist.lower() in t_artist or t_artist in clean_artist.lower()
                            if t.get("preview") and t_title == clean_album.lower() and is_artist_match:
                                data["preview_url"] = t["preview"]
                                data["preview_track_title"] = t["title"]
                                data["preview_track_id"] = t.get("id")
                                found_preview = True
                                try:
                                    alb_resp = requests.get(f"https://api.deezer.com/album/{t['album']['id']}", timeout=3)
                                    if alb_resp.status_code == 200:
                                        data["label"] = alb_resp.json().get("label", "Independent")
                                except: pass
                                break
                        
                        # 2. Partial match AND artist
                        if not found_preview:
                            for t in strict_tracks:
                                t_title = t.get("title", "").lower()
                                t_artist = t.get("artist", {}).get("name", "").lower()
                                is_artist_match = clean_artist.lower() in t_artist or t_artist in clean_artist.lower()
                                if t.get("preview") and clean_album.lower() in t_title and is_artist_match:
                                    data["preview_url"] = t["preview"]
                                    data["preview_track_title"] = t["title"]
                                    data["preview_track_id"] = t.get("id")
                                    found_preview = True
                                    try:
                                        alb_resp = requests.get(f"https://api.deezer.com/album/{t['album']['id']}", timeout=3)
                                        if alb_resp.status_code == 200:
                                            data["label"] = alb_resp.json().get("label", "Independent")
                                    except: pass
                                    break
                        
                        # 3. Any track with a preview
                        if not found_preview:
                            for t in strict_tracks:
                                if t.get("preview"):
                                    data["preview_url"] = t["preview"]
                                    data["preview_track_title"] = t["title"]
                                    data["preview_track_id"] = t.get("id")
                                    found_preview = True
                                    try:
                                        alb_resp = requests.get(f"https://api.deezer.com/album/{t['album']['id']}", timeout=3)
                                        if alb_resp.status_code == 200:
                                            data["label"] = alb_resp.json().get("label", "Independent")
                                    except: pass
                                    break
                    
                    # Try Secondary: Loose fuzzy search
                    if not found_preview:
                        loose_query = urllib.parse.quote(f"{clean_artist} {clean_album}")
                        loose_url = f"https://api.deezer.com/search?q={loose_query}"
                        loose_resp = requests.get(loose_url, timeout=5)
                        if loose_resp.status_code == 200 and loose_resp.json().get("data"):
                            loose_tracks = loose_resp.json()["data"]
                            
                            # 1. Exact match AND artist
                            for t in loose_tracks:
                                t_title = t.get("title", "").lower()
                                t_artist = t.get("artist", {}).get("name", "").lower()
                                is_artist_match = clean_artist.lower() in t_artist or t_artist in clean_artist.lower()
                                if t.get("preview") and t_title == clean_album.lower() and is_artist_match:
                                    data["preview_url"] = t["preview"]
                                    data["preview_track_title"] = t["title"]
                                    data["preview_track_id"] = t.get("id")
                                    found_preview = True
                                    try:
                                        alb_resp = requests.get(f"https://api.deezer.com/album/{t['album']['id']}", timeout=3)
                                        if alb_resp.status_code == 200:
                                            data["label"] = alb_resp.json().get("label", "Independent")
                                    except: pass
                                    break
                            
                            # 2. Partial match AND artist
                            if not found_preview:
                                for t in loose_tracks:
                                    t_title = t.get("title", "").lower()
                                    t_artist = t.get("artist", {}).get("name", "").lower()
                                    is_artist_match = clean_artist.lower() in t_artist or t_artist in clean_artist.lower()
                                    if t.get("preview") and clean_album.lower() in t_title and is_artist_match:
                                        data["preview_url"] = t["preview"]
                                        data["preview_track_title"] = t["title"]
                                        data["preview_track_id"] = t.get("id")
                                        found_preview = True
                                        try:
                                            alb_resp = requests.get(f"https://api.deezer.com/album/{t['album']['id']}", timeout=3)
                                            if alb_resp.status_code == 200:
                                                data["label"] = alb_resp.json().get("label", "Independent")
                                        except: pass
                                        break
                                        
                            # 3. Any track with a preview
                            if not found_preview:
                                for t in loose_tracks:
                                    if t.get("preview"):
                                        data["preview_url"] = t["preview"]
                                        data["preview_track_title"] = t["title"]
                                        data["preview_track_id"] = t.get("id")
                                        found_preview = True
                                        try:
                                            alb_resp = requests.get(f"https://api.deezer.com/album/{t['album']['id']}", timeout=3)
                                            if alb_resp.status_code == 200:
                                                data["label"] = alb_resp.json().get("label", "Independent")
                                        except: pass
                                        break
                    
                    data["top_track"] = tracks[0]["title"]
                    # Calculate Heat Score based on Deezer track ranks
                    avg_rank = sum(t.get("rank", 0) for t in tracks) / len(tracks)
                    heat = min(100, max(1, int((avg_rank / 800000) * 100)))
                    data["heat_score"] = f"{heat}/100"

                    # 5. Track DNA: Deep-dive into the matched track
                    if data.get("preview_track_id"):
                        try:
                            dna_resp = requests.get(f"https://api.deezer.com/track/{data['preview_track_id']}", timeout=3)
                            if dna_resp.status_code == 200:
                                dna = dna_resp.json()
                                data["bpm"] = dna.get("bpm", "N/A") or "N/A"
                                data["release_date"] = dna.get("release_date", "N/A")
                                dur = dna.get("duration", 0)
                                data["duration"] = f"{dur // 60}:{dur % 60:02d}" if dur else "N/A"
                        except Exception:
                            pass
    except Exception:
        pass
    return data

def search_itunes(query: str):
    """Search the iTunes API for albums matching *query*."""
    url = "https://itunes.apple.com/search"
    params = {"term": query, "entity": "album", "limit": 100}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        albums = []
        for item in results:
            albums.append(
                {
                    "artist": item.get("artistName", "Unknown"),
                    "album": item.get("collectionName", "Unknown"),
                    "genre": item.get("primaryGenreName", "—"),
                    "image": re.sub(r'\d+x\d+bb', '300x300bb', item.get("artworkUrl100", "")),
                }
            )
        return albums
    except Exception as e:
        st.error(f"Search failed: {e}")
        return []


# ──────────────────────────────────────────────
# 6. AI PITCH GENERATION
# ──────────────────────────────────────────────
def generate_pitch(
    artist: str,
    album: str,
    genre: str,
    engine_choice: str,
    agency: str = "",
    scout: str = "",
    objective: str = "Live Booking & Tours",
    tone: str = "Professional & Direct",
    api_key: str = "",
) -> str:
    """Generate a cold-email pitch using the selected AI engine."""
    # 1. Calculate Release "Freshness" (Pre-Processing)
    insights = get_artist_insights(artist, album)
    release_date_str = insights.get("release_date", "N/A")
    days_since_release = "unknown"
    release_context = "Music"
    
    if release_date_str != "N/A":
        try:
            rel_date = datetime.strptime(release_date_str, "%Y-%m-%d")
            delta = (datetime.now() - rel_date).days
            days_since_release = str(max(0, delta))
            if delta < 14:
                release_context = "Brand New Drop"
            elif delta < 90:
                release_context = "Recent Release"
            elif delta > 365:
                release_context = "Catalogue Track"
            else:
                release_context = "Recent Release"
        except Exception:
            pass

    # 2. Gather the Context Payload
    artist_name = artist
    album_name = album
    genres = ", ".join(insights.get("genres", [genre])) if insights.get("genres") else genre
    heat_score = insights.get("heat_score", "N/A").split("/")[0]
    agency_name = agency if agency else "a top talent agency"
    scout_name = scout if scout else f"{agency_name} A&R Team"
    formatted_date = release_date_str if release_date_str != "N/A" else "recently"
    
    # 3. Construct the Advanced LLM Prompt Template
    prompt = f"""
You are {scout_name}, an elite A&R Scout at {agency_name}.
Write a highly personalized, cold outreach email to the artist {artist_name}.

[ARTIST CONTEXT]
- Targeted Track/Album: {album_name}
- Exact Release Date: {formatted_date}
- Release Timeline: It was released {days_since_release} days ago (Categorized as: {release_context}).
- Sonic Profile: {genres}
- Current Momentum Score: {heat_score}/100

[OUTREACH OBJECTIVE]
The goal of this email is to discuss: {objective}
The tone of the email MUST be: {tone}

[STRICT RULES - READ CAREFULLY]
1. DO NOT use the phrase "recent track", "latest track", or "new song". Instead, explicitly reference the {release_context} timeline (e.g., "noticed your brand new drop", "listening to your catalogue classic", "loved the record you put out last month").
2. Specifically name their genre ({genres}) to prove we actually listened to them.
3. Keep it under 150 words. A&R scouts are busy, and artists don't read long emails.
4. Do not use generic placeholders like [Insert Link].
5. End the email by asking a low-friction question related to the {objective}.
6. YOU MUST NOT generate any brackets, placeholders, or fill-in-the-blank text (e.g., NO "[Date]", NO "[Insert Link]", NO "[Name]"). Use ONLY the specific facts provided in the context above to write a complete, ready-to-send email.

Draft the email now:
"""

    # ── Local: Gemma via Ollama ──
    if engine_choice == "Local":
        # Verify the model is downloaded
        try:
            installed = [m.model for m in ollama.list().models]
            model_ready = any(
                "gemma3" in name and "270m-it-qat" in name
                for name in installed
            )
        except Exception:
            model_ready = False

        if not model_ready:
            return "⚠️ Please download the local model from the sidebar first."

        response = ollama.chat(
            model="gemma3:270m-it-qat",
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"]

    # ── Cloud: NVIDIA NIM ──
    if not api_key:
        return "⚠️ Please enter your NVIDIA API key in the sidebar."

    client = openai.OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key,
    )
    completion = client.chat.completions.create(
        model="meta/llama-3.1-70b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=512,
    )
    return completion.choices[0].message.content


def _build_eml(artist: str, album: str, body: str, agency: str = "Agency", scout: str = "Scout") -> str:
    """Format the pitch as an RFC-822 .eml string."""
    safe = re.sub(r"[^a-z0-9]", "", artist.lower())
    msg = EmailMessage()
    agency_display = agency if agency else "Agency"
    scout_display = scout if scout else "scouting"
    msg["Subject"] = f"{agency_display} — Let's talk about '{album}'"
    msg["To"] = f"management@{safe}.com"
    safe_scout = re.sub(r"[^a-z0-9]", "", scout_display.lower())
    safe_agency = re.sub(r"[^a-z0-9]", "", agency_display.lower())
    if not safe_scout: safe_scout = "scout"
    if not safe_agency: safe_agency = "agency"
    msg["From"] = f"{safe_scout}@{safe_agency}.com"
    msg.set_content(body)
    return msg.as_string()


# ──────────────────────────────────────────────
# 7. DISPLAY LOGIC
# ──────────────────────────────────────────────
@st.dialog("A&R Scout Insights", width="large")
def show_insights(artist_name: str, album_name: str, genre: str = None, album_image: str = None):
    with st.spinner("Analyzing cross-platform velocity..."):
        insights = get_artist_insights(artist_name, album_name)
        # Fetch bio separately so it's never trapped in the insights cache
        clean_artist = re.split(r'(?i),|&|feat\.', artist_name)[0].strip()
        bio_text = get_artist_bio(clean_artist)
        
    # Format Label
    label = insights.get('label', 'Independent')
    is_major = any(m in label.lower() for m in ['universal', 'sony', 'warner'])
    label_color = "#fa586a" if is_major else "#8e8e93"
    
    # Two-column layout: Text (left) + Artist Image (right)
    text_col, img_col = st.columns([3, 1])
    
    with text_col:
        # Artist Header
        st.markdown(f"<h2 style='color: #ffffff; margin-bottom: 0px; display: flex; align-items: center; gap: 10px;'>{artist_name} <span style='font-size: 1rem; font-weight: 500; color: {label_color}; margin-top: 6px;'>({label})</span></h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #d1d1d6; margin-bottom: 20px;'>Artist Insights</p>", unsafe_allow_html=True)
        if bio_text:
            st.markdown(f"""
                <div style="
                    background: rgba(255, 255, 255, 0.03);
                    padding: 12px;
                    border-radius: 10px;
                    margin-bottom: 18px;
                ">
                    <p style="
                        color: #d1d1d6;
                        font-size: 0.85rem;
                        font-style: italic;
                        line-height: 1.55;
                        margin: 0;
                    ">{bio_text}</p>
                </div>
            """, unsafe_allow_html=True)
            
        genres_to_show = insights.get("genres", [])
        if genre and genre not in genres_to_show:
            genres_to_show.insert(0, genre)
            
        if genres_to_show:
            pills = "".join([f"<span style='background: rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 15px; font-size: 0.75rem; display: inline-block; margin-right: 5px; margin-bottom: 5px; color: #ffffff;'>{g}</span>" for g in genres_to_show])
            st.markdown(f"<div style='margin-bottom: 15px;'>{pills}</div>", unsafe_allow_html=True)

        if st.button("Draft AI Pitch", type="primary", use_container_width=True):
            st.session_state.active_pitch = f"pitch_{artist_name}_{album_name}"
            st.session_state.pitch_text = None
            st.success("Preparing AI workspace...")
            time.sleep(0.6)
            st.rerun()
    
    with img_col:
        if insights.get("artist_image"):
            st.markdown('<div class="artist-portrait">', unsafe_allow_html=True)
            st.image(insights["artist_image"], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Metric Grid (Custom HTML)
    st.markdown(f"""
        <div class="scout-metric-container">
            <div class="scout-metric-card">
                <div class="scout-metric-label">Current Heat</div>
                <div class="scout-metric-value">{insights['heat_score']}</div>
            </div>
            <div class="scout-metric-card">
                <div class="scout-metric-label">Dedicated Fans</div>
                <div class="scout-metric-value">{insights['fans']}</div>
            </div>
            <div class="scout-metric-card">
                <div class="scout-metric-label">Catalog</div>
                <div class="scout-metric-value">{insights['albums']}</div>
            </div>
            <div class="scout-metric-card">
                <div class="scout-metric-label">Safety</div>
                <div class="scout-metric-value">{insights['brand_safety'].split(' ')[0]}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Top Tracks & Chosen Album Image
    tt_col, alb_img_col = st.columns([3, 1])
    with tt_col:
        st.markdown("<p style='color: #ffffff; font-weight: 600; margin-bottom: 10px;'>Top Tracks</p>", unsafe_allow_html=True)
        for i, track in enumerate(insights.get("top_tracks", [])):
            st.markdown(f"""
                <div class="scout-track-item">
                    <div class="scout-track-num">{i+1}</div>
                    <div class="scout-track-name">{track}</div>
                </div>
            """, unsafe_allow_html=True)
            
    with alb_img_col:
        if album_image:
            st.markdown(f"<p style='color: #ffffff; font-weight: 600; margin-bottom: 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{album_name}</p>", unsafe_allow_html=True)
            st.markdown(f"""
                <img src="{album_image}" style="width: 100%; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); object-fit: cover;">
            """, unsafe_allow_html=True)
    
    # Track DNA
    if insights.get("preview_track_id"):
        st.markdown("<p style='color: #ffffff; font-weight: 600; margin-top: 20px; margin-bottom: 10px;'>Track DNA</p>", unsafe_allow_html=True)
        t1, t2, t3 = st.columns(3)
        with t1:
            st.markdown(f"""
                <div class="scout-metric-card">
                    <div class="scout-metric-label">BPM</div>
                    <div class="scout-metric-value">{insights.get('bpm', 'N/A')}</div>
                </div>
            """, unsafe_allow_html=True)
        with t2:
            st.markdown(f"""
                <div class="scout-metric-card">
                    <div class="scout-metric-label">Duration</div>
                    <div class="scout-metric-value">{insights.get('duration', 'N/A')}</div>
                </div>
            """, unsafe_allow_html=True)
        with t3:
            st.markdown(f"""
                <div class="scout-metric-card">
                    <div class="scout-metric-label">Release Date</div>
                    <div class="scout-metric-value">{insights.get('release_date', 'N/A')}</div>
                </div>
            """, unsafe_allow_html=True)

    # Audio Player
    if insights.get("preview_url"):
        st.markdown(f"<p style='color: #8e8e93; font-size: 0.8rem; margin-top: 20px;'>Previewing: {album_name}</p>", unsafe_allow_html=True)
        st.audio(insights["preview_url"])

    # Related Artists (Scouting Discovery)
    if insights.get("related"):
        st.markdown("<p style='color: #ffffff; font-weight: 600; margin-top: 20px; margin-bottom: 10px;'>🔍 Scouting Discovery</p>", unsafe_allow_html=True)
        r_cols = st.columns(len(insights["related"]))
        for i, rel in enumerate(insights["related"]):
            with r_cols[i]:
                st.markdown(f"""
                    <div style="text-align: center; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 14px; padding: 12px;">
                        <img src="{rel['picture']}" style="width: 60px; height: 60px; border-radius: 50%; margin-bottom: 8px; object-fit: cover;">
                        <div style="color: #ffffff; font-size: 0.85rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{rel['name']}</div>
                    </div>
                """, unsafe_allow_html=True)

    # Clean Footer
    st.markdown(f"<div style='text-align: right; margin-top: 20px;'><a href='{insights['deezer_link']}' target='_blank' style='color: #fa243c; text-decoration: none; font-size: 0.9rem; font-weight: 500;'>Full Deezer Profile →</a></div>", unsafe_allow_html=True)


if search_query.strip():
    st.markdown(
        f"<h3 style='font-weight:600; letter-spacing:-0.02em; margin-bottom:0.6rem;'>🔎 Search Results</h3>",
        unsafe_allow_html=True,
    )
    albums = search_itunes(search_query.strip())
else:
    c1, cg, c2, c3 = st.columns([4, 1.5, 1, 1])
    with c1:
        st.markdown(
            f"<h3 style='font-weight:600; letter-spacing:-0.02em; margin-bottom:0.6rem;'>Trending Releases</h3>",
            unsafe_allow_html=True,
        )
    with cg:
        with st.container():
            selected_genre = st.selectbox(
                "Genre", 
                options=["All Genres", "Pop", "Hip-Hop/Rap", "R&B/Soul", "Electronic", "Dance", "Country", "Rock", "Alternative", "Singer/Songwriter", "K-Pop", "Latin", "Jazz", "Classical"], 
                index=0, 
                label_visibility="collapsed"
            )
    with c2:
        with st.container():
            selected_country = st.selectbox("Select Market", options=list(COUNTRIES.keys()), index=0, label_visibility="collapsed")
    with c3:
        with st.container():
            selected_timeframe = st.selectbox("Timeframe", options=["All Time", "Last 7 Days", "Last 30 Days", "Last 6 Months", "Last Year"], index=0, label_visibility="collapsed")
    country_code = COUNTRIES[selected_country]
    albums = get_trending_albums(country_code, selected_timeframe, selected_genre)

# Session-state key for the currently-selected pitch
if "active_pitch" not in st.session_state:
    st.session_state.active_pitch = None
if "pitch_text" not in st.session_state:
    st.session_state.pitch_text = None

if not albums:
    st.markdown(
        "<p style='color:#a1a1a6;'>No results found.</p>",
        unsafe_allow_html=True,
    )
else:
    COLS = 6
    # Only generate a new animation name if the album list has changed
    current_albums_str = str(albums)
    if "albums_str" not in st.session_state or st.session_state.albums_str != current_albums_str:
        st.session_state.anim_id = uuid.uuid4().hex[:8]
        st.session_state.albums_str = current_albums_str

    anim_id = st.session_state.anim_id
    st.markdown(
        f"""
        <style>
            @keyframes slideUp_{anim_id} {{
                from {{ opacity: 0; transform: translateY(24px); }}
                to   {{ opacity: 1; transform: translateY(0); }}
            }}
            @keyframes fadeImg_{anim_id} {{
                from {{ opacity: 0; }}
                to   {{ opacity: 1; }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    card_index = 0
    for row_start in range(0, len(albums), COLS):
        row_items = albums[row_start : row_start + COLS]
        cols = st.columns(COLS)
        for col, item in zip(cols, row_items):
            card_key = f"pitch_{item['artist']}_{item['album']}"
            delay = card_index * 0.04  # stagger each card by 40ms

            with col:
                st.markdown(
                    f"""
                    <div class="album-card" style="
                        opacity: 0;
                        animation: slideUp_{anim_id} 0.45s cubic-bezier(0.16, 1, 0.3, 1) {delay:.2f}s forwards;
                    ">
                        <img src="{item.get('image', '')}" alt="Cover" style="opacity: 0; animation: fadeImg_{anim_id} 0.4s ease-in forwards {delay + 0.15:.2f}s;">
                        <div class="card-album">{item["album"]}</div>
                        <div class="card-artist">{item["artist"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                # Button Layout
                b_col1, b_col2 = st.columns([1, 1])
                with b_col1:
                    if st.button("Pitch", key=card_key, use_container_width=True):
                        st.session_state.active_pitch = card_key
                        st.session_state.pitch_text = None
                with b_col2:
                    if st.button("Data", key=f"ins_{card_key}", use_container_width=True):
                        show_insights(item["artist"], item["album"], item["genre"], item.get("image"))
                card_index += 1

        # ── After each row, check if any card in this row was clicked ──
        for item in row_items:
            card_key = f"pitch_{item['artist']}_{item['album']}"
            if st.session_state.active_pitch == card_key:
                # Smooth auto-scroll to the active pitch workspace
                st.markdown(f"<div id='scroll_{card_key}'></div>", unsafe_allow_html=True)
                components.html(
                    f"""
                    <script>
                        setTimeout(function() {{
                            const target = window.parent.document.getElementById('scroll_{card_key}');
                            if (target) {{
                                target.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                            }}
                        }}, 150);
                    </script>
                    """,
                    height=0,
                )
                
                with st.expander(
                    f"Pitch for **{item['artist']}** — *{item['album']}*",
                    expanded=True,
                ):
                    # Generate if we haven't yet
                    if st.session_state.pitch_text is None:
                        with st.spinner("Generating pitch…"):
                            st.session_state.pitch_text = generate_pitch(
                                artist=item["artist"],
                                album=item["album"],
                                genre=item["genre"],
                                engine_choice=ai_engine,
                                agency=st.session_state.get("agency_name", ""),
                                scout=st.session_state.get("scout_name", ""),
                                objective=st.session_state.get("outreach_objective_custom") if st.session_state.get("outreach_objective_sel") == "Other (Custom)" else st.session_state.get("outreach_objective_sel", "Live Booking & Tours"),
                                tone=st.session_state.get("pitch_tone_custom") if st.session_state.get("pitch_tone_sel") == "Other (Custom)" else st.session_state.get("pitch_tone_sel", "Professional & Direct"),
                                api_key=nvidia_key,
                            )

                    st.markdown(st.session_state.pitch_text)

                    # ── .eml download ──
                    eml_str = _build_eml(
                        item["artist"], item["album"], st.session_state.pitch_text,
                        st.session_state.get("agency_name", ""),
                        st.session_state.get("scout_name", "")
                    )
                    safe_name = re.sub(r"[^a-z0-9]", "_", item["artist"].lower())
                    st.download_button(
                        "📥 Download .eml for Outlook",
                        data=eml_str,
                        file_name=f"pitch_{safe_name}.eml",
                        mime="message/rfc822",
                        key=f"dl_{card_key}",
                        use_container_width=True,
                    )
