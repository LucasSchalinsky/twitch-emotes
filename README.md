# 🎨 Twitch Emote Manager

A Streamlit web app designed to help Twitch artists and creators quickly process emotes, badges, and flairs from a grid layout.

🌐 Live: https://twitchemotemanager.streamlit.app/

---

## 💜 About the Project
This project was created to help my fiancée, [Oceanekorin](https://x.com/oceanekorin), a digital illustrator who designs emotes for Twitch.

The app streamlines the workflow of extracting, previewing, and exporting emotes and badges from a structured grid, making delivery to clients faster and more organized.

---

## ✨ Technologies
- Python  
- Streamlit  
- Pillow (PIL)  
- NumPy  

---

## 🚀 Features
- Grid Detection — Reads a 5×7 grid and detects non-empty cells automatically  
- Smart Cropping — Extracts 500×500 images with precise spacing and margins  
- Emote & Badge Classification — Mark each item as:
  - Emote  
  - Badge  
  - Badge Bit  
  - Flair  
- Twitch Chat Preview — Realistic chat simulation with:
  - Dark & Light mode  
  - Accurate Twitch colors and sizes  
  - Badge, flair, and emote rendering  
- Flip Support — Mirror images and export both versions  
- Bulk Export — Generates a `.zip` containing:
  - All required Twitch sizes  
  - Correct filenames  
  - Variants (flipped & original)  

---

## 🧩 How It Works
1. Upload a grid image containing emotes.
2. The app detects which cells contain artwork.
3. Assign each item a type (Emote, Badge, Flair, etc.).
4. Optionally name and flip items.
5. Preview everything in a Twitch chat simulation.
6. Export a ready-to-deliver `.zip` package.

---

## 📦 Export Details
The generated `.zip` includes:

- Correct Twitch sizes for each asset  
- Proper naming (e.g., `hug_112x112.png`)  
- Discord-size preview files  
- Flipped variants when enabled  
- Organized folders per asset  

---

## 🚦 Running Locally

```bash
# Clone the repository
git clone https://github.com/LucasSchalinsky/twitch-emotes.git

# Enter the project folder
cd twitch-emotes

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

---

## 🎯 Use Cases

- Twitch emote artists
- Streamers organizing assets
- Designers delivering client packages
- Anyone needing batch emote processing

## ❤️ Credits
Created to support the workflow of
🎨 [Oceanekorin](https://x.com/oceanekorin) — Digital Twitch Emote Artist
