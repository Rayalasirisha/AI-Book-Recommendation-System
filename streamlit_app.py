"""
Book Recommendation — An Immersive Book Recommendation Experience
Powered by Tuned SVD (scikit-surprise) and Content Vibe Search
"""

import os
import pickle
import random
import pandas as pd
import numpy as np
import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Book Recommendation – AI Book Exploration",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Compatibility helper — works on ALL Streamlit versions ────────────────────
def _html(body, sidebar=False):
    """Render raw HTML via st.markdown with unsafe_allow_html=True."""
    target = st.sidebar if sidebar else st
    target.markdown(body, unsafe_allow_html=True)

# ── Custom Emerald & Gold CSS ────────────────────────────────────────────────
_html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,400&display=swap');

:root {
  --bg-primary:     #041c15;
  --bg-secondary:   #020d0a;
  --bg-glass:       rgba(9, 58, 47, 0.45);
  --border-gold:    rgba(226, 201, 116, 0.15);
  --border-hover:   rgba(226, 201, 116, 0.5);
  --gold:           #e2c974;
  --gold-glow:      rgba(226, 201, 116, 0.35);
  --text-primary:   #f1f5f9;
  --text-sage:      #8ba89f;
  --font-sans:     'Outfit', sans-serif;
  --font-serif:    'Playfair Display', serif;
}

