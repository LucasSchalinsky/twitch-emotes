import streamlit as st
from PIL import Image, ImageOps
import io
import os
import zipfile
import base64
import numpy as np

# Grid layout constants
GRID_ROWS = 5
GRID_COLS = 7
MARGIN = 150
GAP = 150
SQUARE_SIZE = 500
EMOTE_SIZES = [(128, 128), (112, 112), (56, 56), (28, 28)]
BADGE_SIZES = [(128, 128), (72, 72), (36, 36), (18, 18)]


def is_empty_cell(image_cell, threshold=0.99):
    cell_array = np.array(image_cell)
    if cell_array.ndim == 2:
        return False
    if cell_array.ndim != 3 or cell_array.shape[2] < 4:
        return False
    transparent_pixels = np.sum(cell_array[:, :, 3] == 0)
    total_pixels = cell_array.shape[0] * cell_array.shape[1]
    return (transparent_pixels / total_pixels) > threshold


def get_cell(image, idx, flipped=False):
    row_idx, col_idx = divmod(idx - 1, GRID_COLS)
    x = MARGIN + col_idx * (SQUARE_SIZE + GAP)
    y = MARGIN + row_idx * (SQUARE_SIZE + GAP)
    cell = image.crop((x, y, x + SQUARE_SIZE, y + SQUARE_SIZE))
    return ImageOps.mirror(cell) if flipped else cell

