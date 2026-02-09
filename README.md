# 🎬 VEDA — AI Video Generation Engine

<div align="center">

![VEDA](https://img.shields.io/badge/VEDA-AI%20Video%20Engine-6366f1?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiPjxwb2x5Z29uIHBvaW50cz0iNSAzIDIgNiAyIDE4IDUgMjEgMTkgMjEgMjIgMTggMjIgNiAxOSAzIi8+PHBhdGggZD0ibTkgOSA2IDMtNiAzWiIvPjwvc3ZnPgo=)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.1+-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![Gradio](https://img.shields.io/badge/Gradio-UI-F97316?style=for-the-badge&logo=gradio&logoColor=white)

**Transform text & images into stunning AI-generated videos**

[Quick Start](#-quick-start) • [Features](#-features) • [Web UI](#-web-ui) • [Colab](#-google-colab) • [CLI](#-command-line-interface)

</div>

---

## ✨ What is VEDA?

VEDA is a powerful AI video generation engine designed for content creators. Generate professional-quality short videos from text prompts or animate static images — perfect for Instagram Reels, TikTok, and social media content.

### Key Highlights

- 🎨 **Text-to-Video** — Describe what you want, get a video
- 🖼️ **Image-to-Video** — Bring static photos to life
- 🧠 **Smart Prompt Brain** — AI-enhanced prompts for better results
- ⚡ **GPU Optimized** — Works on GTX 1650 (4GB VRAM) and up
- ☁️ **Colab Integration** — Use free cloud GPU for generation
- 🎯 **Creator-Focused** — 9:16 portrait format, Instagram-ready

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/VEDA.git
cd VEDA

# Install dependencies
pip install -r requirements.txt
```

### Launch Web UI

```bash
python -m veda_app.app
```

Open **http://localhost:7860** in your browser.

---

## 🖥️ Web UI

VEDA includes a beautiful, minimalist web interface built with Gradio:

- **Prompt Input** — Describe your video idea
- **Style Presets** — Cinematic, Portrait, Product, Nature, Aesthetic, Reels
- **Smart Enhancement** — AI automatically improves your prompts
- **Colab Connection** — Connect to Google Colab for free GPU access

### Using the Web UI

1. Start the app: `python -m veda_app.app`
2. Open http://localhost:7860
3. Enter a prompt (e.g., "woman smiling at sunset beach")
4. Select a style
5. Click **✨ Generate Video**

---

## ☁️ Google Colab Integration

No local GPU? No problem! VEDA can connect to Google Colab's free T4 GPU.

### Setup

1. **Open Colab Notebook**
   - Upload `VEDA_Colab_HD_Video.ipynb` to Google Colab
   - Set runtime to **GPU (T4)**

2. **Run the Notebook**
   - Execute Cell 1 (Setup) — ~5 min
   - Execute Cell 3 (Launch Web UI)
   - Copy the `gradio.live` URL

3. **Connect Local App**
   - Paste the URL in the "Connect to Colab GPU" section
   - Click **🔌 Connect**
   - Generate videos using Colab's GPU!

---

## 💻 Command Line Interface

### Text-to-Video

```bash
python -m veda_engine.cli text2video \
  --prompt "A flower blooming in sunlight" \
  --style cinematic \
  --output outputs/flower.mp4
```

### Image-to-Video

```bash
python -m veda_engine.cli img2video \
  --image inputs/landscape.jpg \
  --motion "clouds moving slowly" \
  --strength medium
```

### Portrait Animation

```bash
python -m veda_engine.cli portrait \
  --image inputs/headshot.jpg \
  --expression smile
```

### System Info

```bash
python -m veda_engine.cli info
```

---

## 🎨 Style Presets

| Style | Best For | Settings |
|-------|----------|----------|
| **Cinematic** | Dramatic scenes, landscapes | High guidance, 8K quality |
| **Portrait** | People, faces, headshots | Soft lighting, bokeh |
| **Product** | E-commerce, item showcases | Studio lighting, clean |
| **Nature** | Outdoor scenes, wildlife | Vivid colors, documentary |
| **Aesthetic** | Dreamy, artistic content | Soft, ethereal look |
| **Reels** | Social media, viral content | Engaging, trending style |

---

## 📦 Features

| Feature | Status | Description |
|---------|--------|-------------|
| Text-to-Video | ✅ | Generate video from text prompts |
| Image-to-Video | ✅ | Animate static images |
| Portrait Animation | ✅ | Animate faces with expressions |
| Web UI | ✅ | Beautiful Gradio interface |
| Colab Integration | ✅ | Connect to free cloud GPU |
| Prompt Brain | ✅ | AI-enhanced prompt engineering |
| GTX 1650 Optimized | ✅ | CPU offload, attention slicing |
| Instagram Format | ✅ | 9:16 aspect ratio, H.264 |

---

## 🖥️ Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU | GTX 1650 (4GB) | RTX 3060 (12GB) |
| RAM | 8GB | 16GB |
| Storage | 20GB | 50GB |
| OS | Windows 10/11, Linux | - |

> 💡 **Tip**: Use Google Colab for free GPU access if you have limited hardware!

---

## 📁 Project Structure

```
VEDA/
├── veda_app/
│   ├── app.py              # Gradio Web UI
│   └── colab_client.py     # Colab API integration
├── veda_engine/
│   ├── config.py           # Hardware-aware settings
│   ├── cli.py              # Command-line interface
│   ├── core/
│   │   ├── pipeline.py     # LTX-Video wrapper
│   │   ├── prompt_brain.py # AI prompt enhancement
│   │   └── memory.py       # VRAM management
│   ├── generators/
│   │   ├── text_to_video.py
│   │   └── image_to_video.py
│   └── utils/
├── inputs/                  # Source images
├── outputs/                 # Generated videos
├── VEDA_Colab_HD_Video.ipynb    # Colab notebook (HD)
├── VEDA_Colab_Video_Generator.ipynb  # Colab notebook (Lightweight)
└── requirements.txt
```

---

## ⚙️ Configuration

Default settings optimized for GTX 1650 (4GB VRAM):

| Parameter | Value | Notes |
|-----------|-------|-------|
| Resolution | 512×768 | Safe for 4GB VRAM |
| Frames | 49 | ~2 sec @ 24fps |
| Inference Steps | 25 | Quality/speed balance |
| CPU Offload | Enabled | Saves ~1.5GB VRAM |
| VAE Slicing | Enabled | Memory efficient |

---

## 🔧 Troubleshooting

### Out of Memory (OOM)
- Use `--fast` flag for preview mode
- Close other GPU applications
- Try Google Colab instead

### Slow Generation
- First run downloads ~10GB model
- Subsequent runs use cached model
- Expected: 3-5 min per 2-sec clip locally

### Colab Connection Failed
- Ensure the Colab notebook is still running
- Check if the `gradio.live` URL hasn't expired (valid for ~72 hours)
- Refresh the Colab cell if needed

---

## �️ Roadmap

- [ ] Real-ESRGAN 4x upscaling
- [ ] Batch video generation
- [ ] Custom model fine-tuning
- [ ] Audio/music synchronization
- [ ] Direct social media upload

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

MIT License © 2025 Aman Singh

---

<div align="center">

**Built with ❤️ for creators**

[⭐ Star this repo](https://github.com/yourusername/VEDA) • [🐛 Report Bug](https://github.com/yourusername/VEDA/issues) • [💡 Request Feature](https://github.com/yourusername/VEDA/issues)

</div>