html, body, [data-testid="stAppViewContainer"] {
  background-color: var(--bg-primary) !important;
  font-family: var(--font-sans) !important;
  color: var(--text-primary) !important;
}
[data-testid="stSidebar"] {
  background-color: var(--bg-secondary) !important;
  border-right: 1px solid var(--border-gold) !important;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"], footer, #MainMenu, [data-testid="stDecoration"] { display: none !important; }

.block-container {
  padding-top: 2rem !important;
  padding-bottom: 2rem !important;
  max-width: 1200px !important;
}

/* Target BaseWeb wrapper to prevent double focus ring */
div[data-baseweb="input"] {
  background: rgba(2, 13, 10, 0.6) !important;
  border: 1px solid var(--border-gold) !important;
  border-radius: 12px !important;
  transition: all 0.2s ease !important;
}
div[data-baseweb="input"]:focus-within {
  border-color: var(--gold) !important;
  box-shadow: 0 0 10px var(--gold-glow) !important;
  outline: none !important;
}
div[data-baseweb="input"] input {
  background: transparent !important;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
  color: var(--text-primary) !important;
  font-family: var(--font-sans) !important;
}
/* Also style BaseWeb select dropdowns */
div[data-baseweb="select"] > div {
  background: rgba(2, 13, 10, 0.6) !important;
  border: 1px solid var(--border-gold) !important;
  border-radius: 12px !important;
  transition: all 0.2s ease !important;
  color: var(--text-primary) !important;
}
div[data-baseweb="select"] > div:focus-within {
  border-color: var(--gold) !important;
  box-shadow: 0 0 10px var(--gold-glow) !important;
}

[data-testid="stSlider"] > div > div > div {
  background: linear-gradient(to right, var(--gold), #a88b39) !important;
}
[data-testid="stSlider"] [role="slider"] {
  background: var(--gold) !important;
  border: 2px solid var(--text-primary) !important;
  box-shadow: 0 0 8px var(--gold-glow) !important;
}

/* Style native Streamlit containers (border=True) to match oasis-panel */
div[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--bg-glass) !important;
  border: 1px solid var(--border-gold) !important;
  border-radius: 20px !important;
  padding: 8px 16px !important;
}

.stButton > button {
  background: linear-gradient(135deg, var(--gold), #b89d42) !important;
  color: var(--bg-secondary) !important;
  border: none !important;
  border-radius: 12px !important;
  font-weight: 700 !important;
  font-family: var(--font-sans) !important;
  font-size: 0.95rem !important;
  padding: 10px 20px !important;
  cursor: pointer !important;
  box-shadow: 0 4px 14px var(--gold-glow) !important;
  transition: all 0.25s ease !important;
  border: 1px solid rgba(226, 201, 116, 0.4) !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(226, 201, 116, 0.6) !important;
  color: var(--bg-secondary) !important;
}

[data-testid="stAlert"] {
  border-radius: 12px !important;
  background-color: var(--bg-secondary) !important;
  border: 1px solid var(--border-gold) !important;
  color: var(--text-primary) !important;
}

.oasis-hero {
  background: radial-gradient(circle at 80% 20%, rgba(9, 58, 47, 0.8) 0%, var(--bg-secondary) 100%);
  border-radius: 24px;
  padding: 50px 40px;
  margin-bottom: 32px;
  border: 1px solid var(--border-gold);
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
  position: relative;
}
.oasis-title {
  font-family: var(--font-serif);
  font-size: clamp(2rem, 4vw, 3.2rem);
  font-weight: 700;
  line-height: 1.15;
  margin-bottom: 12px;
  color: var(--text-primary);
}
.oasis-gold-text {
  color: var(--gold);
  text-shadow: 0 0 12px rgba(226, 201, 116, 0.25);
}
.oasis-subtitle {
  font-size: 1rem;
  color: var(--text-sage);
  max-width: 580px;
  line-height: 1.6;
}

.book-oasis-card {
  background: rgba(9, 58, 47, 0.3);
  border: 1px solid var(--border-gold);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  margin-bottom: 8px;
}
.book-oasis-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 0 25px rgba(226, 201, 116, 0.2);
  border-color: var(--gold);
}
.cover-img {
  width: 100%;
  aspect-ratio: 2/3;
  object-fit: cover;
  background: #020d0a;
}
.cover-placeholder {
  width: 100%;
  aspect-ratio: 2/3;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  background: linear-gradient(135deg, #093a2f, #020d0a);
}
.card-info {
  padding: 12px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.card-title {
  font-size: 0.85rem;
  font-weight: 700;
  line-height: 1.25;
  margin-bottom: 4px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  color: var(--text-primary);
  height: 34px;
}
.card-author {
  font-size: 0.74rem;
  color: var(--text-sage);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 8px;
}
.card-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 700;
  background: rgba(226, 201, 116, 0.1);
  border: 1px solid rgba(226, 201, 116, 0.3);
  color: var(--gold);
}

.oasis-panel {
  background: var(--bg-glass);
  border: 1px solid var(--border-gold);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 24px;
}
.oasis-section-title {
  font-family: var(--font-serif);
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}
.oasis-section-sub {
  font-size: 0.92rem;
  color: var(--text-sage);
  margin-bottom: 20px;
}

.stat-banner {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}
.stat-box {
  background: rgba(2, 13, 10, 0.5);
  border: 1px solid var(--border-gold);
  padding: 16px;
  border-radius: 12px;
  text-align: center;
}
.stat-label {
  font-size: 0.75rem;
  color: var(--text-sage);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.stat-val {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--gold);
  margin-top: 4px;
}

.comparison-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}
.comparison-table th {
  text-align: left;
  padding: 10px 14px;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-sage);
  border-bottom: 1px solid var(--border-gold);
}
.comparison-table td {
  padding: 12px 14px;
  border-bottom: 1px solid rgba(226, 201, 116, 0.05);
  color: var(--text-primary);
}
.best-model-row td {
  color: var(--gold);
  font-weight: 700;
  background: rgba(226, 201, 116, 0.08) !important;
}

