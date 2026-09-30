import streamlit as st
from serpapi import GoogleSearch
from google import genai
from PIL import Image
import json, time, re, html, os

SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not SERPAPI_API_KEY or not GEMINI_API_KEY:
    print("WARNING: SERPAPI_API_KEY or GEMINI_API_KEY is missing. Check your .env file.")

HISTORY_FILE = "deal_history.json"
SAVED_FILE = "saved_deals.json"

REGION = {
    "gl": "in",
    "hl": "en",
    "location": "India",
    "google_domain": "google.co.in",
    "currency": "INR",
    "symbol": "₹",
}

st.set_page_config(page_title="Deal Scout", page_icon="🛍️")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');

:root {
    --purple: #8E5DBF;
    --purple-soft: #EDE3FF;
    --pink: #D4588C;
    --pink-soft: #FCE9F1;
    --surface: #FFFFFF;
    --text: #3D3154;
    --text-muted: #756A82;
    --border: rgba(104,76,132,0.14);
}

html, body, .stApp {
    background:
        radial-gradient(circle at 10% 20%, rgba(240,196,235,0.45), transparent 45%),
        radial-gradient(circle at 90% 10%, rgba(222,207,255,0.45), transparent 45%),
        #FFFAF6;
    background-attachment: fixed;
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}
h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'Fraunces', serif !important;
    color: var(--text);
}
p, span, label { color: var(--text); }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #FFFAF6 0%, #FCE9F1 100%);
    border-right: 1px solid var(--border);
}

.ds-header { display:flex; align-items:center; gap:0.6rem; margin-bottom:0.2rem; }
.ds-header .ds-mark { font-size:1.8rem; }
.ds-header h1 { font-size:1.9rem; margin:0; font-weight:800; }
.ds-tagline-pill {
    display:inline-block; background: var(--surface); border:1px solid var(--border);
    color: var(--text-muted); font-size:0.82rem; padding:0.35rem 1rem; border-radius:999px;
    margin: 0.5rem 0 0.7rem 0; box-shadow: 0 2px 10px rgba(139,92,246,0.08);
}
.stat-row { display:flex; gap:0.5rem; margin: 0 0 1.6rem 0; flex-wrap:wrap; }
.stat-chip {
    background: var(--surface); border:1px solid var(--border); color: var(--text-muted);
    font-size:0.72rem; font-weight:600; padding:0.28rem 0.75rem; border-radius:999px;
}

@keyframes fadeSlideUp { from { opacity:0; transform:translateY(10px);} to {opacity:1; transform:translateY(0);} }

