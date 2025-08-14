import streamlit as st
from PIL import Image, ImageOps
import io
import os
import zipfile
import base64
import numpy as np

def is_empty_cell(image_cell, threshold=0.99):
    cell_array = np.array(image_cell)
    if cell_array.shape[2] < 4:
        return False
    transparent_pixels = np.sum(cell_array[:, :, 3] == 0)
    total_pixels = cell_array.shape[0] * cell_array.shape[1]
    return transparent_pixels / total_pixels > threshold

def process_cell_sizes(status, is_flipped, cell, name, zip_file, folder):
    """Extract repeated cell processing logic"""
    sizes = [(128, 128), (112, 112), (56, 56), (28, 28)] if status == "Emote" else [(128, 128), (72, 72), (36, 36), (18, 18)]
    
    for size in sizes:
        # Normal version
        resized = cell.resize(size)
        buffer = io.BytesIO()
        resized.save(buffer, format="PNG")
        buffer.seek(0)
        
        suffix = "A_" if is_flipped else "_"
        filename = f"{name}{suffix}DiscordSize.png" if size[0] == 128 else f"{name}{suffix}{size[0]}x{size[1]}.png"
        zip_file.writestr(f"{folder}{filename}", buffer.getvalue())
        
        # Flipped version if needed
        if is_flipped:
            flipped_resized = ImageOps.mirror(cell).resize(size)
            flipped_buffer = io.BytesIO()
            flipped_resized.save(flipped_buffer, format="PNG")
            flipped_buffer.seek(0)
            
            flipped_filename = f"{name}B_DiscordSize.png" if size[0] == 128 else f"{name}B_{size[0]}x{size[1]}.png"
            zip_file.writestr(f"{folder}{flipped_filename}", flipped_buffer.getvalue())

def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'grid_status': {},
        'grid_names': {},
        'grid_flip': {},
        'processed': False,
        'non_empty_cells': {},
        'flair_images': {},
        'theme': "dark",
        'cells_detected': False,
        'non_empty_rows': set()
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_theme_colors(theme):
    """Return theme colors based on current theme"""
    if theme == "dark":
        return {
            'bg_color': "#18181b",
            'secondary_bg': "#3d3d3f", 
            'text_color': "#ffff",
            'username_color': "#9147ff"
        }
    else:
        return {
            'bg_color': "#ffff",
            'secondary_bg': "#f2f2f2",
            'text_color': "#18181b", 
            'username_color': "#9147ff"
        }

