import streamlit as st
from PIL import Image, ImageOps
import io
import os
import zipfile
import base64
import numpy as np

def main():
    # Set page config for wider layout
    st.set_page_config(
        page_title="Um fragmento de deus",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.title("Um fragmento de deus")
    
    # Initialize session state for grid data
    if 'grid_status' not in st.session_state:
        st.session_state.grid_status = {}
    if 'grid_names' not in st.session_state:
        st.session_state.grid_names = {}
    if 'grid_flip' not in st.session_state:
        st.session_state.grid_flip = {}
    if 'processed' not in st.session_state:
        st.session_state.processed = False

    uploaded_file = st.file_uploader("Imagenzinha da grid mo (❁´◡`❁)", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)

        grid_rows = 5
        grid_cols = 7

        margin = 150
        gap = 150
        square_size = 500

        st.subheader("Download")
        col_buttons = st.columns(2)

        with col_buttons[0]:
            if st.button("Processar as Imagenzinhas", type="primary"):
                # Create a zip file with all the resized images
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                    for idx, status in st.session_state.grid_status.items():
                        if status != "None":
                            # Calculate cell position
                            row, col = divmod(idx-1, grid_cols)
                            x = margin + col * (square_size + gap)
                            y = margin + row * (square_size + gap)

                            # Generate a placeholder name if none provided
                            if idx in st.session_state.grid_names and st.session_state.grid_names[idx]:
                                name = st.session_state.grid_names[idx]
                            else:
                                # Use the cell number as the name
                                name = str(idx)

                            # Extract the cell
                            cell = image.crop((x, y, x + square_size, y + square_size))

                            # Apply horizontal flip if selected
                            if idx in st.session_state.grid_flip and st.session_state.grid_flip[idx]:
                                cell = ImageOps.mirror(cell)

                            # Create folder structure in zip
                            folder = f"{name}/"

                            # Save original 500x500 image
                            orig_buffer = io.BytesIO()
                            cell.save(orig_buffer, format="PNG")
                            orig_buffer.seek(0)
                            zip_file.writestr(f"{folder}{name}_original.png", orig_buffer.getvalue())

                            # Resize and save based on type
                            if status == "Emote":
                                # Added 128x128 for Discord
                                sizes = [(128, 128), (112, 112), (56, 56), (28, 28)]
                                for size in sizes:
                                    resized = cell.resize(size)
                                    img_buffer = io.BytesIO()
                                    resized.save(img_buffer, format="PNG")
                                    img_buffer.seek(0)
                                    # Label 128x128 as Discord size
                                    if size[0] == 128:
                                        zip_file.writestr(f"{folder}{name}_{size[0]}x{size[1]}_Discord.png",
                                                        img_buffer.getvalue())
                                    else:
                                        zip_file.writestr(f"{folder}{name}_{size[0]}x{size[1]}.png",
                                                        img_buffer.getvalue())
                            else:  # Badge
                                # Added 128x128 for Discord
                                sizes = [(128, 128), (72, 72), (36, 36), (18, 18)]
                                for size in sizes:
                                    resized = cell.resize(size)
                                    img_buffer = io.BytesIO()
                                    resized.save(img_buffer, format="PNG")
                                    img_buffer.seek(0)
                                    # Label 128x128 as Discord size
                                    if size[0] == 128:
                                        zip_file.writestr(f"{folder}{name}_{size[0]}x{size[1]}_Discord.png",
                                                        img_buffer.getvalue())
                                    else:
                                        zip_file.writestr(f"{folder}{name}_{size[0]}x{size[1]}.png",
                                                        img_buffer.getvalue())

                # Store the zip data in session state
                zip_buffer.seek(0)
                st.session_state.zip_data = zip_buffer.getvalue()
                st.session_state.processed = True

        with col_buttons[1]:
            if st.session_state.processed:
                st.download_button(
                    label="Baixar as Imagenzinhas",
                    data=st.session_state.zip_data,
                    file_name="emotes_and_badges.zip",
                    mime="application/zip"
                )

        # Create a grid layout with more space for the grid
        col1, col2 = st.columns([3, 1])

        with col1:
            # Expandable grid image section
            with st.expander("Imagem da Grid", expanded=True):
                st.image(image, caption="Uploaded Grid", width=800)

            st.subheader("Seleção dos Emotes e Badges (〃￣︶￣)人(￣︶￣〃)")

            # Create tabs for each row to save vertical space
            tabs = st.tabs([f"Row {i+1}" for i in range(grid_rows)])

            for i, tab in enumerate(tabs):
                with tab:
                    # Create columns for each cell in the row
                    cols = st.columns(grid_cols)
                    for j in range(grid_cols):
                        # Calculate cell number (1-based)
                        cell_num = i * grid_cols + j + 1

                        with cols[j]:
                            # Calculate cell position
                            x = margin + j * (square_size + gap)
                            y = margin + i * (square_size + gap)

                            # Extract the cell from the grid
                            cell = image.crop((x, y, x + square_size, y + square_size))

                            # Apply horizontal flip for preview if selected
                            flip_key = f"flip_{cell_num}"
                            if flip_key in st.session_state and st.session_state[flip_key]:
                                preview_cell = ImageOps.mirror(cell)
                            else:
                                preview_cell = cell

                            # Display cell with reasonable size and cell number
                            st.image(preview_cell, width=120, caption=f"Cell #{cell_num}")

                            # Status toggle button
                            status = st.selectbox(
                                "Tipo",
                                ["None", "Emote", "Badge"],
                                key=f"status_{cell_num}"
                            )
                            st.session_state.grid_status[cell_num] = status

                            # Name input and flip option
                            if status != "None":
                                name = st.text_input(
                                    "Name",
                                    key=f"name_{cell_num}"
                                )
                                st.session_state.grid_names[cell_num] = name

                                # Add flip horizontally option
                                flip = st.checkbox(
                                    "Flip",
                                    key=f"flip_{cell_num}"
                                )
                                st.session_state.grid_flip[cell_num] = flip

        with col2:
            st.subheader("Chat Preview q(≧▽≦q)")

            # Create a container with fixed height for chat preview
            chat_container = st.container()

            with chat_container:
                # Example chat messages with emotes/badges
                for idx, status in st.session_state.grid_status.items():
                    if status != "None":  # Remove the name check
                        # Calculate cell position
                        row, col = divmod(idx-1, grid_cols)
                        x = margin + col * (square_size + gap)
                        y = margin + row * (square_size + gap)

                        # Generate a placeholder name if none provided
                        if idx in st.session_state.grid_names and st.session_state.grid_names[idx]:
                            name = st.session_state.grid_names[idx]
                        else:
                            # Use the cell number as the name
                            name = str(idx)

                        # Extract the cell
                        cell = image.crop((x, y, x + square_size, y + square_size))

                        # Apply horizontal flip if selected
                        if idx in st.session_state.grid_flip and st.session_state.grid_flip[idx]:
                            cell = ImageOps.mirror(cell)

                        # Resize based on type
                        if status == "Emote":
                            preview_size = (28, 28)  # Small preview
                        else:  # Badge
                            preview_size = (18, 18)  # Small preview

                        preview = cell.resize(preview_size)

                        # Convert to base64 for inline display
                        buffered = io.BytesIO()
                        preview.save(buffered, format="PNG")
                        img_str = base64.b64encode(buffered.getvalue()).decode()

                        # Display in chat-like format with placeholder name
                        if status == "Badge":
                            st.markdown(f"<img src='data:image/png;base64,{img_str}'> Wanzin__: Te amo!", unsafe_allow_html=True)
                        else:
                            st.markdown(f"Wanzin__: <img src='data:image/png;base64,{img_str}'>", unsafe_allow_html=True) 

                # Display a message with ALL emotes
                st.markdown("**Todos os Emotes:**")
                emote_html = "Wanzin__: "
                has_emotes = False

                for idx, status in st.session_state.grid_status.items():
                    if status == "Emote":  # Only emotes
                        has_emotes = True
                        # Calculate cell position
                        row, col = divmod(idx-1, grid_cols)
                        x = margin + col * (square_size + gap)
                        y = margin + row * (square_size + gap)

                        # Generate name
                        if idx in st.session_state.grid_names and st.session_state.grid_names[idx]:
                            name = st.session_state.grid_names[idx]
                        else:
                            name = str(idx)

                        # Extract the cell
                        cell = image.crop((x, y, x + square_size, y + square_size))

                        # Apply horizontal flip if selected
                        if idx in st.session_state.grid_flip and st.session_state.grid_flip[idx]:
                            cell = ImageOps.mirror(cell)

                        # Resize for emote
                        preview = cell.resize((28, 28))

                        # Convert to base64 for inline display
                        buffered = io.BytesIO()
                        preview.save(buffered, format="PNG")
                        img_str = base64.b64encode(buffered.getvalue()).decode()

                        # Add to message
                        emote_html += f" <img src='data:image/png;base64,{img_str}'> ({name})"

                if has_emotes:
                    st.markdown(emote_html, unsafe_allow_html=True)
                else:
                    st.markdown("Nenhum Emote selecionado.")

                # Display a message with ALL badges
                st.markdown("**Todas as Badges:**")
                badge_html = ""
                has_badges = False

                for idx, status in st.session_state.grid_status.items():
                    if status == "Badge":  # Only badges
                        has_badges = True
                        # Calculate cell position
                        row, col = divmod(idx-1, grid_cols)
                        x = margin + col * (square_size + gap)
                        y = margin + row * (square_size + gap)

                        # Generate name
                        if idx in st.session_state.grid_names and st.session_state.grid_names[idx]:
                            name = st.session_state.grid_names[idx]
                        else:
                            name = str(idx)

                        # Extract the cell
                        cell = image.crop((x, y, x + square_size, y + square_size))

                        # Apply horizontal flip if selected
                        if idx in st.session_state.grid_flip and st.session_state.grid_flip[idx]:
                            cell = ImageOps.mirror(cell)

                        # Resize for badge
                        preview = cell.resize((18, 18))

                        # Convert to base64 for inline display
                        buffered = io.BytesIO()
                        preview.save(buffered, format="PNG")
                        img_str = base64.b64encode(buffered.getvalue()).decode()

                        # Add to message
                        badge_html += f"<img src='data:image/png;base64,{img_str}'> "

                if has_badges:
                    st.markdown(f"{badge_html} Wanzin__: To Chei de Badge", unsafe_allow_html=True)
                else:
                    st.markdown("Nenhuma Badge selecionada.")

        # Comparison section for flipped emotes - UPDATED for side-by-side compact layout
        st.markdown("---")
        st.subheader("Normal vs Flip (￣_,￣ )")

        # Check if any emotes are flipped
        flipped_items = []
        for idx in st.session_state.grid_status:
            if (idx in st.session_state.grid_flip and
                st.session_state.grid_flip[idx] and
                st.session_state.grid_status[idx] in ["Emote", "Badge"]):
                flipped_items.append(idx)

        if flipped_items:
            items_per_row = 5
            
            # Group items into rows
            for i in range(0, len(flipped_items), items_per_row):
                row_items = flipped_items[i:i+items_per_row]
                cols = st.columns(10)  # Each item needs 2 columns (normal + flipped)
                
                for j, idx in enumerate(row_items):
                    status = st.session_state.grid_status[idx]
                    
                    # Get name
                    if idx in st.session_state.grid_names and st.session_state.grid_names[idx]:
                        name = st.session_state.grid_names[idx]
                    else:
                        name = str(idx)
                    
                    # Calculate cell position
                    row, col = divmod(idx-1, grid_cols)
                    x = margin + col * (square_size + gap)
                    y = margin + row * (square_size + gap)
                    
                    # Extract the cell
                    cell = image.crop((x, y, x + square_size, y + square_size))
                    
                    # Create normal and flipped versions
                    normal = cell
                    flipped = ImageOps.mirror(cell)
                    
                    # Display side by side in the same row
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