.tarot-deck {
  display: flex;
  justify-content: center;
  margin: 30px 0;
}
.tarot-card {
  width: 260px;
  height: 380px;
  background: linear-gradient(145deg, #093a2f 0%, #020d0a 100%);
  border: 2px solid var(--gold);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(226, 201, 116, 0.15);
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  text-align: center;
  transition: all 0.3s ease;
}
.tarot-card:hover {
  transform: scale(1.03);
  box-shadow: 0 15px 40px rgba(226, 201, 116, 0.3);
}
.tarot-decor {
  border: 1px solid rgba(226, 201, 116, 0.3);
  width: 100%;
  height: 100%;
  border-radius: 10px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.tarot-icon { font-size: 2.2rem; margin-bottom: 10px; }

.bm-divider { border: none; border-top: 1px solid rgba(226,201,116,0.1); margin: 40px 0; }
</style>
""")


# ── Helper: Card generator ────────────────────────────────────────────────────
def get_card_html(title, author, img_url, badge_label):
    t = title[:50] + ("…" if len(title) > 50 else "")
    a = author[:35] + ("…" if len(author) > 35 else "")
    if img_url and img_url != "Unknown" and img_url.strip():
        cover = f'<img class="cover-img" src="{img_url}" alt="{t}" loading="lazy" onerror="this.outerHTML=\'<div class=cover-placeholder>📖</div>\'">'
    else:
        cover = '<div class="cover-placeholder">📖</div>'
    return f"""<div class="book-oasis-card">
  {cover}
  <div class="card-info">
    <div><div class="card-title" title="{title}">{t}</div><div class="card-author" title="{author}">{a}</div></div>
    <span class="card-badge">{badge_label}</span>
  </div>
</div>"""


# ── Cache datasets ────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_data():
    base = os.path.dirname(__file__)
    pkl_files = {
        "model":   os.path.join(base, "best_svd_model.pkl"),
        "books":   os.path.join(base, "books.pkl"),
        "ratings": os.path.join(base, "ratings.pkl"),
        "users":   os.path.join(base, "users.pkl"),
    }
    if all(os.path.exists(p) for p in pkl_files.values()):
        with open(pkl_files["model"],   "rb") as f: model   = pickle.load(f)
        with open(pkl_files["books"],   "rb") as f: books   = pickle.load(f)
        with open(pkl_files["ratings"], "rb") as f: ratings = pickle.load(f)
        with open(pkl_files["users"],   "rb") as f: users   = pickle.load(f)
    else:
        model, books, ratings, users = _train_from_raw(base, pkl_files)
    return model, books, ratings, users


def _train_from_raw(base, pkl_files):
    from surprise import SVD, Dataset, Reader
    from surprise.model_selection import train_test_split
    users   = pd.read_csv(os.path.join(base, "Users.csv"),   encoding="latin-1")
    books   = pd.read_csv(os.path.join(base, "Books.csv"),   encoding="latin-1", low_memory=False)
    ratings = pd.read_csv(os.path.join(base, "Ratings.csv"), encoding="latin-1")
    ratings = ratings.sample(n=25_000, random_state=42)
    users["Age"] = users["Age"].fillna(users["Age"].median())
    users = users[(users["Age"] >= 5) & (users["Age"] <= 100)]
    reader = Reader(rating_scale=(1, 10))
    data   = Dataset.load_from_df(ratings[["User-ID", "ISBN", "Book-Rating"]], reader)
    trainset, _ = train_test_split(data, test_size=0.2, random_state=42)
    model = SVD(n_factors=50, n_epochs=50, lr_all=0.005, reg_all=0.05)
    model.fit(trainset)
    for name, path in pkl_files.items():
        obj = {"model": model, "books": books, "ratings": ratings, "users": users}[name]
        with open(path, "wb") as f:
            pickle.dump(obj, f)
    return model, books, ratings, users


@st.cache_data(show_spinner=False)
def get_popular_list(_books, _ratings, n=30):
    merged = _ratings[_ratings["Book-Rating"] > 0].merge(
        _books[["ISBN", "Book-Title", "Book-Author", "Publisher", "Image-URL-L"]],
        on="ISBN", how="inner"
    )
    pop = (
        merged.groupby("Book-Title")
        .agg(avg_rating=("Book-Rating", "mean"), count=("Book-Rating", "count"),
             isbn=("ISBN", "first"), author=("Book-Author", "first"), image=("Image-URL-L", "first"))
        .reset_index()
    )
    return pop[pop["count"] >= 10].sort_values("avg_rating", ascending=False).head(n)


@st.cache_data(show_spinner=False)
def get_user_options(_ratings):
    return _ratings["User-ID"].unique()[:500].tolist()


def predict_svd(user_id, model, books, ratings, top_n=10):
    try:
        # Get raw item IDs (ISBNs) that are in the training set of the model
        known_isbns = [model.trainset.to_raw_iid(iid) for iid in model.trainset.all_items()]
    except Exception:
        # Fallback if trainset is not available or differs
        known_isbns = ratings["ISBN"].unique().tolist()
        
    rated = ratings.loc[ratings["User-ID"] == user_id, "ISBN"].unique()
    
    # Filter candidates to books that are known to the SVD model and not already rated by this user
    candidates = books[books["ISBN"].isin(known_isbns) & ~books["ISBN"].isin(rated)].copy()
    if candidates.empty:
        # Fallback: if no candidates in training set, use books from ratings to ensure popularity/bias matching
        candidates = books[books["ISBN"].isin(ratings["ISBN"].unique()) & ~books["ISBN"].isin(rated)].copy()
        if candidates.empty:
            return pd.DataFrame()
            
    preds = [(isbn, model.predict(user_id, isbn).est) for isbn in candidates["ISBN"].unique()]
    preds.sort(key=lambda x: x[1], reverse=True)
    
    # --- Diversity and Uniqueness Sampling ---
    # To prevent identical recommendations for different users (especially cold-start users),
    # we take a larger pool of the top-predicted books and sample from them deterministically 
    # using the user_id as a seed. This ensures distinct, stable recommendations for each user.
    pool_size = max(top_n * 3, 30)
    top_candidates = preds[:pool_size]
    
    if len(top_candidates) > top_n:
        rng = np.random.default_rng(user_id)
        selected_indices = rng.choice(len(top_candidates), size=top_n, replace=False)
        selected_indices.sort()  # Maintain ordering by prediction score
        selected_preds = [top_candidates[i] for i in selected_indices]
    else:
        selected_preds = top_candidates
        
    res = pd.DataFrame(selected_preds, columns=["ISBN", "Predicted_Rating"])
    res = res.merge(books[["ISBN", "Book-Title", "Book-Author", "Publisher", "Image-URL-L"]], on="ISBN", how="left").fillna("Unknown")
    return res


# ── Mood presets ──────────────────────────────────────────────────────────────
mood_presets = {
    "Cozy & Warming 🏡": ["secret", "tree", "garden", "summer", "life", "home", "cozy", "house", "light"],
    "Dark & Thrilling 🔍": ["da vinci", "code", "murder", "death", "silent", "shadow", "key", "night", "dark"],
    "Epic & Fantastical 🐉": ["hobbit", "lord", "ring", "wizard", "potter", "harry", "dragon", "star", "chronicles"],
    "Thought-Provoking 🧠": ["world", "time", "history", "mind", "science", "brief", "philosophy", "lost"],
}

# ── Session state ─────────────────────────────────────────────────────────────
if "reading_list" not in st.session_state:
    st.session_state.reading_list = []
if "oracle_results" not in st.session_state:
    st.session_state.oracle_results = None
if "oracle_info" not in st.session_state:
    st.session_state.oracle_info = None
if "active_user_id" not in st.session_state:
    st.session_state.active_user_id = 276726
if "recommended_user_id" not in st.session_state:
    st.session_state.recommended_user_id = None

# ── Load resources ────────────────────────────────────────────────────────────
with st.spinner("🔮 Summoning BookMind Oasis…"):
    model, books, ratings, users = load_data()

popular_df = get_popular_list(books, ratings)
user_pool  = get_user_options(ratings)


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
_html("""
<div style="text-align:center; padding:10px 0;">
  <span style="font-size:3rem; filter: drop-shadow(0 0 10px rgba(226,201,116,0.3));">🔮</span>
  <h2 style="color:#e2c974; font-family:'Playfair Display',serif; font-weight:700; margin-top:10px; margin-bottom:5px;">Oasis Menu</h2>
</div>
""", sidebar=True)

explore_mode = st.sidebar.radio(
    "Choose Exploration Mode",
    ["📚 Book Recommendation", "🔮 Vibe Explorer", "🃏 Book Tarot", "📈 Insights Hub"]
)

_html("""
<hr style="border-top: 1px solid rgba(226,201,116,0.2); margin: 25px 0;">
<h3 style="color:#e2c974; font-size:1.1rem; font-weight:700; margin-bottom:12px;">📖 My Reading Queue</h3>
""", sidebar=True)

if not st.session_state.reading_list:
    st.sidebar.info("Your queue is empty. Click '➕ Queue' on cards to add books.")
else:
    for idx, item in enumerate(st.session_state.reading_list):
        col_txt, col_del = st.sidebar.columns([4, 1])
        with col_txt:
            _html(f"""<div style="margin-bottom:8px;">
              <div style="font-size:0.82rem; font-weight:700; color:#f1f5f9; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="{item['title']}">{item['title']}</div>
              <div style="font-size:0.7rem; color:#8ba89f;">{item['author']}</div>
            </div>""", sidebar=True)
        with col_del:
            if st.sidebar.button("❌", key=f"del_{item['isbn']}_{idx}"):
                st.session_state.reading_list.pop(idx)
                st.rerun()
    if st.sidebar.button("🧹 Clear All Queue", key="clear_all"):
        st.session_state.reading_list = []
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  MODE 1: BOOK RECOMMENDATION
# ══════════════════════════════════════════════════════════════════════════════
if explore_mode == "📚 Book Recommendation":
    _html("""<div class="oasis-hero">
      <h1 class="oasis-title">📚 <span class="oasis-gold-text">Book Recommendation</span></h1>
      <p class="oasis-subtitle">Provide your User ID to retrieve custom machine learning predictions trained specifically on the rating matrices.</p>
    </div>""")

    with st.container(border=True):
        col_id, col_num, col_rand = st.columns([2, 2, 1])
        with col_id:
            user_id_input = st.number_input(
                "Enter User ID", 
                min_value=1, 
                max_value=999_999, 
                value=int(st.session_state.active_user_id), 
                step=1, 
                help="Type a user ID from the dataset."
            )
        with col_num:
            top_n = st.slider("Number of predictions", min_value=1, max_value=20, value=10)
        with col_rand:
            _html("<div style='height:26px'></div>")
            if st.button("🎲 Random", use_container_width=True):
                st.session_state.active_user_id = random.choice(user_pool)
                st.rerun()
        calc_btn = st.button("🔮 Calculate Predictions", use_container_width=True)

    # Sync the typed value into active_user_id
    st.session_state.active_user_id = int(user_id_input)


    if st.session_state.oracle_results is None or calc_btn:
        uid = int(st.session_state.active_user_id)
        with st.spinner("Querying the matrix..."):
            res = predict_svd(uid, model, books, ratings, top_n)
        if res.empty:
            st.error("User not found or has rated all candidate books.")
            if st.session_state.oracle_results is None:
                st.session_state.oracle_results = None
                st.session_state.oracle_info = None
        else:
            user_row = users[users["User-ID"] == uid]
            rated_cnt = len(ratings[ratings["User-ID"] == uid])
            persona = "Bibliophile" if rated_cnt > 15 else ("Active Reader" if rated_cnt > 5 else "Curious Traveler")
            st.session_state.oracle_info = {
                "user_id": uid,
                "age": int(user_row["Age"].values[0]) if not user_row.empty else "N/A",
                "location": user_row["Location"].values[0] if not user_row.empty else "Unknown",
                "rated_count": rated_cnt,
                "persona": persona,
            }
            st.session_state.oracle_results = res
            st.session_state.recommended_user_id = uid

    if st.session_state.oracle_results is not None:
        info = st.session_state.oracle_info
        res  = st.session_state.oracle_results

        _html(f"""<div class="stat-banner">
          <div class="stat-box"><div class="stat-label">User ID</div><div class="stat-val">#{info['user_id']}</div></div>
          <div class="stat-box"><div class="stat-label">Reader Persona</div><div class="stat-val" style="color:#fbbf24;">{info['persona']}</div></div>
          <div class="stat-box"><div class="stat-label">Age</div><div class="stat-val">{info['age']}</div></div>
          <div class="stat-box"><div class="stat-label">Location</div><div class="stat-val" style="font-size:0.95rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{info['location']}</div></div>
          <div class="stat-box"><div class="stat-label">Books Rated</div><div class="stat-val">{info['rated_count']}</div></div>
        </div>""")

        _html('<div class="oasis-section-title">🔮 Predicted for You</div>')
        _html('<div class="oasis-section-sub">Tuned SVD predictions based on matrix factorization</div>')

        num_cols = 5
        cols = st.columns(num_cols)
        for idx, row in res.iterrows():
            col = cols[idx % num_cols]
            with col:
                _html(get_card_html(row["Book-Title"], row["Book-Author"], row["Image-URL-L"], f"★ {row['Predicted_Rating']:.2f} Est"))
                isbn, title, auth = row["ISBN"], row["Book-Title"], row["Book-Author"]
                if st.button("➕ Queue", key=f"add_{isbn}_{idx}", use_container_width=True):
                    if isbn not in [b["isbn"] for b in st.session_state.reading_list]:
                        st.session_state.reading_list.append({"isbn": isbn, "title": title, "author": auth})
                        st.toast(f"Added '{title}' to queue!")
                        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  MODE 2: VIBE EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
elif explore_mode == "🔮 Vibe Explorer":
    _html("""<div class="oasis-hero">
      <h1 class="oasis-title">🔮 The <span class="oasis-gold-text">Vibe Explorer</span></h1>
      <p class="oasis-subtitle">Filter or search the library based on your current reading mood or specific keyword tags.</p>
    </div>""")

    with st.container(border=True):
        col_mood, col_kw = st.columns([1, 1])
        with col_mood:
            selected_mood = st.selectbox("Select a Mood", ["None - Search custom keyword instead"] + list(mood_presets.keys()))
        with col_kw:
            custom_query = st.text_input("Or type custom keyword", placeholder="e.g. magic, thriller, historical")

    query_terms = []
    if selected_mood != "None - Search custom keyword instead":
        query_terms = mood_presets[selected_mood]
    elif custom_query.strip():
        query_terms = [custom_query.strip().lower()]

    if query_terms:
        pattern = "|".join(query_terms)
        matches = books[books["Book-Title"].str.lower().str.contains(pattern, na=False)].copy().head(15)
        if matches.empty:
            st.warning("No matches found for that vibe. Try another keyword!")
        else:
            _html(f'<div class="oasis-section-title">🔮 Matching Your Vibe</div>')
            _html(f'<div class="oasis-section-sub">Filtered books based on the tags: {", ".join(query_terms)}</div>')
            num_cols = 5
            cols = st.columns(num_cols)
            for idx, (_, row) in enumerate(matches.iterrows()):
                col = cols[idx % num_cols]
                with col:
                    _html(get_card_html(row["Book-Title"], row["Book-Author"], row["Image-URL-L"], "Vibe Match"))
                    isbn, title, auth = row["ISBN"], row["Book-Title"], row["Book-Author"]
                    if st.button("➕ Queue", key=f"vibe_{isbn}_{idx}", use_container_width=True):
                        if isbn not in [b["isbn"] for b in st.session_state.reading_list]:
                            st.session_state.reading_list.append({"isbn": isbn, "title": title, "author": auth})
                            st.toast(f"Added '{title}' to queue!")
                            st.rerun()
    else:
        st.info("Choose a mood or type a keyword above to explore matching books.")


# ══════════════════════════════════════════════════════════════════════════════
#  MODE 3: BOOK TAROT
# ══════════════════════════════════════════════════════════════════════════════
elif explore_mode == "🃏 Book Tarot":
    _html("""<div class="oasis-hero">
      <h1 class="oasis-title">🃏 Book <span class="oasis-gold-text">Tarot</span></h1>
      <p class="oasis-subtitle">Draw a tarot card from the library. The Oracle will select a surprise highly-rated book and interpret its meaning for you.</p>
    </div>""")

    draw_card = st.button("🃏 Draw a Tarot Card", use_container_width=True)

    if draw_card:
        tarot_book = popular_df.sample(1).iloc[0]
        oracle_readings = [
            "The stars indicate this book holds the wisdom you seek. It represents a journey of self-discovery and intrigue.",
            "A warm and inviting tale. The Oracle predicts this will bring tranquility and comfort to your current thoughts.",
            "A thrilling adventure awaits. Prepare to be kept on the edge of your seat as hidden truths are revealed.",
            "This card symbolizes growth. This story will challenge your assumptions and expand your horizons.",
        ]
        reading = random.choice(oracle_readings)

        _html(f"""
        <div class="tarot-deck">
          <div class="tarot-card">
            <div class="tarot-decor">
              <span class="tarot-icon">🃏</span>
              <div style="font-weight:700; color:#e2c974; font-size:1.15rem; margin:10px 0; font-family:'Playfair Display',serif;">THE READ</div>
              <div style="font-size:0.85rem; color:#f1f5f9; font-weight:600; line-height:1.4;">"{tarot_book['Book-Title']}"</div>
              <div style="font-size:0.75rem; color:#8ba89f; margin-top:5px;">by {tarot_book['author']}</div>
              <span class="tarot-icon">🔮</span>
            </div>
          </div>
        </div>
        <div class="oasis-panel" style="text-align:center; max-width:600px; margin:0 auto 30px;">
          <h4 style="color:#e2c974; margin-bottom:8px; font-family:'Playfair Display',serif; font-style:italic;">Oracle's Interpretation</h4>
          <p style="color:#8ba89f; font-size:0.92rem; line-height:1.6;">{reading}</p>
        </div>""")

        isbn, title, auth = tarot_book["isbn"], tarot_book["Book-Title"], tarot_book["author"]
        col_tarot_add, _ = st.columns([1, 1])
        with col_tarot_add:
            if st.button("➕ Queue This Surprise Read", key=f"add_tarot_{isbn}", use_container_width=True):
                if isbn not in [b["isbn"] for b in st.session_state.reading_list]:
                    st.session_state.reading_list.append({"isbn": isbn, "title": title, "author": auth})
                    st.toast(f"Added '{title}' to queue!")
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  MODE 4: INSIGHTS HUB
# ══════════════════════════════════════════════════════════════════════════════
elif explore_mode == "📈 Insights Hub":
    _html("""<div class="oasis-hero">
      <h1 class="oasis-title">📈 Insights <span class="oasis-gold-text">Hub</span></h1>
      <p class="oasis-subtitle">Explore key model evaluation metrics and algorithms benchmarked on the book-crossing dataset.</p>
    </div>""")

    _html("""<div class="oasis-panel">
      <div style="font-weight:700; font-size:1.15rem; margin-bottom:18px; color:#e2c974;">📈 Model Benchmarks</div>
      <table class="comparison-table">
        <thead><tr><th>Model / Algorithm</th><th>RMSE ↓</th><th>MAE ↓</th></tr></thead>
        <tbody>
          <tr class="best-model-row"><td>🏆 Tuned SVD (Collaborative Filtering)</td><td>1.8422</td><td>1.4433</td></tr>
          <tr><td>Tuned Baseline Only</td><td>1.8478</td><td>1.4563</td></tr>
          <tr><td>Standard Baseline Only</td><td>1.8624</td><td>1.4758</td></tr>
          <tr><td>Standard SVD</td><td>1.8639</td><td>1.4777</td></tr>
          <tr><td>K-Nearest Neighbors (KNN Basic)</td><td>1.9120</td><td>1.5309</td></tr>
          <tr><td>Non-Negative Matrix Factorization (NMF)</td><td>2.0880</td><td>1.6621</td></tr>
          <tr><td>Wide &amp; Deep (Neural Hybrid)</td><td>4.1430</td><td>3.1116</td></tr>
          <tr><td>Neural Collaborative Filtering (NCF)</td><td>4.2512</td><td>3.1212</td></tr>
          <tr><td>DeepFM (Deep Factorization Machines)</td><td>4.2578</td><td>3.1102</td></tr>
        </tbody>
      </table>
    </div>""")


# ══════════════════════════════════════════════════════════════════════════════
#  TRENDING BOOKS FOOTER
# ══════════════════════════════════════════════════════════════════════════════
if explore_mode != "📈 Insights Hub":
    _html("<hr class='bm-divider'>")
    _html('<div class="oasis-section-title">🔥 Trending Books</div>')
    _html('<div class="oasis-section-sub">Highest-rated books across all users in the community</div>')

    num_cols = 6
    cols = st.columns(num_cols)
    for idx, (_, row) in enumerate(popular_df.head(18).iterrows()):
        col = cols[idx % num_cols]
        with col:
            _html(get_card_html(row["Book-Title"], row["author"], row["image"], f"★ {row['avg_rating']:.1f} Avg"))
            isbn, title, auth = row["isbn"], row["Book-Title"], row["author"]
            if st.button("➕ Queue", key=f"trend_{isbn}_{idx}", use_container_width=True):
                if isbn not in [b["isbn"] for b in st.session_state.reading_list]:
                    st.session_state.reading_list.append({"isbn": isbn, "title": title, "author": auth})
                    st.toast(f"Added '{title}' to queue!")
                    st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
_html("""<hr class="bm-divider">
<div style="text-align:center; color:#475569; font-size:0.85rem; padding:20px 0 40px;">
  🔮 <strong style="color:#94a3b8;">Book Recommendation</strong> — AI Book Recommendation System<br/>
  <span style="font-size:0.78rem;">Built with Python · Streamlit · scikit-surprise · Book-Crossing Dataset</span>
</div>""")