def main():
    st.set_page_config(
        page_title="A fragment of god",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.title("A fragment of god")

    if 'grid_status' not in st.session_state:
        st.session_state.grid_status = {}
    if 'grid_names' not in st.session_state:
        st.session_state.grid_names = {}
    if 'grid_flip' not in st.session_state:
        st.session_state.grid_flip = {}
    if 'processed' not in st.session_state:
        st.session_state.processed = False
    if 'non_empty_cells' not in st.session_state:
        st.session_state.non_empty_cells = {}
    if 'flair_images' not in st.session_state:
        st.session_state.flair_images = {}
    if 'theme' not in st.session_state:
        st.session_state.theme = "dark"
    if 'uploaded_file_id' not in st.session_state:
        st.session_state.uploaded_file_id = None

    def toggle_theme():
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

    if st.session_state.theme == "dark":
        bg_color = "#18181b"
        secondary_bg = "#3d3d3f"
        text_color = "#ffffff"
        username_color = "#9147ff"
    else:
        bg_color = "#ffffff"
        secondary_bg = "#f2f2f2"
        text_color = "#18181b"
        username_color = "#9147ff"

    st.markdown(f"""
    <style>
        .chat-container {{
            background-color: {bg_color};
            color: {text_color};
            border-radius: 4px;
            padding: 10px;
            margin-bottom: 20px;
            font-family: 'Inter', sans-serif;
        }}
        .chat-message {{
            padding: 4px 8px;
        }}
        .chat-message:hover {{
            background-color: {secondary_bg};
        }}
        .username {{
            color: {username_color};
            font-weight: bold;
        }}
        .theme-button {{
            background-color: #9147ff;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
        }}
        .theme-button:hover {{
            background-color: #772ce8;
        }}
    </style>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Grid image (❁´◡`❁)", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        file_id = (uploaded_file.name, uploaded_file.size)

        default_name = os.path.splitext(uploaded_file.name)[0].replace("Grid", "").strip()

        if st.session_state.uploaded_file_id != file_id:
            st.session_state.cells_detected = False
            st.session_state.uploaded_file_id = file_id

        if 'cells_detected' not in st.session_state or not st.session_state.cells_detected:
            st.session_state.non_empty_cells = {}
            st.session_state.non_empty_rows = set()

            for i in range(GRID_ROWS):
                row_has_content = False
                for j in range(GRID_COLS):
                    cell_num = i * GRID_COLS + j + 1
                    cell = get_cell(image, cell_num)
                    if not is_empty_cell(cell):
                        st.session_state.non_empty_cells[cell_num] = (i, j)
                        row_has_content = True
                if row_has_content:
                    st.session_state.non_empty_rows.add(i)

            st.session_state.cells_detected = True

        zip_name = st.text_input("Zip name /ᐠ˵- ⩊ -˵マ", value="")
        zip_display = default_name if not zip_name else zip_name
        st.caption(f"File Name: {zip_display}.zip")

        st.subheader("Download")
        col_buttons = st.columns(2)

        def _write_resized_variants(zip_file, folder, name, cell, is_flipped, sizes):
            for size in sizes:
                for flip_label, img in [("A_", cell), ("B_", ImageOps.mirror(cell))] if is_flipped else [("_", cell)]:
                    resized = img.resize(size)
                    buf = io.BytesIO()
                    resized.save(buf, format="PNG")
                    buf.seek(0)
                    suffix = "DiscordSize.png" if size[0] == 128 else f"{size[0]}x{size[1]}.png"
                    zip_file.writestr(f"{folder}{name}{flip_label}{suffix}", buf.getvalue())

        with col_buttons[0]:
            if st.button("Process images", type="primary"):
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                    for idx, status in st.session_state.grid_status.items():
                        if status == "None":
                            continue
                        name = st.session_state.grid_names.get(idx) or str(idx)
                        cell = get_cell(image, idx)
                        is_flipped = st.session_state.grid_flip.get(idx, False)
                        folder = f"{name}/"
                        orig_suffix = "A_" if is_flipped else "_"

                        orig_buffer = io.BytesIO()
                        cell.save(orig_buffer, format="PNG")
                        orig_buffer.seek(0)
                        zip_file.writestr(f"{folder}{name}{orig_suffix}Original.png", orig_buffer.getvalue())

                        if is_flipped:
                            flipped_buffer = io.BytesIO()
                            ImageOps.mirror(cell).save(flipped_buffer, format="PNG")
                            flipped_buffer.seek(0)
                            zip_file.writestr(f"{folder}{name}B_Original.png", flipped_buffer.getvalue())

                        if status == "Emote":
                            _write_resized_variants(zip_file, folder, name, cell, is_flipped, EMOTE_SIZES)
                        else:
                            _write_resized_variants(zip_file, folder, name, cell, is_flipped, BADGE_SIZES)

                zip_buffer.seek(0)
                st.session_state.zip_data = zip_buffer.getvalue()
                st.session_state.processed = True

        with col_buttons[1]:
            if st.session_state.processed:
                if zip_name:
                    download_filename = f"{zip_name}.zip"
                else:
                    download_filename = f"{default_name}.zip" if default_name else "emotes_and_badges.zip"

                st.download_button(
                    label="Download images",
                    data=st.session_state.zip_data,
                    file_name=download_filename,
                    mime="application/zip"
                )

        col1, col2 = st.columns([3, 1])

        with col1:
            with st.expander("Grid image", expanded=True):
                st.image(image, caption="Uploaded Grid", width=800)

            st.subheader("Selection of Emotes and Badges (〃￣︶￣)人(￣︶￣〃)")

            # Criar tabs apenas para as linhas não vazias
            non_empty_rows_list = sorted(st.session_state.non_empty_rows)
            tabs = st.tabs([f"Row {i+1}" for i in non_empty_rows_list])

            row_actions = [
                ("All Emotes", "Emote", "all_emotes"),
                ("All Badges", "Badge", "all_badges"),
                ("All Badge Bits", "Badge Bit", "all_badge_bits"),
                ("All Flairs", "Flair", "all_flairs"),
                ("Clear Row", "None", "clear_row"),
            ]

            for tab_idx, row_idx in enumerate(non_empty_rows_list):
                with tabs[tab_idx]:
                    row_buttons = st.columns(5)
                    for col_idx, (label, status_val, key_prefix) in enumerate(row_actions):
                        with row_buttons[col_idx]:
                            btn_label = f"{label} in Row {row_idx+1}" if status_val != "None" else f"Clear Row {row_idx+1}"
                            if st.button(btn_label, key=f"{key_prefix}_{row_idx}"):
                                for j in range(GRID_COLS):
                                    cell_num = row_idx * GRID_COLS + j + 1
                                    if cell_num in st.session_state.non_empty_cells:
                                        st.session_state[f"status_{cell_num}"] = status_val
                                        st.session_state.grid_status[cell_num] = status_val
                                st.rerun()

                    row_cells = [c for c, (r, _) in st.session_state.non_empty_cells.items() if r == row_idx]

                    if row_cells:
                        cols = st.columns(GRID_COLS)
                        for j in range(GRID_COLS):
                            cell_num = row_idx * GRID_COLS + j + 1
                            if cell_num not in st.session_state.non_empty_cells:
                                continue
                            with cols[j]:
                                is_flip = st.session_state.get(f"flip_{cell_num}", False)
                                cell = get_cell(image, cell_num, flipped=is_flip)
                                st.image(cell, width=120, caption=f"Cell #{cell_num}")

                                status = st.selectbox(
                                    "Type",
                                    ["None", "Emote", "Badge", "Badge Bit", "Flair"],
                                    key=f"status_{cell_num}"
                                )
                                st.session_state.grid_status[cell_num] = status

                                if status != "None":
                                    name = st.text_input("Name", key=f"name_{cell_num}")
                                    st.session_state.grid_names[cell_num] = name
                                    flip = st.checkbox("Flip", key=f"flip_{cell_num}")
                                    st.session_state.grid_flip[cell_num] = flip

        with col2:
            st.subheader("Chat Preview q(≧▽≦q)")

            theme_text = "Change to Light Theme" if st.session_state.theme == "dark" else "Change to Dark Theme"
            if st.button(theme_text, on_click=toggle_theme, key="theme_toggle_button"):
                pass

            st.markdown(f"""
            <style>
                /* Individual messages */
                .chat-message {{
                    background-color: {bg_color} !important;
                    padding: 4px 8px;
                    color: {text_color} !important;
                }}

                .chat-message:hover {{
                    background-color: {secondary_bg} !important;
                }}

                .username {{
                    color: {username_color} !important;
                    font-weight: bold;
                }}

                /* Ensure the text inside the chat has the correct color */
                .chat-container p, .chat-container div, .chat-container span {{
                    color: {text_color} !important;
                }}

                /* Ensure the headers inside the chat have the correct color */
                .chat-container h1, .chat-container h2, .chat-container h3,
                .chat-container h4, .chat-container h5, .chat-container h6 {{
                    color: {text_color} !important;
                }}
            </style>
            """, unsafe_allow_html=True)

            def _preview_data_uri(cell, size):
                buf = io.BytesIO()
                cell.resize(size).save(buf, format="PNG")
                return base64.b64encode(buf.getvalue()).decode()

            for idx, status in st.session_state.grid_status.items():
                if status == "None":
                    continue
                cell = get_cell(image, idx, flipped=st.session_state.grid_flip.get(idx, False))
                preview_size = (28, 28) if status == "Emote" else (18, 18)
                img_str = _preview_data_uri(cell, preview_size)
                if status in ["Badge", "Badge Bit"]:
                    st.markdown(f'<div class="chat-message"><img src="data:image/png;base64,{img_str}"> <span class="username">Wanzin__</span>: <span style="color:{text_color}">I love you!</span></div>', unsafe_allow_html=True)
                elif status == "Emote":
                    st.markdown(f'<div class="chat-message"><span class="username">Wanzin__</span>: <img src="data:image/png;base64,{img_str}"></div>', unsafe_allow_html=True)

            st.markdown('<h4>All Emotes:</h4>', unsafe_allow_html=True)
            emote_parts = []
            for idx, status in st.session_state.grid_status.items():
                if status == "Emote":
                    cell = get_cell(image, idx, flipped=st.session_state.grid_flip.get(idx, False))
                    emote_parts.append(f' <img src="data:image/png;base64,{_preview_data_uri(cell, (28, 28))}">')
            if emote_parts:
                st.markdown(f'<div class="chat-message"><span class="username">Wanzin__</span>:{"".join(emote_parts)}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message"><span style="color:{text_color}">No Emote selected.</span></div>', unsafe_allow_html=True)

            st.markdown('<h4>Todas as Badges:</h4>', unsafe_allow_html=True)

            badges = []
            badge_bits = []
            flairs = []
            for idx, status in st.session_state.grid_status.items():
                if status not in ("Badge", "Badge Bit", "Flair"):
                    continue
                cell = get_cell(image, idx, flipped=st.session_state.grid_flip.get(idx, False))
                if status == "Badge":
                    badges.append(cell)
                elif status == "Badge Bit":
                    badge_bits.append(cell)
                else:
                    flairs.append(cell)

            if badges or badge_bits:
                # Badges normais
                if badges:
                    badge_html = ""
                    for badge in badges:
                        badge_preview = badge.resize((18, 18))
                        badge_buffer = io.BytesIO()
                        badge_preview.save(badge_buffer, format="PNG")
                        badge_img_str = base64.b64encode(badge_buffer.getvalue()).decode()
                        badge_html += f'<img src="data:image/png;base64,{badge_img_str}"> '

                    if flairs or badge_bits:
                        st.markdown(f'<h4>Normal Badges:</h4>', unsafe_allow_html=True)
                        st.markdown(f'<div class="chat-message">{badge_html} <span class="username">Wanzin__</span>: <span style="color:{text_color}">Normal Badges</span></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="chat-message">{badge_html} <span class="username">Wanzin__</span>: <span style="color:{text_color}">Im full of badges!</span></div>', unsafe_allow_html=True)

                # Badge Bits (Badge na esquerda + Badge Bit na direita)
                if badge_bits and badges:
                    st.markdown(f'<h4>Badges with Badge Bits:</h4>', unsafe_allow_html=True)
                    
                    for badge_bit in badge_bits:
                        badge_bit_html = ""
                        
                        for badge in badges:
                            badge_preview = badge.resize((18, 18))
                            badge_bit_preview = badge_bit.resize((18, 18))

                            # Criar imagem combinada: Badge na esquerda, Badge Bit na direita
                            combined = Image.new('RGBA', (36, 18), (0, 0, 0, 0))
                            combined.paste(badge_preview, (0, 0), badge_preview)
                            combined.paste(badge_bit_preview, (18, 0), badge_bit_preview)

                            combined_buffer = io.BytesIO()
                            combined.save(combined_buffer, format="PNG")
                            combined_img_str = base64.b64encode(combined_buffer.getvalue()).decode()

                            badge_bit_html += f'<img src="data:image/png;base64,{combined_img_str}"> '

                        st.markdown(f'<div class="chat-message">{badge_bit_html} <span class="username">Wanzin__</span>: <span style="color:{text_color}">Badges with Badge Bit</span></div>', unsafe_allow_html=True)

                # Badges com Flairs
                if flairs and badges:
                    st.markdown(f'<h4>Badges with Flairs:</h4>', unsafe_allow_html=True)

                    for flair in flairs:
                        flair_badge_html = ""

                        for badge in badges:
                            badge_preview = badge.resize((18, 18))
                            flair_preview = flair.resize((18, 18))

                            combined = Image.new('RGBA', (18, 18), (0, 0, 0, 0))
                            combined.paste(badge_preview, (0, 0), badge_preview)
                            combined.paste(flair_preview, (0, 0), flair_preview)

                            combined_buffer = io.BytesIO()
                            combined.save(combined_buffer, format="PNG")
                            combined_img_str = base64.b64encode(combined_buffer.getvalue()).decode()

                            flair_badge_html += f'<img src="data:image/png;base64,{combined_img_str}"> '

                        st.markdown(f'<div class="chat-message">{flair_badge_html} <span class="username">Wanzin__</span>: <span style="color:{text_color}">Badges with Flair</span></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message"><span style="color:{text_color}">No Badge selected.</span></div>', unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Normal vs Flip (￣_,￣ )")

        flipped_items = [
            idx for idx in st.session_state.grid_status
            if st.session_state.grid_flip.get(idx) and st.session_state.grid_status[idx] in ("Emote", "Badge", "Badge Bit", "Flair")
        ]

        if flipped_items:
            items_per_row = 5
            for i in range(0, len(flipped_items), items_per_row):
                row_items = flipped_items[i : i + items_per_row]
                cols = st.columns(10)
                for j, idx in enumerate(row_items):
                    cell = get_cell(image, idx)
                    col_idx = j * 2
                    with cols[col_idx]:
                        st.markdown("**Normal**")
                        st.image(cell, width=150)
                    with cols[col_idx + 1]:
                        st.markdown("**Flipped**")
                        st.image(ImageOps.mirror(cell), width=150)
                st.markdown("---")
        else:
            st.markdown("No emote or badge flipped yet.")

if __name__ == "__main__":
    main()