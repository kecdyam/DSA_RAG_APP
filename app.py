import re, time, html, json, uuid
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from retriever import retrieve, MIN_SIMILARITY
from llm import answer_stream, MODEL
from cheatsheet import build_cheatsheet

REFUSAL = "can't find that in the notes"
NOT_FOUND_MSG = "I couldn't find that in your notes. Try naming a specific topic, like 'merge sort steps' or 'binary tree traversal'."
EXAMPLES = ["Explain Big-O", "What is a leaf node?", "How does merge sort work?", "/cheatsheet merge sort"]
FONTS = "@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600&family=Inter:wght@400;500&family=JetBrains+Mono:wght@500&display=swap');"
CHATS_FILE = Path(__file__).with_name("chats.json")

st.set_page_config(page_title="DSA Notes Assistant", page_icon="📚", initial_sidebar_state="expanded")

# ---------- saved chats ----------
def load_chats():
    try:
        return json.loads(CHATS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_chats():
    CHATS_FILE.write_text(json.dumps(st.session_state.chats, ensure_ascii=False), encoding="utf-8")

def new_chat():
    cid = uuid.uuid4().hex[:8]
    st.session_state.chats[cid] = {"title": "New chat", "messages": []}
    st.session_state.current = cid

if "chats" not in st.session_state:
    st.session_state.chats = load_chats()
    if st.session_state.chats:
        st.session_state.current = list(st.session_state.chats)[-1]
    else:
        new_chat()

# ---------- sidebar (hidden until the cursor touches the left edge) ----------
with st.sidebar:
    if st.button("+ New chat", use_container_width=True):
        if st.session_state.chats[st.session_state.current]["messages"]:  # don't pile up empty chats
            new_chat()
            save_chats()
        st.rerun()
    st.markdown('<div class="lbl">Chats</div>', unsafe_allow_html=True)
    for cid, c in reversed(list(st.session_state.chats.items())):
        mark = "● " if cid == st.session_state.current else ""
        col1, col2 = st.columns([5, 1])
        if col1.button(mark + c["title"][:26], key=f"chat_{cid}", use_container_width=True):
            st.session_state.current = cid
            st.rerun()
        if col2.button("✕", key=f"del_{cid}"):
            del st.session_state.chats[cid]
            if not st.session_state.chats:
                new_chat()
            elif st.session_state.current == cid:
                st.session_state.current = list(st.session_state.chats)[-1]
            save_chats()
            st.rerun()
    with st.expander("Advanced"):
        top_k = st.slider("Chunks to use (top-k)", 1, 8, 4)
        fx = st.radio("FX intensity", ["Off", "Low", "High"], index=1, horizontal=True)
    try:  # assumes the Chroma folder is "chroma_db"; shows a dash if not found
        import chromadb
        n_chunks = chromadb.PersistentClient(path="chroma_db").list_collections()[0].count()
    except Exception:
        n_chunks = "—"
    st.markdown(f'<div class="lbl">System</div><div class="sys"><span class="dot"></span>ONLINE<br>'
                f'CHUNKS {n_chunks}<br>EMBED bge-small-en-v1.5<br>MODEL {MODEL}</div>', unsafe_allow_html=True)

messages = st.session_state.chats[st.session_state.current]["messages"]

# ---------- styles + cursor effects ----------
level = {"Off": 0, "Low": 0.5, "High": 1}[fx]
off = ".stApp::before,.stApp::after{display:none}*{animation:none!important}" if fx == "Off" else ""
css = Path(__file__).with_name("styles.css").read_text(encoding="utf-8")
st.markdown(f"<style>{FONTS}:root{{--fx:{level}}}{css}{off}</style>", unsafe_allow_html=True)
fx_js = Path(__file__).with_name("fx.js").read_text(encoding="utf-8")
components.html(  # scripts can't run via st.markdown, so a hidden component injects fx.js into the page
    "<script>const p=window.parent;p.__fxLevel=" + str(level) + ";"
    "if(!p.__fxInit){const s=p.document.createElement('script');s.textContent=" + json.dumps(fx_js) + ";p.document.head.appendChild(s);}</script>",
    height=0)

# ---------- helpers ----------
def chipify(text):
    return re.sub(r"\[(\d+)\]", r'<span class="chip">\1</span>', text)

def source_cards(sources):
    out = ""
    for s in sources:
        bar = (f'<div class="rel-row"><div class="rel"><i style="width:{s["pct"]}%"></i></div>{s["pct"]}</div>'
               if s["pct"] is not None else "")
        out += (f'<div class="src"><div class="src-h">[{s["n"]}] {html.escape(s["name"])} · {s["where"]}</div>'
                f'<div class="src-t">{html.escape(s["preview"])}</div>{bar}</div>')
    return out

def render_assistant(m, key="x"):
    if m.get("artifact"):
        st.markdown(m["text"])
        st.download_button("⬇ Download .md", m["text"], file_name=m["file"],
                           mime="text/markdown", key=f"dl_{key}")
        return
    if m["refused"]:
        
        st.warning(m["text"])
    else:
        st.markdown(chipify(m["text"]), unsafe_allow_html=True)
    if m["sources"]:
        with st.expander(f"SOURCES · {len(m['sources']):02d}"):
            st.markdown(source_cards(m["sources"]), unsafe_allow_html=True)
    if m.get("footer"):
        st.markdown(f'<div class="foot">{m["footer"]}</div>', unsafe_allow_html=True)

# ---------- header ----------
st.markdown(
    '<div class="hdr"><div class="brand">'
    '<svg width="26" height="26" viewBox="0 0 26 26" fill="none" stroke="#00F0FF" stroke-width="1.2"><path d="M13 2 23 7.5v11L13 24 3 18.5v-11Z" stroke-opacity=".6"/>'
    '<circle cx="13" cy="13" r="2.5" fill="#00F0FF"/><path d="M13 13 13 2M13 13 23 18.5M13 13 3 18.5" stroke-opacity=".35"/></svg>'
    '<div><div class="ttl">DSA Notes Assistant</div><div class="tag">Answers grounded in your lecture notes</div></div></div>'
    f'<div class="meta"><span class="dot"></span>Online · {n_chunks} chunks</div></div>', unsafe_allow_html=True)

question = st.chat_input("> ask a DSA question_") or st.session_state.pop("pending", None)

# ---------- history / empty state ----------
for i, m in enumerate(messages):
    with st.chat_message(m["role"]):
        if m["role"] == "user":
            st.write(m["text"])
        else:
            render_assistant(m, key=f"{st.session_state.current}_{i}")

if not messages and not question:
    st.markdown('<div class="hero"><p>Ask a question, or start with one of these.</p></div>', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, q in enumerate(EXAMPLES):
        if cols[i % 2].button(q, key=f"ex{i}", use_container_width=True):
            st.session_state.pending = q
            st.rerun()

# ---------- new question ----------
if question:
    chat = st.session_state.chats[st.session_state.current]
    if chat["title"] == "New chat":
        chat["title"] = question[:40]
    messages.append({"role": "user", "text": question})
    with st.chat_message("user"):
        st.write(question)
        
    if question.strip().lower().startswith("/cheatsheet"):
        topic = question.strip()[len("/cheatsheet"):].strip()
        with st.chat_message("assistant"):
            if not topic:
                text = "Add a topic after the command, like `/cheatsheet merge sort`."
                st.markdown(text)
                msg = {"role": "assistant", "text": text, "sources": [], "refused": False, "footer": ""}
            else:
                with st.status(f"Building cheat sheet for {topic}...", expanded=False) as status:
                    t0 = time.perf_counter()
                    sheet = build_cheatsheet(topic)
                    status.update(label=f"Cheat sheet ready · {time.perf_counter() - t0:.0f}s", state="complete")
                msg = {"role": "assistant", "text": sheet, "artifact": True,
                       "file": topic.replace(" ", "_") + "_cheatsheet.md",
                       "sources": [], "refused": False, "footer": ""}
                render_assistant(msg, key=f"{st.session_state.current}_{len(messages)}")
        messages.append(msg)
        save_chats()
        st.stop()

    with st.chat_message("assistant"):
        t0 = time.perf_counter()
        with st.status("RETRIEVE", expanded=False) as status:
            results, best_sim = retrieve(question, k=top_k)
            ms = int((time.perf_counter() - t0) * 1000)
            status.update(label=f"RETRIEVE · {ms} ms", state="complete")

        sources, refused, footer = [], False, ""
        if best_sim < MIN_SIMILARITY:
            answer, refused = NOT_FOUND_MSG, True
        else:
            ph = st.empty()
            with ph.container():
                answer = st.write_stream(answer_stream(question, results))
            ph.empty()
            if REFUSAL in answer.lower().replace("\u2019", "'"):
                refused, answer = True, NOT_FOUND_MSG  # drop anything the model added after refusing
            else:
                cited = {int(n) for n in re.findall(r"\[(\d+)\]", answer)}
                for n, r in enumerate(results, start=1):
                    if cited and n not in cited:
                        continue
                    sim = r.get("similarity", r.get("score"))  # adjust key if your retriever names it differently
                    sources.append({
                        "n": n, "name": r["source"],
                        "where": f"page {r['page']}" if r["page"] != -1 else "code or document file",
                        "preview": r["text"][:300].replace("\n", " "),
                        "pct": round(sim * 100) if isinstance(sim, (int, float)) else None})
                footer = f"LATENCY {time.perf_counter() - t0:.1f}s · CHUNKS {len(results)} · MODEL {MODEL}"

        msg = {"role": "assistant", "text": answer, "sources": sources, "refused": refused, "footer": footer}
        render_assistant(msg)
    messages.append(msg)
    save_chats()