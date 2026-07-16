"""FolderWise AI - a local-first file organizer.

Run with: streamlit run app.py
"""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from config import CATEGORY_ORDER, INSTRUCTION_EXAMPLES, PAYHIP_PRO_URL
from organizer import (
    build_plan,
    execute_plan,
    human_size,
    undo_last,
)

# ---------------------------------------------------------------------------
# Page config & styling
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="FolderWise AI",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CUSTOM_CSS = """
<style>
:root {
    --fw-orange: #FF6A00;
    --fw-orange-soft: #FFF3E8;
    --fw-orange-dark: #E05A00;
    --fw-ink: #1A1A1A;
    --fw-muted: #6B7280;
    --fw-line: #ECECEC;
    --fw-card: #FFFFFF;
    --fw-bg: #FAFAFA;
}

html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
    color: var(--fw-ink) !important;
}

.stApp {
    background: var(--fw-bg);
    color: var(--fw-ink) !important;
}

/* Force readable text colors on every Streamlit text element */
.stApp, .stApp p, .stApp span, .stApp div, .stApp label,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stMarkdown, .stMarkdown p, .stMarkdown span,
.stTextInput, .stTextInput label, .stTextInput input,
.stSelectbox, .stSelectbox label,
.stRadio, .stRadio label,
.stButton, .stButton label,
.stExpander, .stExpander header,
.stInfo, .stSuccess, .stWarning, .stError {
    color: var(--fw-ink) !important;
}

/* Inputs: dark text on white */
.stApp input, .stApp textarea, .stApp .stTextInput input {
    color: var(--fw-ink) !important;
    background: #fff !important;
}
.stApp input::placeholder, .stApp textarea::placeholder {
    color: #9CA3AF !important;
}

/* Muted helper text stays grey but never blends */
.stApp .fw-muted, .stApp [data-testid="stCaptionContainer"] {
    color: var(--fw-muted) !important;
}

/* Expander headers and selectbox/radio labels */
.stApp [data-testid="stExpander"] details summary,
.stApp [data-testid="stExpander"] details summary p,
.stApp [data-baseweb="select"] > div,
.stApp [data-baseweb="radio"] label,
.stApp [data-baseweb="radio"] .st-bf,
.stApp [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stWidgetLabel"] {
    color: var(--fw-ink) !important;
}

/* Expander body text */
.stApp [data-testid="stExpander"] details div p,
.stApp [data-testid="stExpander"] details div span {
    color: var(--fw-ink) !important;
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; }

.fw-card {
    background: var(--fw-card);
    border: 1px solid var(--fw-line);
    border-radius: 18px;
    padding: 22px 24px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.04);
}

.fw-card-accent {
    background: linear-gradient(135deg, #FF6A00 0%, #FF8A3D 100%);
    border-radius: 18px;
    padding: 24px;
    color: #fff;
    box-shadow: 0 8px 24px rgba(255,106,0,0.28);
}

.fw-title {
    font-size: 26px;
    font-weight: 800;
    color: var(--fw-ink);
    margin: 0;
}
.fw-subtitle {
    font-size: 14px;
    color: var(--fw-muted);
    margin: 4px 0 0 0;
}

.fw-label {
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--fw-muted);
}

.fw-chip {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    background: var(--fw-orange-soft);
    color: var(--fw-orange-dark);
    font-size: 12px;
    font-weight: 600;
    margin: 2px 4px 2px 0;
}

.fw-cat-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px;
    border-radius: 12px;
    background: #FAFAFA;
    margin-bottom: 6px;
}
.fw-cat-row:hover { background: var(--fw-orange-soft); }

.fw-bar-track {
    width: 100%;
    height: 8px;
    background: #F0F0F0;
    border-radius: 999px;
    overflow: hidden;
}
.fw-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #FF6A00, #FF9A4D);
    border-radius: 999px;
    transition: width 0.4s ease;
}

.fw-btn-primary button {
    background: var(--fw-orange) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    padding: 10px 20px !important;
    width: 100%;
    transition: background 0.2s ease;
}
.fw-btn-primary button:hover { background: var(--fw-orange-dark) !important; }

.fw-btn-ghost button {
    background: transparent !important;
    color: var(--fw-orange-dark) !important;
    border: 1.5px solid var(--fw-orange) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    width: 100%;
}
.fw-btn-ghost button:hover { background: var(--fw-orange-soft) !important; }

.fw-upgrade-btn button {
    background: #fff !important;
    color: var(--fw-orange-dark) !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    padding: 12px 0 !important;
    width: 100%;
    font-size: 15px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    transition: transform 0.15s ease;
}
.fw-upgrade-btn button:hover { transform: translateY(-1px); }

.fw-pro-feature {
    font-size: 13px;
    color: rgba(255,255,255,0.92);
    margin: 6px 0;
    display: flex;
    align-items: center;
}
.fw-pro-feature::before {
    content: "✓";
    margin-right: 8px;
    font-weight: 800;
}

.fw-section-title {
    font-size: 16px;
    font-weight: 700;
    color: var(--fw-ink);
    margin: 0 0 12px 0;
}

.fw-file-list {
    max-height: 260px;
    overflow-y: auto;
    border-radius: 12px;
}
.fw-file-list::-webkit-scrollbar { width: 6px; }
.fw-file-list::-webkit-scrollbar-thumb { background: #ddd; border-radius: 999px; }

.fw-file-row {
    display: flex;
    justify-content: space-between;
    padding: 7px 12px;
    font-size: 13px;
    border-bottom: 1px solid #F4F4F4;
}
.fw-file-name { color: var(--fw-ink); font-weight: 500; }
.fw-file-meta { color: var(--fw-muted); }

.fw-empty {
    text-align: center;
    color: var(--fw-muted);
    padding: 30px 10px;
    font-size: 14px;
}

.fw-success {
    background: #E9F9EF;
    border: 1px solid #BFE9D0;
    border-radius: 14px;
    padding: 14px 18px;
    color: #137A3A;
    font-weight: 600;
}
.fw-warn {
    background: #FFF3E8;
    border: 1px solid #FFD9B8;
    border-radius: 14px;
    padding: 14px 18px;
    color: #9A4A00;
    font-weight: 500;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "plan" not in st.session_state:
    st.session_state.plan = None
if "executed" not in st.session_state:
    st.session_state.executed = False
if "last_undo" not in st.session_state:
    st.session_state.last_undo = None


def reset_plan_state() -> None:
    st.session_state.plan = None
    st.session_state.executed = False


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

# Header
st.markdown(
    """
    <div style="display:flex; align-items:center; gap:14px; margin-bottom:6px;">
        <div style="font-size:34px;">🗂️</div>
        <div>
            <p class="fw-title">FolderWise AI</p>
            <p class="fw-subtitle">Organize any folder locally — no cloud, no uploads, fully offline.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

