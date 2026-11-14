from datetime import datetime
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------
# Config
# ---------------------------------------------------------------
st.set_page_config(
    page_title="File Manager Pro",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

WORKSPACE = Path("workspace")
WORKSPACE.mkdir(exist_ok=True)

# ---------------------------------------------------------------
# Styling
# ---------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #1e1b4b 0%, #0f172a 45%, #020617 100%);
    }
    #MainMenu, footer {visibility: hidden;}

    .hero {
        padding: 2.2rem 2.5rem;
        border-radius: 22px;
        background: linear-gradient(120deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        box-shadow: 0 20px 45px rgba(99, 102, 241, 0.35);
        margin-bottom: 1.6rem;
    }
    .hero h1 {color: #fff; font-size: 2.4rem; margin: 0; font-weight: 800;}
    .hero p {color: rgba(255,255,255,0.88); margin: 0.4rem 0 0; font-size: 1.05rem;}

    .stat-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 18px;
        padding: 1.2rem 1.4rem;
        backdrop-filter: blur(8px);
        transition: transform .2s ease, border-color .2s ease;
    }
    .stat-card:hover {transform: translateY(-4px); border-color: #8b5cf6;}
    .stat-icon {font-size: 1.6rem;}
    .stat-value {font-size: 2rem; font-weight: 800; color: #fff; line-height: 1.1;}
    .stat-label {color: #94a3b8; font-size: .85rem; text-transform: uppercase; letter-spacing: .08em;}

    .section-title {
        color: #e2e8f0; font-size: 1.35rem; font-weight: 700;
        margin: 1.4rem 0 .6rem;
    }
    .pill {
        display: inline-block; padding: .2rem .7rem; border-radius: 999px;
        background: rgba(139,92,246,.18); color: #c4b5fd;
        font-size: .78rem; font-weight: 600; margin-right: .4rem;
    }
    div[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.95);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    .stButton > button, .stDownloadButton > button {
        border-radius: 12px; font-weight: 600; padding: .55rem 1.4rem;
        border: none; color: white;
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        transition: all .2s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(139,92,246,.45);
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------
def safe_path(name: str) -> Path | None:
    """Resolve a name inside the workspace; block path traversal."""
    name = name.strip()
    if not name:
        return None
    target = (WORKSPACE / name).resolve()
    if WORKSPACE.resolve() not in target.parents:
        return None
    return target


def list_files() -> list[Path]:
    return sorted(p for p in WORKSPACE.rglob("*") if p.is_file())


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024 # type: ignore
    return f"{n:.1f} TB"


def rel(p: Path) -> str:
    return str(p.relative_to(WORKSPACE))


def stat_card(icon: str, value: str, label: str):
    st.markdown(
        f"""<div class="stat-card">
        <div class="stat-icon">{icon}</div>
        <div class="stat-value">{value}</div>
        <div class="stat-label">{label}</div></div>""",
        unsafe_allow_html=True,
    )


def pick_file(label: str, key: str):
    files = list_files()
    if not files:
        st.info("The workspace is empty. Create a file first ✨")
        return None
    choice = st.selectbox(label, [rel(f) for f in files], key=key)
    return WORKSPACE / choice


# ---------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🗂️ File Manager Pro")
    st.caption("A CRUD playground built with Python & Streamlit")
    page = st.radio(
        "Navigate",
        ["📊 Dashboard", "➕ Create", "📖 Read", "✏️ Update", "🗑️ Delete"],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown(
        '<span class="pill">Python</span><span class="pill">Streamlit</span><span class="pill">pathlib</span>',
        unsafe_allow_html=True,
    )
    st.caption("All operations run inside the sandboxed `workspace/` folder.")

# ---------------------------------------------------------------
# Hero
# ---------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>🗂️ File Manager Pro</h1>
        <p>Create, read, update and delete files with a clean, modern interface.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------
# Pages
# ---------------------------------------------------------------
if page == "📊 Dashboard":
    files = list_files()
    folders = [p for p in WORKSPACE.rglob("*") if p.is_dir()]
    total = sum(f.stat().st_size for f in files)
    latest = max(files, key=lambda f: f.stat().st_mtime) if files else None

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("📄", str(len(files)), "Files")
    with c2:
        stat_card("📁", str(len(folders)), "Folders")
    with c3:
        stat_card("💾", human_size(total), "Total size")
    with c4:
        stat_card("🕒", latest.name if latest else "—", "Last modified")

    st.markdown('<div class="section-title">Workspace explorer</div>', unsafe_allow_html=True)
    if files:
        rows = [
            {
                "#": i + 1,
                "Name": rel(f),
                "Type": f.suffix or "—",
                "Size": human_size(f.stat().st_size),
                "Modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%d %b %Y, %H:%M"),
            }
            for i, f in enumerate(files)
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("No files yet. Head over to **Create** to add your first one 🚀")

elif page == "➕ Create":
    st.markdown('<div class="section-title">Create a new file</div>', unsafe_allow_html=True)
    with st.form("create_form", clear_on_submit=True):
        name = st.text_input("File name", placeholder="notes.txt")
        content = st.text_area("Content", height=220, placeholder="Write something awesome...")
        submitted = st.form_submit_button("Create file")
    if submitted:
        p = safe_path(name)
        if p is None:
            st.error("Please enter a valid file name.")
        elif p.exists():
            st.warning(f"`{name}` already exists. Use **Update** to modify it.")
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            st.toast(f"Created {name}", icon="✅")
            st.success(f"File `{name}` created successfully.")
            st.balloons()

elif page == "📖 Read":
    st.markdown('<div class="section-title">Read a file</div>', unsafe_allow_html=True)
    p = pick_file("Select a file", "read_sel")
    if p:
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            st.error("This file is not a readable text file.")
        else:
            m1, m2, m3 = st.columns(3)
            m1.metric("Size", human_size(p.stat().st_size))
            m2.metric("Lines", len(text.splitlines()))
            m3.metric("Characters", len(text))
            st.code(text or "(empty file)", language=p.suffix.lstrip(".") or "text")
            st.download_button("⬇️ Download", text, file_name=p.name)

elif page == "✏️ Update":
    st.markdown('<div class="section-title">Update a file</div>', unsafe_allow_html=True)
    p = pick_file("Select a file", "upd_sel")
    if p:
        mode = st.radio(
            "Action",
            ["Rename", "Overwrite content", "Append content"],
            horizontal=True,
        )
        if mode == "Rename":
            new_name = st.text_input("New name", value=rel(p))
            if st.button("Rename file"):
                target = safe_path(new_name)
                if target is None:
                    st.error("Invalid name.")
                elif target.exists():
                    st.warning("A file with that name already exists.")
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    p.rename(target)
                    st.toast("Renamed", icon="✅")
                    st.success(f"Renamed to `{new_name}`.")
        elif mode == "Overwrite content":
            current = p.read_text(encoding="utf-8", errors="ignore")
            new = st.text_area("New content (replaces everything)", value=current, height=240)
            if st.button("Overwrite file"):
                p.write_text(new, encoding="utf-8")
                st.toast("File overwritten", icon="✅")
                st.success("Content updated.")
        else:
            extra = st.text_area("Text to append", height=160)
            if st.button("Append to file"):
                with open(p, "a", encoding="utf-8") as f:
                    f.write(" " + extra)
                st.toast("Content appended", icon="✅")
                st.success("Content appended.")

elif page == "🗑️ Delete":
    st.markdown('<div class="section-title">Delete a file</div>', unsafe_allow_html=True)
    p = pick_file("Select a file to delete", "del_sel")
    if p:
        st.warning(f"You are about to permanently delete **{rel(p)}**.")
        confirm = st.checkbox("Yes, I understand this can't be undone")
        if st.button("Delete file", disabled=not confirm):
            p.unlink()
            st.toast("File deleted", icon="🗑️")
            st.success(f"`{rel(p)}` has been deleted.")
            st.rerun()