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

def main():
    st.set_page_config(
        page_title="Um fragmento de deus",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.title("Um fragmento de deus")

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

    uploaded_file = st.file_uploader("Imagenzinha da grid mo (❁´◡`❁)", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)

        grid_rows = 5
        grid_cols = 7

        margin = 150
        gap = 150
        square_size = 500

        default_name = uploaded_file.name
        default_name = os.path.splitext(default_name)[0]
        default_name = default_name.replace("Grid", "").strip()

        if 'cells_detected' not in st.session_state or not st.session_state.cells_detected:
            st.session_state.non_empty_cells = {}
            st.session_state.non_empty_rows = set()

            for i in range(grid_rows):
                row_has_content = False
                for j in range(grid_cols):
                    cell_num = i * grid_cols + j + 1

                    x = margin + j * (square_size + gap)
                    y = margin + i * (square_size + gap)

                    cell = image.crop((x, y, x + square_size, y + square_size))

                    if not is_empty_cell(cell):
                        st.session_state.non_empty_cells[cell_num] = (i, j)
                        row_has_content = True

                if row_has_content:
                    st.session_state.non_empty_rows.add(i)

            st.session_state.cells_detected = True

        zip_name = st.text_input("Nome do Zip /ᐠ˵- ⩊ -˵マ", value="")
        f"O nome do Zip vai ser: {default_name if not zip_name else zip_name}.zip（￣︶￣）↗"

        st.subheader("Download")
        col_buttons = st.columns(2)

        with col_buttons[0]:
            if st.button("Processar as Imagenzinhas", type="primary"):
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                    for idx, status in st.session_state.grid_status.items():
                        if status != "None":
                            row_idx, col_idx = divmod(idx-1, grid_cols)
                            x = margin + col_idx * (square_size + gap)
                            y = margin + row_idx * (square_size + gap)

                            if idx in st.session_state.grid_names and st.session_state.grid_names[idx]:
                                name = st.session_state.grid_names[idx]
                            else:
                                name = str(idx)

                            cell = image.crop((x, y, x + square_size, y + square_size))

                            folder = f"{name}/"

                            is_flipped = idx in st.session_state.grid_flip and st.session_state.grid_flip[idx]

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

                            if status == "Emote":
                                sizes = [(128, 128), (112, 112), (56, 56), (28, 28)]
                                for size in sizes:
                                    normal_cell = cell
                                    normal_resized = normal_cell.resize(size)
                                    normal_buffer = io.BytesIO()
                                    normal_resized.save(normal_buffer, format="PNG")
                                    normal_buffer.seek(0)

                                    normal_suffix = "A_" if is_flipped else "_"

                                    if size[0] == 128:
                                        zip_file.writestr(f"{folder}{name}{normal_suffix}DiscordSize.png",
                                                        normal_buffer.getvalue())
                                    else:
                                        zip_file.writestr(f"{folder}{name}{normal_suffix}{size[0]}x{size[1]}.png",
                                                        normal_buffer.getvalue())

                                    if is_flipped:
                                        flipped_cell = ImageOps.mirror(cell)
                                        flipped_resized = flipped_cell.resize(size)
                                        flipped_buffer = io.BytesIO()
                                        flipped_resized.save(flipped_buffer, format="PNG")
                                        flipped_buffer.seek(0)

                                        if size[0] == 128:
                                            zip_file.writestr(f"{folder}{name}B_DiscordSize.png",
                                                            flipped_buffer.getvalue())
                                        else:
                                            zip_file.writestr(f"{folder}{name}B_{size[0]}x{size[1]}.png",
                                                            flipped_buffer.getvalue())
                            else:
                                sizes = [(128, 128), (72, 72), (36, 36), (18, 18)]
                                for size in sizes:
                                    normal_cell = cell
                                    normal_resized = normal_cell.resize(size)
                                    normal_buffer = io.BytesIO()
                                    normal_resized.save(normal_buffer, format="PNG")
                                    normal_buffer.seek(0)

                                    normal_suffix = "A_" if is_flipped else "_"

                                    if size[0] == 128:
                                        zip_file.writestr(f"{folder}{name}{normal_suffix}DiscordSize.png",
                                                        normal_buffer.getvalue())
                                    else:
                                        zip_file.writestr(f"{folder}{name}{normal_suffix}{size[0]}x{size[1]}.png",
                                                        normal_buffer.getvalue())

                                    if is_flipped:
                                        flipped_cell = ImageOps.mirror(cell)
                                        flipped_resized = flipped_cell.resize(size)
                                        flipped_buffer = io.BytesIO()
                                        flipped_resized.save(flipped_buffer, format="PNG")
                                        flipped_buffer.seek(0)

                                        if size[0] == 128:
                                            zip_file.writestr(f"{folder}{name}B_DiscordSize.png",
                                                            flipped_buffer.getvalue())
                                        else:
                                            zip_file.writestr(f"{folder}{name}B_{size[0]}x{size[1]}.png",
                                                            flipped_buffer.getvalue())

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
                    row_buttons = st.columns(5)
                    with row_buttons[0]:
                        if st.button(f"Todos Emotes na Row {row_idx+1}", key=f"all_emotes_{row_idx}"):
                            for j in range(grid_cols):
                                cell_num = row_idx * grid_cols + j + 1
                                if cell_num in st.session_state.non_empty_cells:
                                    st.session_state[f"status_{cell_num}"] = "Emote"
                                    st.session_state.grid_status[cell_num] = "Emote"
                            st.rerun()

                    with row_buttons[1]:
                        if st.button(f"Todos Badges na Row {row_idx+1}", key=f"all_badges_{row_idx}"):
                            for j in range(grid_cols):
                                cell_num = row_idx * grid_cols + j + 1
                                if cell_num in st.session_state.non_empty_cells:
                                    st.session_state[f"status_{cell_num}"] = "Badge"
                                    st.session_state.grid_status[cell_num] = "Badge"
                            st.rerun()

                    with row_buttons[2]:
                        if st.button(f"Todos Badge Bits na Row {row_idx+1}", key=f"all_badge_bits_{row_idx}"):
                            for j in range(grid_cols):
                                cell_num = row_idx * grid_cols + j + 1
                                if cell_num in st.session_state.non_empty_cells:
                                    st.session_state[f"status_{cell_num}"] = "Badge Bit"
                                    st.session_state.grid_status[cell_num] = "Badge Bit"
                            st.rerun()

                    with row_buttons[3]:
                        if st.button(f"Todos Flairs na Row {row_idx+1}", key=f"all_flairs_{row_idx}"):
                            for j in range(grid_cols):
                                cell_num = row_idx * grid_cols + j + 1
                                if cell_num in st.session_state.non_empty_cells:
                                    st.session_state[f"status_{cell_num}"] = "Flair"
                                    st.session_state.grid_status[cell_num] = "Flair"
                            st.rerun()

                    with row_buttons[4]:
                        if st.button(f"Limpar Row {row_idx+1}", key=f"clear_row_{row_idx}"):
                            for j in range(grid_cols):
                                cell_num = row_idx * grid_cols + j + 1
                                if cell_num in st.session_state.non_empty_cells:
                                    st.session_state[f"status_{cell_num}"] = "None"
                                    st.session_state.grid_status[cell_num] = "None"
                            st.rerun()

                    # Encontrar células não vazias nesta linha
                    row_cells = [cell_num for cell_num, (row, _) in st.session_state.non_empty_cells.items() if row == row_idx]

                    if row_cells:
                        cols = st.columns(grid_cols)
                        for j in range(grid_cols):
                            cell_num = row_idx * grid_cols + j + 1

                            # Mostrar apenas células não vazias
                            if cell_num in st.session_state.non_empty_cells:
                                with cols[j]:
                                    x = margin + j * (square_size + gap)
                                    y = margin + row_idx * (square_size + gap)

                                    cell = image.crop((x, y, x + square_size, y + square_size))

                                    flip_key = f"flip_{cell_num}"
                                    if flip_key in st.session_state and st.session_state[flip_key]:
                                        preview_cell = ImageOps.mirror(cell)
                                    else:
                                        preview_cell = cell

                                    st.image(preview_cell, width=120, caption=f"Cell #{cell_num}")

                                    status = st.selectbox(
                                        "Tipo",
                                        ["None", "Emote", "Badge", "Badge Bit", "Flair"],
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

            st.markdown(f"""
            <style>
                /* Mensagens individuais */
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

                /* Garantir que o texto dentro do chat tenha a cor correta */
                .chat-container p, .chat-container div, .chat-container span {{
                    color: {text_color} !important;
                }}

                /* Garantir que os cabeçalhos dentro do chat tenham a cor correta */
                .chat-container h1, .chat-container h2, .chat-container h3,
                .chat-container h4, .chat-container h5, .chat-container h6 {{
                    color: {text_color} !important;
                }}
            </style>
            """, unsafe_allow_html=True)

            for idx, status in st.session_state.grid_status.items():
                if status != "None":
                    row_idx, col_idx = divmod(idx-1, grid_cols)
                    x = margin + col_idx * (square_size + gap)
                    y = margin + row_idx * (square_size + gap)

                    if idx in st.session_state.grid_names and st.session_state.grid_names[idx]:
                        name = st.session_state.grid_names[idx]
                    else:
                        name = str(idx)

                    cell = image.crop((x, y, x + square_size, y + square_size))

                    if idx in st.session_state.grid_flip and st.session_state.grid_flip[idx]:
                        cell = ImageOps.mirror(cell)

                    if status == "Emote":
                        preview_size = (28, 28)
                    else:
                        preview_size = (18, 18)

                    preview = cell.resize(preview_size)

                    buffered = io.BytesIO()
                    preview.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()

                    if status in ["Badge", "Badge Bit"]:
                        st.markdown(f'<div class="chat-message"><img src="data:image/png;base64,{img_str}"> <span class="username">Wanzin__</span>: <span style="color:{text_color}">Te amo!</span></div>', unsafe_allow_html=True)
                    elif status == "Emote":
                        st.markdown(f'<div class="chat-message"><span class="username">Wanzin__</span>: <img src="data:image/png;base64,{img_str}"></div>', unsafe_allow_html=True)

            st.markdown(f'<h4>Todos os Emotes:</h4>', unsafe_allow_html=True)
            emote_html = f'<div class="chat-message"><span class="username">Wanzin__</span>: '
            has_emotes = False

            for idx, status in st.session_state.grid_status.items():
                if status == "Emote":
                    has_emotes = True
                    row_idx, col_idx = divmod(idx-1, grid_cols)
                    x = margin + col_idx * (square_size + gap)
                    y = margin + row_idx * (square_size + gap)

                    if idx in st.session_state.grid_names and st.session_state.grid_names[idx]:
                        name = st.session_state.grid_names[idx]
                    else:
                        name = str(idx)

                    cell = image.crop((x, y, x + square_size, y + square_size))

                    if idx in st.session_state.grid_flip and st.session_state.grid_flip[idx]:
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
                st.markdown(f'<div class="chat-message"><span style="color:{text_color}">Nenhum Emote selecionado.</span></div>', unsafe_allow_html=True)

            st.markdown(f'<h4>Todas as Badges:</h4>', unsafe_allow_html=True)

            badges = []
            badge_bits = []
            flairs = []

            for idx, status in st.session_state.grid_status.items():
                if status == "Badge":
                    row_idx, col_idx = divmod(idx-1, grid_cols)
                    x = margin + col_idx * (square_size + gap)
                    y = margin + row_idx * (square_size + gap)

                    cell = image.crop((x, y, x + square_size, y + square_size))

                    if idx in st.session_state.grid_flip and st.session_state.grid_flip[idx]:
                        cell = ImageOps.mirror(cell)

                    badges.append(cell)

                elif status == "Badge Bit":
                    row_idx, col_idx = divmod(idx-1, grid_cols)
                    x = margin + col_idx * (square_size + gap)
                    y = margin + row_idx * (square_size + gap)

                    cell = image.crop((x, y, x + square_size, y + square_size))

                    if idx in st.session_state.grid_flip and st.session_state.grid_flip[idx]:
                        cell = ImageOps.mirror(cell)

                    badge_bits.append(cell)

                elif status == "Flair":
                    row_idx, col_idx = divmod(idx-1, grid_cols)
                    x = margin + col_idx * (square_size + gap)
                    y = margin + row_idx * (square_size + gap)

                    cell = image.crop((x, y, x + square_size, y + square_size))

                    if idx in st.session_state.grid_flip and st.session_state.grid_flip[idx]:
                        cell = ImageOps.mirror(cell)

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
                        st.markdown(f'<h4>Badges normais:</h4>', unsafe_allow_html=True)
                        st.markdown(f'<div class="chat-message">{badge_html} <span class="username">Wanzin__</span>: <span style="color:{text_color}">Badges normais</span></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="chat-message">{badge_html} <span class="username">Wanzin__</span>: <span style="color:{text_color}">To Chei de Badge</span></div>', unsafe_allow_html=True)

                # Badge Bits (Badge na esquerda + Badge Bit na direita)
                if badge_bits and badges:
                    st.markdown(f'<h4>Badges com Badge Bits:</h4>', unsafe_allow_html=True)
                    
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

                        st.markdown(f'<div class="chat-message">{badge_bit_html} <span class="username">Wanzin__</span>: <span style="color:{text_color}">Badges com Badge Bit</span></div>', unsafe_allow_html=True)

                # Badges com Flairs
                if flairs and badges:
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

                        st.markdown(f'<div class="chat-message">{flair_badge_html} <span class="username">Wanzin__</span>: <span style="color:{text_color}">Badges com Flair</span></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message"><span style="color:{text_color}">Nenhuma Badge selecionada.</span></div>', unsafe_allow_html=True)

            # Fechar o container do chat
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Normal vs Flip (￣_,￣ )")

        flipped_items = []
        for idx in st.session_state.grid_status:
            if (idx in st.session_state.grid_flip and
                st.session_state.grid_flip[idx] and
                st.session_state.grid_status[idx] in ["Emote", "Badge", "Badge Bit", "Flair"]):
                flipped_items.append(idx)

        if flipped_items:
            items_per_row = 5

            for i in range(0, len(flipped_items), items_per_row):
                row_items = flipped_items[i:i+items_per_row]
                cols = st.columns(10)

                for j, idx in enumerate(row_items):
                    status = st.session_state.grid_status[idx]

                    if idx in st.session_state.grid_names and st.session_state.grid_names[idx]:
                        name = st.session_state.grid_names[idx]
                    else:
                        name = str(idx)

                    row_idx, col_idx = divmod(idx-1, grid_cols)
                    x = margin + col_idx * (square_size + gap)
                    y = margin + row_idx * (square_size + gap)

                    cell = image.crop((x, y, x + square_size, y + square_size))

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