def apply_theme_css(colors):
    """Apply CSS styling based on theme colors"""
    st.markdown(f"""
    <style>
    .chat-container {{
        background-color: {colors['bg_color']};
        color: {colors['text_color']};
        border-radius: 4px;
        padding: 10px;
        margin-bottom: 20px;
        font-family: 'Inter', sans-serif;
    }}
    .chat-message {{
        background-color: {colors['bg_color']} !important;
        padding: 4px 8px;
        color: {colors['text_color']} !important;
    }}
    .chat-message:hover {{
        background-color: {colors['secondary_bg']} !important;
    }}
    .username {{
        color: {colors['username_color']} !important;
        font-weight: bold;
    }}
    .chat-container p, .chat-container div, .chat-container span,
    .chat-container h1, .chat-container h2, .chat-container h3,
    .chat-container h4, .chat-container h5, .chat-container h6 {{
        color: {colors['text_color']} !important;
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

def get_cell_position_and_size(row_idx, col_idx, grid_rows=5, grid_cols=7):
    """Get cell position and size based on row and column indices"""
    margin = 150
    gap = 150
    square_size = 500
    
    if row_idx >= 3:
        small_margin = 175
        small_square_size = 300
        x = small_margin + col_idx * (small_square_size + gap)
        
        if row_idx == 3:
            y = margin + 3 * (square_size + gap)
        else:
            y = margin + 3 * (square_size + gap) + small_square_size + gap
        
        return x, y, small_square_size
    else:
        x = margin + col_idx * (square_size + gap)
        y = margin + row_idx * (square_size + gap)
        return x, y, square_size

def detect_non_empty_cells(image, grid_rows=5, grid_cols=7, margin=150, gap=150, square_size=500):
    """Detect non-empty cells in the grid"""
    if st.session_state.cells_detected:
        return
    
    st.session_state.non_empty_cells = {}
    st.session_state.non_empty_rows = set()
    
    for i in range(grid_rows):
        row_has_content = False
        
        # Determine number of columns for this row
        current_cols = 10 if i >= 3 else grid_cols  # Bottom 2 rows have 10 columns
        
        for j in range(current_cols):
            cell_num = i * 10 + j + 1 if i >= 3 else i * grid_cols + j + 1  # Adjust cell numbering
            x, y, cell_size = get_cell_position_and_size(i, j, grid_rows, grid_cols)
            cell = image.crop((x, y, x + cell_size, y + cell_size))
            
            if not is_empty_cell(cell):
                st.session_state.non_empty_cells[cell_num] = (i, j)
                row_has_content = True
        
        if row_has_content:
            st.session_state.non_empty_rows.add(i)
    
    st.session_state.cells_detected = True

def main():
    st.set_page_config(
        page_title="Um fragmento de deus",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.title("Um fragmento de deus")

    initialize_session_state()
    
    def toggle_theme():
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

    colors = get_theme_colors(st.session_state.theme)
    apply_theme_css(colors)

    uploaded_file = st.file_uploader("Imagenzinha da grid mo (❁´◡`❁)", type=["png", "jpg", "jpeg"])

    if uploaded_file is None:
        return

    image = Image.open(uploaded_file)

    grid_rows = 5
    grid_cols = 7

    margin = 150
    gap = 150
    square_size = 500

    default_name = uploaded_file.name
    default_name = os.path.splitext(default_name)[0]
    default_name = default_name.replace("Grid", "").strip()

    detect_non_empty_cells(image, grid_rows, grid_cols, margin, gap, square_size)

    zip_name = st.text_input("Nome do Zip /ᐠ˵- ⩊ -˵マ", value="")
    f"O nome do Zip vai ser: {default_name if not zip_name else zip_name}.zip（￣︶￣）↗"

    st.subheader("Download")
    col_buttons = st.columns(2)

    with col_buttons[0]:
        if st.button("Processar as Imagenzinhas", type="primary"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for idx, status in st.session_state.grid_status.items():
                    if status == "None":
                        continue
                    
                    # Get cell position based on the new layout
                    if idx in st.session_state.non_empty_cells:
                        row_idx, col_idx = st.session_state.non_empty_cells[idx]
                        x, y, cell_size = get_cell_position_and_size(row_idx, col_idx, grid_rows, grid_cols)
                    else:
                        continue

                    name = st.session_state.grid_names.get(idx, str(idx)) or str(idx)
                    cell = image.crop((x, y, x + cell_size, y + cell_size))
                    folder = f"{name}/"
                    is_flipped = st.session_state.grid_flip.get(idx, False)

                    # Save original
                    original_suffix = "A_" if is_flipped else "_"
                    orig_buffer = io.BytesIO()
                    cell.save(orig_buffer, format="PNG")
                    orig_buffer.seek(0)
                    zip_file.writestr(f"{folder}{name}{original_suffix}Original.png", orig_buffer.getvalue())

                    if is_flipped:
                        flipped_original_cell = ImageOps.mirror(cell)
                        orig_flipped_buffer = io.BytesIO()
                        flipped_original_cell.save(orig_flipped_buffer, format="PNG")
                        orig_flipped_buffer.seek(0)
                        zip_file.writestr(f"{folder}{name}B_Original.png", orig_flipped_buffer.getvalue())

                    # Process different sizes
                    process_cell_sizes(status, is_flipped, cell, name, zip_file, folder)

            zip_buffer.seek(0)
            st.session_state.zip_data = zip_buffer.getvalue()
            st.session_state.processed = True

    with col_buttons[1]:
        if st.session_state.processed:
            download_filename = f"{zip_name or default_name or 'emotes_and_badges'}.zip"

            st.download_button(
                label="Baixar as Imagenzinhas",
                data=st.session_state.zip_data,
                file_name=download_filename,
                mime="application/zip"
            )

    col1, col2 = st.columns([3, 1])

    with col1:
        with st.expander("Imagem da Grid", expanded=True):
            st.image(image, caption="Uploaded Grid", width=800)

        st.subheader("Seleção dos Emotes e Badges (〃￣︶￣)人(￣︶￣〃)")

        # Criar tabs apenas para as linhas não vazias
        non_empty_rows_list = sorted(list(st.session_state.non_empty_rows))
        tabs = st.tabs([f"Row {i+1}" for i in non_empty_rows_list])

        for tab_idx, row_idx in enumerate(non_empty_rows_list):
            with tabs[tab_idx]:
                row_buttons = st.columns(4)
                with row_buttons[0]:
                    if st.button(f"Todos Emotes na Row {row_idx+1}", key=f"all_emotes_{row_idx}"):
                        current_cols = 10 if row_idx >= 3 else grid_cols
                        for j in range(current_cols):
                            cell_num = row_idx * 10 + j + 1 if row_idx >= 3 else row_idx * grid_cols + j + 1
                            if cell_num in st.session_state.non_empty_cells:
                                st.session_state[f"status_{cell_num}"] = "Emote"
                                st.session_state.grid_status[cell_num] = "Emote"
                        st.rerun()

                with row_buttons[1]:
                    if st.button(f"Todos Badges na Row {row_idx+1}", key=f"all_badges_{row_idx}"):
                        current_cols = 10 if row_idx >= 3 else grid_cols
                        for j in range(current_cols):
                            cell_num = row_idx * 10 + j + 1 if row_idx >= 3 else row_idx * grid_cols + j + 1
                            if cell_num in st.session_state.non_empty_cells:
                                st.session_state[f"status_{cell_num}"] = "Badge"
                                st.session_state.grid_status[cell_num] = "Badge"
                        st.rerun()

                with row_buttons[2]:
                    if st.button(f"Todos Flairs na Row {row_idx+1}", key=f"all_flairs_{row_idx}"):
                        current_cols = 10 if row_idx >= 3 else grid_cols
                        for j in range(current_cols):
                            cell_num = row_idx * 10 + j + 1 if row_idx >= 3 else row_idx * grid_cols + j + 1
                            if cell_num in st.session_state.non_empty_cells:
                                st.session_state[f"status_{cell_num}"] = "Flair"
                                st.session_state.grid_status[cell_num] = "Flair"
                        st.rerun()

                with row_buttons[3]:
                    if st.button(f"Limpar Row {row_idx+1}", key=f"clear_row_{row_idx}"):
                        current_cols = 10 if row_idx >= 3 else grid_cols
                        for j in range(current_cols):
                            cell_num = row_idx * 10 + j + 1 if row_idx >= 3 else row_idx * grid_cols + j + 1
                            if cell_num in st.session_state.non_empty_cells:
                                st.session_state[f"status_{cell_num}"] = "None"
                                st.session_state.grid_status[cell_num] = "None"
                        st.rerun()

                # Encontrar células não vazias nesta linha
                row_cells = [cell_num for cell_num, (row, _) in st.session_state.non_empty_cells.items() if row == row_idx]

                if row_cells:
                    current_cols = 10 if row_idx >= 3 else grid_cols
                    cols = st.columns(current_cols)
                    for j in range(current_cols):
                        cell_num = row_idx * 10 + j + 1 if row_idx >= 3 else row_idx * grid_cols + j + 1

                        # Mostrar apenas células não vazias
                        if cell_num in st.session_state.non_empty_cells:
                            with cols[j]:
                                row_idx_cell, col_idx_cell = st.session_state.non_empty_cells[cell_num]
                                x, y, cell_size = get_cell_position_and_size(row_idx_cell, col_idx_cell, grid_rows, grid_cols)

                                cell = image.crop((x, y, x + cell_size, y + cell_size))

                                flip_key = f"flip_{cell_num}"
                                if flip_key in st.session_state and st.session_state[flip_key]:
                                    preview_cell = ImageOps.mirror(cell)
                                else:
                                    preview_cell = cell

                                st.image(preview_cell, width=120, caption=f"Cell #{cell_num}")

                                status = st.selectbox(
                                    "Tipo",
                                    ["None", "Emote", "Badge", "Flair"],
                                    key=f"status_{cell_num}"
                                )
                                st.session_state.grid_status[cell_num] = status

                                if status != "None":
                                    name = st.text_input(
                                        "Name",
                                        key=f"name_{cell_num}"
                                    )
                                    st.session_state.grid_names[cell_num] = name

                                    flip = st.checkbox(
                                        "Flip",
                                        key=f"flip_{cell_num}"
                                    )
                                    st.session_state.grid_flip[cell_num] = flip

    with col2:
        st.subheader("Chat Preview q(≧▽≦q)")

        theme_text = "Mudar para Tema Claro" if st.session_state.theme == "dark" else "Mudar para Tema Escuro"
        if st.button(theme_text, on_click=toggle_theme, key="theme_toggle_button"):
            pass

        for idx, status in st.session_state.grid_status.items():
            if status != "None":
                if idx in st.session_state.non_empty_cells:
                    row_idx, col_idx = st.session_state.non_empty_cells[idx]
                    x, y, cell_size = get_cell_position_and_size(row_idx, col_idx, grid_rows, grid_cols)
                else:
                    continue

                name = st.session_state.grid_names.get(idx, str(idx)) or str(idx)

                cell = image.crop((x, y, x + cell_size, y + cell_size))

                if st.session_state.grid_flip.get(idx, False):
                    cell = ImageOps.mirror(cell)

                if status == "Emote":
                    preview_size = (28, 28)
                else:
                    preview_size = (18, 18)

                preview = cell.resize(preview_size)

                buffered = io.BytesIO()
                preview.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()

                if status == "Badge":
                    st.markdown(f'<div class="chat-message"><img src="data:image/png;base64,{img_str}"> <span class="username">Wanzin__</span>: <span style="color:{colors["text_color"]}">Te amo!</span></div>', unsafe_allow_html=True)
                elif status == "Emote":
                    st.markdown(f'<div class="chat-message"><span class="username">Wanzin__</span>: <img src="data:image/png;base64,{img_str}"></div>', unsafe_allow_html=True)

        st.markdown(f'<h4>Todos os Emotes:</h4>', unsafe_allow_html=True)
        emote_html = f'<div class="chat-message"><span class="username">Wanzin__</span>: '
        has_emotes = False

        for idx, status in st.session_state.grid_status.items():
            if status == "Emote":
                has_emotes = True
                if idx in st.session_state.non_empty_cells:
                    row_idx, col_idx = st.session_state.non_empty_cells[idx]
                    x, y, cell_size = get_cell_position_and_size(row_idx, col_idx, grid_rows, grid_cols)
                else:
                    continue

                name = st.session_state.grid_names.get(idx, str(idx)) or str(idx)

                cell = image.crop((x, y, x + cell_size, y + cell_size))

                if st.session_state.grid_flip.get(idx, False):
                    cell = ImageOps.mirror(cell)

                preview = cell.resize((28, 28))

                buffered = io.BytesIO()
                preview.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()

                emote_html += f' <img src="data:image/png;base64,{img_str}">'

        emote_html += '</div>'

        if has_emotes:
            st.markdown(emote_html, unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message"><span style="color:{colors["text_color"]}">Nenhum Emote selecionado.</span></div>', unsafe_allow_html=True)

        st.markdown(f'<h4>Todas as Badges:</h4>', unsafe_allow_html=True)

        badges = []
        flairs = []

        for idx, status in st.session_state.grid_status.items():
            if status == "Badge":
                if idx in st.session_state.non_empty_cells:
                    row_idx, col_idx = st.session_state.non_empty_cells[idx]
                    x, y, cell_size = get_cell_position_and_size(row_idx, col_idx, grid_rows, grid_cols)
                else:
                    continue

                cell = image.crop((x, y, x + cell_size, y + cell_size))

                if st.session_state.grid_flip.get(idx, False):
                    cell = ImageOps.mirror(cell)

                badges.append(cell)

            elif status == "Flair":
                if idx in st.session_state.non_empty_cells:
                    row_idx, col_idx = st.session_state.non_empty_cells[idx]
                    x, y, cell_size = get_cell_position_and_size(row_idx, col_idx, grid_rows, grid_cols)
                else:
                    continue

                cell = image.crop((x, y, x + cell_size, y + cell_size))

                if st.session_state.grid_flip.get(idx, False):
                    cell = ImageOps.mirror(cell)

                flairs.append(cell)

        if badges:
            badge_html = ""

            for badge in badges:
                badge_preview = badge.resize((18, 18))

                badge_buffer = io.BytesIO()
                badge_preview.save(badge_buffer, format="PNG")
                badge_img_str = base64.b64encode(badge_buffer.getvalue()).decode()

                badge_html += f'<img src="data:image/png;base64,{badge_img_str}"> '

            if flairs:
                st.markdown(f'<h4>Badges normais:</h4>', unsafe_allow_html=True)
                st.markdown(f'<div class="chat-message">{badge_html} <span class="username">Wanzin__</span>: <span style="color:{colors["text_color"]}">Badges normais</span></div>', unsafe_allow_html=True)

                st.markdown(f'<h4>Badges com Flairs:</h4>', unsafe_allow_html=True)

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

                    st.markdown(f'<div class="chat-message">{flair_badge_html} <span class="username">Wanzin__</span>: <span style="color:{colors["text_color"]}">Badges com Flair</span></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message">{badge_html} <span class="username">Wanzin__</span>: <span style="color:{colors["text_color"]}">To Chei de Badge</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message"><span style="color:{colors["text_color"]}">Nenhuma Badge selecionada.</span></div>', unsafe_allow_html=True)

        # Fechar o container do chat
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Normal vs Flip (￣_,￣ )")

        flipped_items = []
        for idx in st.session_state.grid_status:
            if (st.session_state.grid_flip.get(idx, False) and
                st.session_state.grid_status[idx] in ["Emote", "Badge", "Flair"]):
                flipped_items.append(idx)

        if flipped_items:
            items_per_row = 5

            for i in range(0, len(flipped_items), items_per_row):
                row_items = flipped_items[i:i+items_per_row]
                cols = st.columns(10)

                for j, idx in enumerate(row_items):
                    status = st.session_state.grid_status[idx]

                    name = st.session_state.grid_names.get(idx, str(idx)) or str(idx)

                    if idx in st.session_state.non_empty_cells:
                        row_idx, col_idx = st.session_state.non_empty_cells[idx]
                        x, y, cell_size = get_cell_position_and_size(row_idx, col_idx, grid_rows, grid_cols)
                    else:
                        continue

                    cell = image.crop((x, y, x + cell_size, y + cell_size))

                    normal = cell
                    flipped = ImageOps.mirror(cell)

                    col_idx = j * 2
                    with cols[col_idx]:
                        st.markdown(f"**Normal**")
                        st.image(normal, width=150)

                    with cols[col_idx + 1]:
                        st.markdown(f"**Flipped**")
                        st.image(flipped, width=150)

            st.markdown("---")
        else:
            st.markdown("Nenhum emote ou badge flipado ainda.")

if __name__ == "__main__":
    main()