left_col, right_col = st.columns([2.3, 1], gap="large")

# ---------------------------------------------------------------------------
# Left column: main workflow
# ---------------------------------------------------------------------------

with left_col:
    # Step 1: folder picker
    st.markdown('<p class="fw-label">1 · Choose a folder</p>', unsafe_allow_html=True)
    col_pick, col_quick = st.columns([1, 1], gap="medium")
    with col_pick:
        folder_path = st.text_input(
            "Folder path",
            value=os.path.expanduser("~") if "HOME" in os.environ else "",
            placeholder="/Users/you/Desktop or C:\\Users\\you\\Downloads",
            label_visibility="collapsed",
        )
    with col_quick:
        # Quick-pick common directories
        quick_dirs = []
        for name, env in [("Home", "HOME"), ("Desktop", None), ("Downloads", None)]:
            base = os.path.expanduser("~")
            candidate = os.path.join(base, name) if env else os.path.join(base, name)
            if os.path.isdir(candidate):
                quick_dirs.append((name, candidate))
        if quick_dirs:
            picked = st.selectbox(
                "Quick pick",
                options=["— pick a folder —"] + [d[0] for d in quick_dirs],
                label_visibility="collapsed",
            )
            if picked != "— pick a folder —":
                folder_path = next(d[1] for d in quick_dirs if d[0] == picked)

    valid_folder = bool(folder_path) and os.path.isdir(folder_path)
    if folder_path and not valid_folder:
        st.markdown(
            '<div class="fw-warn">That path does not exist. Please enter a valid directory.</div>',
            unsafe_allow_html=True,
        )

    # Step 2: instruction
    st.markdown('<p class="fw-label" style="margin-top:14px;">2 · What should I organize?</p>', unsafe_allow_html=True)
    instruction = st.text_input(
        "Instruction",
        placeholder="e.g. Organize images, Organize CAD files, Organize everything…",
        label_visibility="collapsed",
    )
    chips_html = "".join(f'<span class="fw-chip">{ex}</span>' for ex in INSTRUCTION_EXAMPLES)
    st.markdown(chips_html, unsafe_allow_html=True)

    # Step 2b: organization mode
    st.markdown('<p class="fw-label" style="margin-top:14px;">3 · Where should files go?</p>', unsafe_allow_html=True)
    mode_col, name_col = st.columns([1, 1.4], gap="medium")
    with mode_col:
        organize_mode = st.radio(
            "Mode",
            options=["subfolder", "inplace"],
            format_func=lambda x: "New subfolder" if x == "subfolder" else "In this folder",
            horizontal=True,
            label_visibility="collapsed",
        )
    with name_col:
        if organize_mode == "subfolder":
            subfolder_name = st.text_input(
                "Subfolder name",
                value="FolderWise_AI_Organized",
                placeholder="FolderWise_AI_Organized",
                label_visibility="collapsed",
            )
        else:
            subfolder_name = ""
            st.markdown(
                '<p style="font-size:13px; color:var(--fw-muted); padding-top:8px;">'
                'Files will be sorted into category folders directly inside the chosen directory.</p>',
                unsafe_allow_html=True,
            )

    # Step 4: organize button
    st.markdown('<div class="fw-btn-primary" style="margin-top:14px;">', unsafe_allow_html=True)
    preview_clicked = st.button("🗂️  Organize Folder", disabled=not valid_folder, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Build preview plan
    if preview_clicked and valid_folder:
        st.session_state.plan = build_plan(folder_path, instruction, organize_mode, subfolder_name)
        st.session_state.executed = False
        st.session_state.last_undo = None

    plan = st.session_state.plan

    # ---------------------------------------------------------------------------
    # Preview panel
    # ---------------------------------------------------------------------------
    if plan is not None:
        st.markdown('<div class="fw-card" style="margin-top:18px;">', unsafe_allow_html=True)
        st.markdown(
            '<p class="fw-section-title">📋 Preview — nothing is moved yet</p>',
            unsafe_allow_html=True,
        )

        if plan.total_files == 0:
            st.markdown(
                '<div class="fw-empty">No files found in this folder. Pick a different directory.</div>',
                unsafe_allow_html=True,
            )
        else:
            # New folders
            st.markdown('<p class="fw-label">Folders that will be created</p>', unsafe_allow_html=True)
            if plan.new_folders:
                st.markdown(
                    "".join(f'<span class="fw-chip">{Path(f).name}</span>' for f in plan.new_folders),
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="fw-empty">No new folders needed — files are already organized.</div>',
                    unsafe_allow_html=True,
                )

            # File moves per group
            group_label = "extension" if plan.grouping == "extension" else "category"
            st.markdown(f'<p class="fw-label" style="margin-top:14px;">Files that will be moved (by {group_label})</p>', unsafe_allow_html=True)
            for group_key, files in plan.by_category.items():
                if not files:
                    continue
                label = plan.folder_labels.get(group_key, group_key)
                with st.expander(f"{label} — {len(files)} file(s), {human_size(sum(f.size for f in files))}", expanded=False):
                    rows = "".join(
                        f'<div class="fw-file-row">'
                        f'<span class="fw-file-name">{f.name}</span>'
                        f'<span class="fw-file-meta">{human_size(f.size)} → {label}/</span>'
                        f'</div>'
                        for f in files
                    )
                    st.markdown(f'<div class="fw-file-list">{rows}</div>', unsafe_allow_html=True)

            # Totals
            st.markdown(
                f'<div style="margin-top:12px; font-size:13px; color:var(--fw-muted);">'
                f'<b>{plan.total_files}</b> files · <b>{human_size(plan.total_size)}</b> total</div>',
                unsafe_allow_html=True,
            )

            # Confirmation
            if not st.session_state.executed:
                st.markdown('<div class="fw-warn" style="margin-top:14px;">'
                            'Review the preview above. Confirm below to move the files.</div>',
                            unsafe_allow_html=True)
                col_c1, col_c2 = st.columns(2, gap="medium")
                with col_c1:
                    if st.button("✅ Confirm & Move Files", use_container_width=True, type="primary"):
                        manifest = execute_plan(plan)
                        st.session_state.executed = True
                        st.success(f"Done! Moved {len(manifest['moves'])} files into organized folders.")
            else:
                st.markdown('<div class="fw-success">✓ Organization complete. Use "Undo Last Organization" to revert.</div>',
                            unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------------------------------------------------
    # Undo
    # ---------------------------------------------------------------------------
    st.markdown('<div class="fw-card" style="margin-top:18px;">', unsafe_allow_html=True)
    st.markdown('<p class="fw-section-title">↩️ Undo</p>', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:13px; color:var(--fw-muted); margin:0 0 12px 0;">'
        'Restores every file to its original location and removes the organized folders.</p>',
        unsafe_allow_html=True,
    )
    undo_disabled = not valid_folder
    st.markdown('<div class="fw-btn-ghost">', unsafe_allow_html=True)
    if st.button("Undo Last Organization", disabled=undo_disabled, use_container_width=True):
        result = undo_last(folder_path)
        if result is None:
            st.info("Nothing to undo — no previous organization found for this folder.")
        else:
            st.session_state.last_undo = result
            reset_plan_state()
            st.success(f"Undone! Restored {len(result['moves'])} files to their original locations.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Right column: storage summary + upgrade card
# ---------------------------------------------------------------------------

with right_col:
    # Storage summary
    st.markdown('<div class="fw-card">', unsafe_allow_html=True)
    st.markdown('<p class="fw-section-title">📊 Storage by type</p>', unsafe_allow_html=True)

    if valid_folder:
        from organizer import scan_directory
        files = scan_directory(folder_path)
        if not files:
            st.markdown('<div class="fw-empty">No files in this folder yet.</div>', unsafe_allow_html=True)
        else:
            total_size = sum(f.size for f in files) or 1
            by_cat: dict[str, int] = {c: 0 for c in CATEGORY_ORDER}
            for f in files:
                by_cat[f.category] += f.size
            for cat in CATEGORY_ORDER:
                size = by_cat[cat]
                if size == 0:
                    continue
                pct = size / total_size * 100
                st.markdown(
                    f'<div style="margin-bottom:10px;">'
                    f'<div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;">'
                    f'<span style="font-weight:600; color:var(--fw-ink);">{cat}</span>'
                    f'<span style="color:var(--fw-muted);">{human_size(size)}</span>'
                    f'</div>'
                    f'<div class="fw-bar-track"><div class="fw-bar-fill" style="width:{pct:.1f}%"></div></div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            st.markdown(
                f'<div style="margin-top:10px; font-size:12px; color:var(--fw-muted);">'
                f'{len(files)} files · {human_size(total_size)} total</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown('<div class="fw-empty">Pick a folder to see the breakdown.</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Upgrade card
    st.markdown('<div class="fw-card-accent" style="margin-top:18px;">', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:20px; font-weight:800; margin:0;">⭐ FolderWise App</p>'
        '<p style="font-size:13px; color:rgba(255,255,255,0.9); margin:6px 0 14px 0;">'
        'Unlock the offline desktop app and download for your PC at $1.</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="fw-pro-feature">Offline desktop app</div>'
        '<div class="fw-pro-feature">Content-aware smart folders</div>'
        '<div class="fw-pro-feature">Batch & scheduled organization</div>'
        '<div class="fw-pro-feature">suggest me for improved feautures</div>'
        '<div class="fw-pro-feature">easy to use</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="fw-upgrade-btn" style="margin-top:16px;">', unsafe_allow_html=True)
    st.link_button("⬇  Download app", url=PAYHIP_PRO_URL, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
