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
                    row_buttons = st.columns(3)
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
                                        ["None", "Emote", "Badge"],
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

            chat_container = st.container()

            with chat_container:
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

                        if status == "Badge":
                            st.markdown(f"<img src='data:image/png;base64,{img_str}'> Wanzin__: Te amo!", unsafe_allow_html=True)
                        else:
                            st.markdown(f"Wanzin__: <img src='data:image/png;base64,{img_str}'>", unsafe_allow_html=True)

                st.markdown("**Todos os Emotes:**")
                emote_html = "Wanzin__: "
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

                        emote_html += f" <img src='data:image/png;base64,{img_str}'>"

                if has_emotes:
                    st.markdown(emote_html, unsafe_allow_html=True)
                else:
                    st.markdown("Nenhum Emote selecionado.")

                st.markdown("**Todas as Badges:**")
                badge_html = ""
                has_badges = False

                for idx, status in st.session_state.grid_status.items():
                    if status == "Badge":
                        has_badges = True
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

                        preview = cell.resize((18, 18))

                        buffered = io.BytesIO()
                        preview.save(buffered, format="PNG")
                        img_str = base64.b64encode(buffered.getvalue()).decode()

                        badge_html += f"<img src='data:image/png;base64,{img_str}'> "

                if has_badges:
                    st.markdown(f"{badge_html} Wanzin__: To Chei de Badge", unsafe_allow_html=True)
                else:
                    st.markdown("Nenhuma Badge selecionada.")

        st.markdown("---")
        st.subheader("Normal vs Flip (￣_,￣ )")

        flipped_items = []
        for idx in st.session_state.grid_status:
            if (idx in st.session_state.grid_flip and
                st.session_state.grid_flip[idx] and
                st.session_state.grid_status[idx] in ["Emote", "Badge"]):
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
                        st.markdown(f"**{name}**")
                        st.image(normal, width=150)

                    with cols[col_idx + 1]:
                        st.markdown(f"**Flipped**")
                        st.image(flipped, width=150)

                st.markdown("---")
        else:
            st.markdown("Nenhum emote ou badge flipado ainda.")

if __name__ == "__main__":
    main()