.product-card {
    display:flex; gap:1rem; align-items:center;
    background: var(--surface); border-radius:18px;
    box-shadow: 0 4px 18px rgba(139,92,246,0.12);
    padding:1.1rem 1.3rem; margin-bottom:1rem;
    animation: fadeSlideUp 0.35s ease;
}
.product-card img { width:100px; height:100px; object-fit:contain; border-radius:14px; background:#fff; border:1px solid var(--border); }
.product-card .p-title { font-family:'Fraunces',serif; font-weight:700; font-size:1.15rem; margin:0; }
.product-card .p-price { color: var(--pink); font-family:'Fraunces',serif; font-weight:700; font-size:1.05rem; margin-top:0.3rem; }

.reviews-card {
    background: var(--purple-soft); border-radius:14px; padding:0.8rem 1.1rem; margin-bottom:1rem;
    animation: fadeSlideUp 0.4s ease;
}
.reviews-title { font-family:'Fraunces',serif; font-weight:700; font-size:0.85rem; color: var(--purple); margin-bottom:0.3rem; }
.reviews-line { font-size:0.95rem; }
.sentiment-tag {
    display:inline-block; font-size:0.75rem; padding:0.15rem 0.6rem; border-radius:999px;
    margin-left:0.5rem; background: var(--surface); border:1px solid var(--border); color: var(--purple); font-weight:600;
}

.verdict-panel {
    background: var(--surface); border-radius:18px;
    box-shadow: 0 4px 18px rgba(139,92,246,0.12);
    padding:1.3rem 1.5rem; margin-bottom:1.2rem;
    animation: fadeSlideUp 0.45s ease;
}
.verdict-pill {
    display:inline-flex; align-items:center; gap:0.4rem;
    font-family:'Fraunces',serif; font-weight:700; font-size:1.05rem;
    padding:0.5rem 1.2rem; border-radius:999px; margin-bottom:0.8rem;
}
.pill-buy { background: var(--purple); color: #fff; }
.pill-pass { background: var(--pink); color: #fff; }

.score-label { color: var(--text-muted); font-size:0.78rem; margin-bottom:0.3rem; }
.score-track { background: var(--purple-soft); border-radius:999px; height:9px; width:100%; max-width:280px; overflow:hidden; margin-bottom:1.1rem; }
.score-fill { height:100%; border-radius:999px; }
.verdict-summary { font-size:1rem; line-height:1.6; color: var(--text); max-width:70ch; }

.pc-grid { display:flex; gap:1rem; flex-wrap:wrap; margin-top:1.1rem; }
.pc-col { flex:1; min-width:220px; border-radius:14px; padding:0.9rem 1.1rem; }
.pc-pros { background: var(--purple-soft); }
.pc-cons { background: var(--pink-soft); }
.pc-col h4 { margin:0 0 0.5rem 0; font-size:0.85rem; font-weight:700; font-family:'Fraunces',serif; }
.pc-col ul { margin:0; padding-left:1.1rem; font-size:0.88rem; line-height:1.6; }

.store-card {
    display:flex; justify-content:space-between; align-items:center;
    border-radius:12px; padding:0.7rem 1.1rem;
    margin-bottom:0.5rem; background: var(--surface); box-shadow: 0 2px 10px rgba(139,92,246,0.08);
    transition: transform .15s ease, box-shadow .15s ease;
}
.store-card:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(139,92,246,0.16); }
.store-card a { color: var(--text); font-weight:600; text-decoration:none; }
.store-card a:hover { color: var(--purple); }
.store-price { font-family:'Fraunces',serif; font-weight:700; color: var(--pink); }
.store-rating { color: var(--text-muted); font-size:0.85rem; margin-left:0.5rem; }

.alt-row { display:flex; flex-wrap:wrap; gap:0.6rem; margin-top:0.5rem; }
.alt-chip {
    border-radius:12px; padding:0.55rem 0.9rem;
    background: var(--surface); font-size:0.85rem; max-width:220px;
    box-shadow: 0 2px 10px rgba(139,92,246,0.08);
}
.alt-chip a { color: var(--text); text-decoration:none; font-weight:600; }
.alt-chip a:hover { color: var(--purple); }
.alt-chip .alt-price { color: var(--pink); font-weight:600; display:block; margin-top:0.2rem; }

div.stButton > button {
    background: linear-gradient(110deg, var(--purple), var(--pink)); color:#fff; border:none; border-radius:999px;
    font-family:'DM Sans',sans-serif; font-weight:700; padding:0.55rem 1.4rem;
    box-shadow: 0 10px 18px rgba(191,100,184,0.22);
}
div.stButton > button:hover { filter: saturate(1.1); color:#fff; }

.side-item { font-size:0.85rem; margin-bottom:0.5rem; line-height:1.4; }
</style>

<div class="ds-header">
    <span class="ds-mark">🛍️</span>
    <h1>Deal Scout</h1>
</div>
<div class="ds-tagline-pill">Live prices &amp; honest verdicts — powered by SerpApi + Gemini</div>
<div class="stat-row">
    <span class="stat-chip">🔎 Live SerpApi Data</span>
    <span class="stat-chip">🤖 Gemini AI Verdict</span>
    <span class="stat-chip">💜 Zero-cost FAQ</span>
</div>
""", unsafe_allow_html=True)

def load_json_list(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_json_list(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

# Session state initialization
if "shopping_results" not in st.session_state:
    st.session_state.shopping_results = None
if "last_query" not in st.session_state:
    st.session_state.last_query = ""
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "current_alternatives" not in st.session_state:
    st.session_state.current_alternatives = []
if "deal_history" not in st.session_state:
    st.session_state.deal_history = load_json_list(HISTORY_FILE)
if "saved_deals" not in st.session_state:
    st.session_state.saved_deals = load_json_list(SAVED_FILE)

def clean_query(user_query):
    return re.sub(r'[^\w\s]', '', user_query).strip()

def extract_price(item, symbol):
    """Robustly extracts and formats price from SerpApi data fields."""
    price = item.get("price")
    if not price and item.get("extracted_price"):
        price = f"{symbol}{item.get('extracted_price')}"
    if not price:
        price = item.get("rich_snippet", {}).get("top", {}).get("detected_extensions", {}).get("price")
        if price and not str(price).startswith(symbol):
            price = f"{symbol}{price}"
    if not price or str(price).strip() == "N/A":
        return None
    return str(price).strip()

def is_valid_local_item(item, region):
    """Filters out items with missing prices or foreign currency symbols."""
    price = extract_price(item, region["symbol"])
    if not price:
        return False
    if region["currency"] == "INR":
        if any(sym in price for sym in ["$", "€", "£"]):
            return False
    return True

def classify_gemini_error(err):
    """Sorts a Gemini failure into a type so the UI can show the right message."""
    if err is None:
        return None
    text = str(err)
    if "429" in text or "RESOURCE_EXHAUSTED" in text or "quota" in text.lower():
        return "quota"
    if "503" in text or "UNAVAILABLE" in text or "overloaded" in text.lower():
        return "overload"
    return "other"

def call_gemini_with_retry(contents, max_retries=4, model_name="gemini-flash-latest"):
    """
    Calls Gemini with REAL retries: waits longer between each attempt (1s, 2s, 4s, 8s)
    for transient overload errors. Stops immediately on a quota error - that's a
    daily request limit, and waiting a few seconds won't fix it.
    """
    client = genai.Client(api_key=GEMINI_KEY)
    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model=model_name, contents=contents)
            return response.text.strip(), None
        except Exception as e:
            last_error = e
            print(f"[Gemini attempt {attempt + 1}/{max_retries} failed] {e}")
            if classify_gemini_error(e) == "quota":
                break
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    return None, last_error

def analyze_image_with_gemini(image_file):
    """Identifies the product in an image using Gemini Vision."""
    img = Image.open(image_file)
    prompt = (
        "Look at this image carefully and identify the exact product. Pay close attention to "
        "its color, pattern, material, and any visible brand name or text. Return ONLY a specific "
        "search term (4-8 words) that includes the color and key distinguishing details, suitable "
        "for finding this exact item on Google Shopping - for example 'blue chiffon tiered midi "
        "dress' rather than just 'midi dress'. If it's clearly a real household/consumer item, do "
        "not describe it in a way that could be confused with a children's toy version, unless it "
        "actually is a toy. Do not add markdown, quotes, or conversational text."
    )
    return call_gemini_with_retry([img, prompt])

def parse_json_verdict(text):
    """Tries to parse Gemini's reply as the structured verdict JSON. Returns dict or None."""
    cleaned = re.sub(r'^```(?:json)?|```$', '', text.strip(), flags=re.MULTILINE).strip()
    try:
        data = json.loads(cleaned)
        if "verdict" in data:
            return data
    except Exception:
        pass
    return None

def parse_plain_verdict(text):
    """Fallback for when Gemini ignores the JSON format and replies in plain text."""
    match = re.match(r'\s*(BUY|PASS)\b[:\-]?\s*(.*)', text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).upper(), match.group(2).strip()
    return None, text.strip()

def parse_price_number(price_str):
    """Best-effort extraction of a comparable number from a price string like '₹19,999'."""
    if not price_str:
        return None
    match = re.search(r'[\d,]+(?:\.\d+)?', str(price_str))
    if not match:
        return None
    try:
        return float(match.group(0).replace(",", ""))
    except ValueError:
        return None

def sentiment_label(rating):
    """Maps the product's real star rating to a plain-language tag - no extra API call needed."""
    try:
        r = float(rating)
    except (TypeError, ValueError):
        return None
    if r >= 4.5:
        return "Strongly Positive"
    if r >= 4.0:
        return "Positive"
    if r >= 3.0:
        return "Mixed"
    return "Negative"

def build_deal_entry(summary, price_display, verdict_word, score, thumb, summary_text, pros, cons, stores):
    """Bundles everything needed to fully re-display this deal later from History or Saved Deals."""
    return {
        "title": summary.get("title"),
        "price": price_display,
        "verdict": verdict_word,
        "score": score,
        "thumbnail": thumb,
        "summary_text": summary_text,
        "pros": pros or [],
        "cons": cons or [],
        "rating": summary.get("rating"),
        "reviews": summary.get("reviews"),
        "stores": stores or [],
    }

def entry_to_result(entry):
    """Converts a stored History/Saved Deals entry back into the shape render_result() expects."""
    verdict_json = json.dumps({
        "verdict": entry.get("verdict"),
        "score": entry.get("score"),
        "summary": entry.get("summary_text"),
        "pros": entry.get("pros") or [],
        "cons": entry.get("cons") or [],
    })
    return {
        "summary": {
            "title": entry.get("title"),
            "rating": entry.get("rating"),
            "reviews": entry.get("reviews"),
            "price_range": entry.get("price"),
        },
        "thumb": entry.get("thumbnail"),
        "stores": entry.get("stores") or [],
        "verdict_text": verdict_json,
        "error_type": None,
        "last_error_str": None,
        "_logged": True,
    }

def render_result(result, alternatives=None):
    """Renders the product card, reviews, verdict, pros/cons, save button, stores, and the
    zero-cost 'Ask Deal Scout' quick-question section. Lives OUTSIDE the Get Verdict button
    so it survives reruns (like clicking Save)."""
    summary = result["summary"]
    thumb = result["thumb"]
    stores = result["stores"]
    verdict_text = result["verdict_text"]
    error_type = result["error_type"]
    last_error_str = result["last_error_str"]
    alternatives = alternatives or []

    rating_val = summary.get("rating")
    reviews_val = summary.get("reviews")
    sentiment = sentiment_label(rating_val)
    price_display = summary.get("price_range") or summary.get("price")

    # 1. Product details
    img_html = f'<img src="{thumb}" />' if thumb else ""
    price_html = f'<div class="p-price">{html.escape(str(price_display))}</div>' if price_display else ""
    st.markdown(
        f'<div class="product-card">{img_html}'
        f'<div><p class="p-title">{html.escape(str(summary.get("title") or ""))}</p>{price_html}</div></div>',
        unsafe_allow_html=True
    )

    # 2. Reviews
    if rating_val or reviews_val:
        sentiment_html = f'<span class="sentiment-tag">{sentiment}</span>' if sentiment else ""
        stars = "⭐ " + str(rating_val) if rating_val else ""
        review_count = f" · {reviews_val} reviews" if reviews_val else ""
        st.markdown(
            f'<div class="reviews-card"><div class="reviews-title">Reviews</div>'
            f'<div class="reviews-line">{html.escape(stars)}{html.escape(review_count)}{sentiment_html}</div></div>',
            unsafe_allow_html=True
        )

    # 3. Verdict + score + pros/cons
    final_verdict_word = None
    final_score = None
    final_summary_text = None
    final_pros = []
    final_cons = []

    if verdict_text:
        parsed = parse_json_verdict(verdict_text)
        if parsed:
            verdict_word = str(parsed.get("verdict", "")).upper()
            score = parsed.get("score")
            final_verdict_word = verdict_word
            final_score = score if isinstance(score, (int, float)) else None
            final_summary_text = str(parsed.get("summary", ""))
            final_pros = parsed.get("pros") or []
            final_cons = parsed.get("cons") or []
            pill_class = "pill-buy" if verdict_word == "BUY" else "pill-pass"
            fill_color = "var(--purple)" if verdict_word == "BUY" else "var(--pink)"
            score_html = ""
            if isinstance(score, (int, float)):
                score_html = (
                    f'<div class="score-label">Deal Value Score — {int(score)}/100</div>'
                    f'<div class="score-track"><div class="score-fill" style="width:{int(score)}%; background:{fill_color};"></div></div>'
                )
            pros = parsed.get("pros") or []
            cons = parsed.get("cons") or []
            pros_html = "".join(f"<li>{html.escape(str(x))}</li>" for x in pros)
            cons_html = "".join(f"<li>{html.escape(str(x))}</li>" for x in cons)
            pc_html = ""
            if pros or cons:
                pc_html = (
                    '<div class="pc-grid">'
                    f'<div class="pc-col pc-pros"><h4>✓ Key Strengths</h4><ul>{pros_html}</ul></div>'
                    f'<div class="pc-col pc-cons"><h4>⚠ Watch Out For</h4><ul>{cons_html}</ul></div>'
                    '</div>'
                )
            st.markdown(
                f'<div class="verdict-panel">'
                f'<div class="verdict-pill {pill_class}">{"✔" if verdict_word=="BUY" else "✕"} {verdict_word} DEAL</div>'
                f'{score_html}'
                f'<div class="verdict-summary">{html.escape(str(parsed.get("summary","")))}</div>'
                f'{pc_html}'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            verdict_word, reasoning = parse_plain_verdict(verdict_text)
            final_verdict_word = verdict_word
            final_summary_text = reasoning
            if verdict_word:
                pill_class = "pill-buy" if verdict_word == "BUY" else "pill-pass"
                st.markdown(
                    f'<div class="verdict-panel">'
                    f'<div class="verdict-pill {pill_class}">{verdict_word} DEAL</div>'
                    f'<div class="verdict-summary">{html.escape(reasoning)}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown("### Verdict")
                st.write(verdict_text)
    elif error_type == "quota":
        st.error("You've hit today's free Gemini quota (20 requests/day for this model). Wait for it to reset, or switch to a different API key.")
    elif error_type == "overload":
        st.error("Gemini is overloaded right now (high demand). Wait a few seconds and click Get Verdict again.")
    else:
        st.error(f"Gemini API Error: {last_error_str}")

    # 4. History (log once) + Save Deal
    if final_verdict_word and not result.get("_logged"):
        entry = build_deal_entry(summary, price_display, final_verdict_word, final_score, thumb,
                                  final_summary_text, final_pros, final_cons, stores)
        st.session_state.deal_history.insert(0, entry)
        st.session_state.deal_history = st.session_state.deal_history[:20]
        save_json_list(HISTORY_FILE, st.session_state.deal_history)
        result["_logged"] = True

    if final_verdict_word:
        if st.button("💾 Save This Deal", key=f"save_{summary.get('title')}"):
            entry = build_deal_entry(summary, price_display, final_verdict_word, final_score, thumb,
                                      final_summary_text, final_pros, final_cons, stores)
            st.session_state.saved_deals.insert(0, entry)
            st.session_state.saved_deals = st.session_state.saved_deals[:20]
            save_json_list(SAVED_FILE, st.session_state.saved_deals)
            st.success("Saved! Check the sidebar. 💜")

    # 5. Where to buy
    if stores:
        st.markdown("### Where to buy")
        for s in stores:
            rating_str = f"⭐ {s['rating']}" if s.get("rating") else "rating unavailable"
            name = html.escape(str(s.get("name") or ""))
            price = html.escape(str(s.get("price") or ""))
            name_html = f'<a href="{s["link"]}" target="_blank">{name}</a>' if s.get("link") else name
            st.markdown(
                f'<div class="store-card"><div>{name_html}'
                f'<span class="store-rating">{rating_str}</span></div>'
                f'<div class="store-price">{price}</div></div>',
                unsafe_allow_html=True
            )

    # 6. You might also consider — visible section (real data, already fetched, no extra cost)
    if alternatives:
        st.markdown("### You might also consider")
        chips = ""
        for a in alternatives:
            title = html.escape(str(a.get("title") or "")[:40])
            price = html.escape(str(a.get("clean_price") or ""))
            link = a.get("link") or a.get("product_link")
            title_html = f'<a href="{link}" target="_blank">{title}</a>' if link else title
            chips += f'<div class="alt-chip">{title_html}<span class="alt-price">{price}</span></div>'
        st.markdown(f'<div class="alt-row">{chips}</div>', unsafe_allow_html=True)

    # 7. Ask Deal Scout — quick answers from data already fetched, zero extra Gemini calls
    if final_verdict_word:
        st.markdown("### 💬 Ask Deal Scout")

        with st.expander("💰 Why this price?"):
            st.write(final_summary_text or "No pricing breakdown available for this item.")

        with st.expander("⭐ What do reviews say?"):
            if rating_val or reviews_val:
                sent = sentiment_label(rating_val)
                st.write(f"Rated {rating_val or 'N/A'} across {reviews_val or 0} reviews — overall sentiment: **{sent or 'unknown'}**.")
            else:
                st.write("No review data was available for this listing.")

        with st.expander("🤔 Buy now or wait?"):
            verb = "go for it" if final_verdict_word == "BUY" else "hold off"
            st.write(f"Deal Scout's take: **{final_verdict_word}** — in short, {verb}. {final_summary_text or ''}")

        with st.expander("💸 Who has the lowest price?"):
            if stores:
                priced = [(s, parse_price_number(s.get("price"))) for s in stores]
                priced = [(s, p) for s, p in priced if p is not None]
                if priced:
                    cheapest, _ = min(priced, key=lambda x: x[1])
                    st.write(f"**{cheapest.get('name')}** has the lowest listed price here: {cheapest.get('price')}.")
                else:
                    st.write("Couldn't compare prices across sellers for this item.")
            else:
                st.write(f"Only one listing found: {price_display or 'price unavailable'}.")

        with st.expander("📊 What's driving this score?"):
            if final_score is not None:
                bits = [f"Deal Scout gave this a **{int(final_score)}/100**."]
                if final_pros:
                    bits.append(f"Biggest strength: {final_pros[0]}.")
                if final_cons:
                    bits.append(f"Biggest concern: {final_cons[0]}.")
                st.write(" ".join(bits))
            else:
                st.write("No score was generated for this item.")

# --- Sidebar: History + Saved Deals (click any item to see its full details again) ---
with st.sidebar:
    st.markdown("### 📜 Recent History")
    if st.session_state.deal_history:
        for i, h in enumerate(st.session_state.deal_history[:10]):
            tag = "🟣" if h.get("verdict") == "BUY" else "🌸"
            label = f"{tag} {str(h.get('title',''))[:32]}"
            if st.button(label, key=f"hist_{i}"):
                st.session_state.current_result = entry_to_result(h)
                st.session_state.current_alternatives = []
            st.caption(str(h.get("price","")))
        if st.button("🗑️ Clear History", key="clear_history"):
            st.session_state.deal_history = []
            save_json_list(HISTORY_FILE, [])
    else:
        st.caption("No searches yet.")

    st.markdown("### ⭐ Saved Deals")
    if st.session_state.saved_deals:
        for i, s in enumerate(st.session_state.saved_deals[:10]):
            label = f"💜 {str(s.get('title',''))[:32]}"
            if st.button(label, key=f"saved_{i}"):
                st.session_state.current_result = entry_to_result(s)
                st.session_state.current_alternatives = []
            st.caption(str(s.get("price","")))
        if st.button("🗑️ Clear Saved", key="clear_saved"):
            st.session_state.saved_deals = []
            save_json_list(SAVED_FILE, [])
    else:
        st.caption("Nothing saved yet.")

# Choose Search Mode
search_mode = st.radio("Choose Search Mode:", ["⌨️ Type Product Name", "📸 Take/Upload Photo"], horizontal=True)

query_input = ""

if search_mode == "⌨️ Type Product Name":
    query_input = st.text_input("What are you thinking of buying?", placeholder="e.g. OnePlus Nord Buds")
    if query_input:
        st.session_state.search_source = "text"

else:
    photo_option = st.radio("Photo Source:", ["Take Photo (Camera)", "Upload File"], horizontal=True)
    image_file = None

    if photo_option == "Take Photo (Camera)":
        image_file = st.camera_input("Snap a photo of the product")
    else:
        image_file = st.file_uploader("Upload product picture", type=["jpg", "jpeg", "png"])

    if image_file is not None:
        st.image(image_file, caption="Target Product Image", width=250)
        if st.button("Identify & Search Product"):
            with st.spinner("AI is analyzing the product image..."):
                extracted_query, img_error = analyze_image_with_gemini(image_file)
                error_type = classify_gemini_error(img_error)

            if extracted_query:
                st.success(f"Identified as: **{extracted_query}**")
                query_input = extracted_query
                st.session_state.search_source = "photo"
            else:
                st.session_state.shopping_results = None
                st.session_state.current_result = None
                if error_type == "quota":
                    st.error("You've hit today's free Gemini quota (20 requests/day for this model). Wait for it to reset, or switch to a different API key.")
                elif error_type == "overload":
                    st.error("Gemini is overloaded right now (high demand). Wait a few seconds and try again.")
                else:
                    st.error("Could not identify the product image. Try taking a clearer photo.")

# Execute Search when the query changes
if query_input and query_input != st.session_state.last_query:
    cleaned_q = clean_query(query_input)

    with st.spinner(f"Searching for '{cleaned_q}'..."):
        shopping_params = {
            "engine": "google_shopping",
            "q": cleaned_q,
            "gl": REGION["gl"],
            "hl": REGION["hl"],
            "location": REGION["location"],
            "google_domain": REGION["google_domain"],
            "api_key": SERPAPI_KEY,
        }
        shopping = GoogleSearch(shopping_params).get_dict()

        spelling_suggestion = shopping.get("search_information", {}).get("spelling_fix")
        if spelling_suggestion:
            st.info(f"Showing results for: **{spelling_suggestion}**")
            shopping_params["q"] = spelling_suggestion
            shopping = GoogleSearch(shopping_params).get_dict()

        raw_results = shopping.get("shopping_results", [])

        valid_items = []
        for r in raw_results:
            if is_valid_local_item(r, REGION):
                r["clean_price"] = extract_price(r, REGION["symbol"])
                valid_items.append(r)

        if not valid_items:
            fallback_search = GoogleSearch({
                "engine": "google",
                "q": f"buy {cleaned_q}",
                "gl": REGION["gl"],
                "hl": REGION["hl"],
                "location": REGION["location"],
                "google_domain": REGION["google_domain"],
                "api_key": SERPAPI_KEY,
            }).get_dict()

            organic = fallback_search.get("organic_results", [])
            for item in organic:
                if is_valid_local_item(item, REGION):
                    item["clean_price"] = extract_price(item, REGION["symbol"])
                    valid_items.append(item)

        st.session_state.shopping_results = valid_items[:5]
        st.session_state.last_query = query_input
        st.session_state.current_result = None

results = st.session_state.shopping_results

if results is not None:
    if not results:
        st.error("No valid prices found for this product. Try a broader search term.")
    else:
        if st.session_state.get("search_source") == "photo":
            # Photo mode: the user doesn't know the product name, so a "which one did you
            # mean" list of guesses isn't useful - just go straight to the closest match.
            selected = results[0]
            st.caption(f"Matched to your photo: **{selected.get('title')}** — {selected.get('clean_price')}")
        else:
            options = [f"{r.get('title')} — {r.get('clean_price')}" for r in results]
            choice = st.selectbox("Which one did you mean?", options)
            selected = results[options.index(choice)]

        if st.button("Get Verdict"):
            page_token = selected.get("immersive_product_page_token")

            stores = []
            if page_token:
                details = GoogleSearch({
                    "engine": "google_immersive_product",
                    "page_token": page_token,
                    "api_key": SERPAPI_KEY,
                }).get_dict()
                p = details.get("product_results", {})

                for s in p.get("stores", [])[:5]:
                    s_price = s.get("price")
                    # Skip store prices in a different currency (the immersive API isn't always region-locked)
                    if s_price and any(sym in str(s_price) for sym in ["$", "€", "£"]) and REGION["symbol"] not in str(s_price):
                        continue
                    store_rating = s.get("rating") or s.get("store_rating") or s.get("extracted_rating")
                    stores.append({
                        "name": s.get("name"),
                        "price": s_price,
                        "rating": store_rating,
                        "link": s.get("link")
                    })

                # The immersive API's price_range can come back unlocalized (e.g. in $) even for an India search -
                # only trust it if it actually carries the region's currency symbol; otherwise use the
                # already-verified price from the original (region-filtered) search result.
                raw_price_range = p.get("price_range")
                if raw_price_range and REGION["symbol"] in str(raw_price_range) and not any(sym in str(raw_price_range) for sym in ["$", "€", "£"]):
                    price_range_value = raw_price_range
                else:
                    price_range_value = selected.get("clean_price")

                summary = {
                    "currency": REGION["currency"],
                    "title": p.get("title", selected.get("title")),
                    "brand": p.get("brand"),
                    "rating": p.get("rating", selected.get("rating")),
                    "reviews": p.get("reviews", selected.get("reviews")),
                    "price_range": price_range_value,
                    "stores": stores,
                }
            else:
                summary = {
                    "currency": REGION["currency"],
                    "title": selected.get("title"),
                    "price": selected.get("clean_price"),
                    "source": selected.get("source"),
                    "rating": selected.get("rating"),
                    "reviews": selected.get("reviews"),
                    "snippet": selected.get("snippet")
                }

            prompt = f"""You're a blunt, honest shopping advisor evaluating a deal in {REGION['currency']}.
Respond with ONLY valid JSON (no markdown fences, no extra text) in exactly this shape:
{{
  "verdict": "BUY" or "PASS",
  "score": <integer 0-100 - how good a deal this is>,
  "summary": "<2-3 sentence honest executive summary>",
  "pros": ["<short strength>", "..."],
  "cons": ["<short concern>", "..."]
}}
Don't just be positive - call out real red flags in cons if the rating or price looks weak. List at most 4 pros and 4 cons.

Product data:
{json.dumps(summary, indent=2)}"""

            with st.spinner("Getting verdict..."):
                verdict_text, last_error = call_gemini_with_retry(prompt)
            error_type = classify_gemini_error(last_error)

            st.session_state.current_result = {
                "summary": summary,
                "thumb": selected.get("thumbnail"),
                "stores": stores,
                "verdict_text": verdict_text,
                "error_type": error_type,
                "last_error_str": str(last_error) if last_error else None,
                "_logged": False,
            }
            st.session_state.current_alternatives = [r for r in results if r is not selected][:3]

# Render the persisted result - top-level so it shows whether it came from a fresh
# search, the Save button, or clicking a History/Saved item in the sidebar.
if st.session_state.current_result:
    render_result(st.session_state.current_result, st.session_state.get("current_alternatives", []))