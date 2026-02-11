"""
VEDA Web UI - Seedance 2.0 Inspired Interface
Black & white theme, split-panel layout.
Supports local preview, Colab GPU generation, batch processing.
"""

import gradio as gr
from typing import Optional
import os
import json
import tempfile
from pathlib import Path

# Import Prompt Brain and Colab Client
from veda_engine.core.prompt_brain import PromptBrain, STYLES
from veda_app.colab_client import get_colab_client

brain = PromptBrain()
colab = get_colab_client()

# ─── Seedance 2.0 Inspired CSS — Black & White ──────────────────────────────
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Reset & Globals ── */
:root {
    --bg-primary: #000000;
    --bg-secondary: #0a0a0a;
    --bg-surface: #111111;
    --bg-elevated: #1a1a1a;
    --border-primary: #222222;
    --border-secondary: #333333;
    --text-primary: #ffffff;
    --text-secondary: #aaaaaa;
    --text-muted: #666666;
    --accent: #ffffff;
    --radius: 12px;
    --radius-sm: 8px;
    --radius-lg: 16px;
}

* { box-sizing: border-box; }

body, .gradio-container {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.gradio-container {
    max-width: 1400px !important;
    margin: 0 auto !important;
    padding: 0 !important;
}

/* ── Dark mode overrides ── */
.dark, .dark .gradio-container {
    background: var(--bg-primary) !important;
}

/* ── Top Navigation Bar ── */
.top-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 32px;
    border-bottom: 1px solid var(--border-primary);
    background: var(--bg-primary);
}

.top-nav .brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.1rem;
    font-weight: 600;
    letter-spacing: 1px;
    color: var(--text-primary);
}

.top-nav .brand .dot {
    width: 10px;
    height: 10px;
    background: #ffffff;
    border-radius: 50%;
    display: inline-block;
}

.top-nav .nav-links {
    display: flex;
    align-items: center;
    gap: 24px;
    font-size: 0.9rem;
    color: var(--text-secondary);
}

.top-nav .nav-links a {
    color: var(--text-secondary);
    text-decoration: none;
    transition: color 0.2s;
}

.top-nav .nav-links a:hover {
    color: var(--text-primary);
}

/* ── Hero Section ── */
.hero-section {
    text-align: center;
    padding: 48px 24px 32px;
}

.hero-section h1 {
    font-size: 2.8rem;
    font-weight: 800;
    color: var(--text-primary);
    margin: 0 0 12px;
    letter-spacing: -1px;
}

.hero-section p {
    color: var(--text-secondary);
    font-size: 0.95rem;
    max-width: 700px;
    margin: 0 auto;
    line-height: 1.6;
}

.hero-section p em {
    color: var(--text-muted);
    font-style: normal;
    text-decoration: underline;
    text-underline-offset: 3px;
    text-decoration-color: var(--border-secondary);
}

/* ── Main Content Panel ── */
.main-panel {
    display: flex;
    gap: 0;
    margin: 0 24px 24px;
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-lg);
    overflow: hidden;
    background: var(--bg-secondary);
    min-height: 600px;
}

/* ── Left Panel (Controls) ── */
.controls-panel {
    width: 420px;
    min-width: 420px;
    padding: 24px;
    overflow-y: auto;
    border-right: 1px solid var(--border-primary);
    background: var(--bg-surface);
}

/* ── Right Panel (Preview) ── */
.preview-panel {
    flex: 1;
    padding: 24px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: var(--bg-secondary);
}

/* ── Tab Switcher ── */
.tab-switcher {
    display: flex;
    background: var(--bg-elevated);
    border-radius: var(--radius);
    padding: 4px;
    margin-bottom: 20px;
    border: 1px solid var(--border-primary);
}

.tab-switcher button {
    flex: 1;
    padding: 10px 16px;
    border: none;
    border-radius: var(--radius-sm);
    background: transparent;
    color: var(--text-muted);
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    font-family: 'Inter', sans-serif;
}

.tab-switcher button.active,
.tab-switcher button:hover {
    background: var(--bg-surface);
    color: var(--text-primary);
}

/* ── Section Labels ── */
.section-label {
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--text-secondary);
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.section-label .icon {
    font-size: 0.85rem;
}

/* ── Upload Area ── */
.upload-area {
    border: 2px dashed var(--border-secondary);
    border-radius: var(--radius);
    padding: 32px 20px;
    text-align: center;
    cursor: pointer;
    transition: border-color 0.2s, background 0.2s;
    background: var(--bg-elevated);
    margin-bottom: 16px;
}

.upload-area:hover {
    border-color: var(--text-muted);
    background: rgba(255,255,255,0.03);
}

.upload-area .upload-icon {
    font-size: 1.8rem;
    color: var(--text-muted);
    margin-bottom: 8px;
}

.upload-area p {
    color: var(--text-secondary);
    font-size: 0.85rem;
    margin: 4px 0 0;
}

.upload-area .formats {
    color: var(--text-muted);
    font-size: 0.75rem;
    margin-top: 4px;
}

/* ── Resolution Pills ── */
.resolution-pills {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
}

.resolution-pill {
    padding: 8px 18px;
    border-radius: 999px;
    border: 1px solid var(--border-secondary);
    background: transparent;
    color: var(--text-secondary);
    font-size: 0.82rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    font-family: 'Inter', sans-serif;
}

.resolution-pill.active,
.resolution-pill:hover {
    background: var(--text-primary);
    color: var(--bg-primary);
    border-color: var(--text-primary);
}

/* ── Aspect Ratio Grid ── */
.aspect-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    margin-bottom: 16px;
}

.aspect-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 12px 6px;
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-sm);
    background: var(--bg-elevated);
    cursor: pointer;
    transition: all 0.2s;
    gap: 4px;
}

.aspect-card:hover,
.aspect-card.active {
    border-color: var(--text-primary);
    background: rgba(255,255,255,0.06);
}

.aspect-card .ratio-icon {
    width: 28px;
    height: 28px;
    border: 1.5px solid var(--text-muted);
    border-radius: 3px;
}

.aspect-card .ratio-label {
    font-size: 0.7rem;
    color: var(--text-muted);
}

/* ── Generate Button ── */
.generate-btn {
    width: 100%;
    padding: 14px 24px !important;
    background: var(--text-primary) !important;
    color: var(--bg-primary) !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    cursor: pointer;
    transition: all 0.2s !important;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: 0.3px;
}

.generate-btn:hover {
    background: #e0e0e0 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(255,255,255,0.15) !important;
}

/* ── Footer ── */
.veda-footer {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr;
    gap: 40px;
    padding: 48px 32px;
    border-top: 1px solid var(--border-primary);
    margin-top: 24px;
}

.veda-footer .footer-brand h3 {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 12px;
    color: var(--text-primary);
}

.veda-footer .footer-brand h3 .dot {
    width: 8px;
    height: 8px;
    background: white;
    border-radius: 50%;
    display: inline-block;
}

.veda-footer .footer-brand p {
    color: var(--text-muted);
    font-size: 0.82rem;
    line-height: 1.6;
}

.veda-footer .footer-col h4 {
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 12px;
    color: var(--text-primary);
}

.veda-footer .footer-col a {
    display: block;
    color: var(--text-muted);
    text-decoration: none;
    font-size: 0.82rem;
    padding: 4px 0;
    transition: color 0.2s;
}

.veda-footer .footer-col a:hover {
    color: var(--text-primary);
}

.footer-copy {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.75rem;
    padding: 16px 32px 32px;
    border-top: 1px solid var(--border-primary);
}

/* ── Gradio Component Overrides ── */
.gradio-container .gr-box,
.gradio-container .gr-panel,
.gradio-container .gr-form {
    background: var(--bg-surface) !important;
    border-color: var(--border-primary) !important;
}

.gradio-container input,
.gradio-container textarea,
.gradio-container select {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-primary) !important;
    color: var(--text-primary) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Inter', sans-serif !important;
}

.gradio-container input:focus,
.gradio-container textarea:focus {
    border-color: var(--text-muted) !important;
    box-shadow: 0 0 0 2px rgba(255,255,255,0.05) !important;
}

.gradio-container label {
    color: var(--text-secondary) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}

.gradio-container .tabs {
    background: transparent !important;
    border: none !important;
}

.gradio-container .tab-nav {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-primary) !important;
    border-radius: var(--radius) !important;
    padding: 4px !important;
    gap: 0 !important;
}

.gradio-container .tab-nav button {
    background: transparent !important;
    color: var(--text-muted) !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    padding: 10px 20px !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.2s !important;
}

.gradio-container .tab-nav button.selected {
    background: var(--bg-surface) !important;
    color: var(--text-primary) !important;
}

.gradio-container .tabitem {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

/* Slider styling */
.gradio-container input[type="range"] {
    accent-color: white !important;
}

.gradio-container .gr-slider {
    --slider-color: white !important;
}

/* Checkbox styling */
.gradio-container input[type="checkbox"]:checked {
    accent-color: white !important;
}

/* Accordion */
.gradio-container .accordion {
    border: 1px solid var(--border-primary) !important;
    border-radius: var(--radius) !important;
    background: var(--bg-elevated) !important;
}

.gradio-container .accordion > .label-wrap {
    background: var(--bg-elevated) !important;
    color: var(--text-secondary) !important;
}

/* Video component */
.gradio-container .gr-video {
    border-radius: var(--radius-lg) !important;
    overflow: hidden;
    border: 1px solid var(--border-primary) !important;
}

/* Dropdown */
.gradio-container .gr-dropdown {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-primary) !important;
    border-radius: var(--radius-sm) !important;
}

/* Button variants */
.gradio-container button.secondary {
    background: var(--bg-elevated) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-secondary) !important;
    border-radius: var(--radius-sm) !important;
}

.gradio-container button.secondary:hover {
    background: rgba(255,255,255,0.08) !important;
    color: var(--text-primary) !important;
}

/* Radio buttons as pills */
.gradio-container .gr-radio {
    gap: 8px !important;
}

.gradio-container .gr-radio label {
    padding: 8px 18px !important;
    border-radius: 999px !important;
    border: 1px solid var(--border-secondary) !important;
    background: transparent !important;
    transition: all 0.2s !important;
    cursor: pointer !important;
}

.gradio-container .gr-radio label.selected,
.gradio-container .gr-radio input:checked + label {
    background: var(--text-primary) !important;
    color: var(--bg-primary) !important;
    border-color: var(--text-primary) !important;
}

/* Status bar */
.status-bar {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    padding: 12px 0;
    font-size: 0.8rem;
    color: var(--text-muted);
}

.status-bar .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #4ade80;
    display: inline-block;
}

/* Hide default gradio footers */
footer { display: none !important; }
.gradio-container > .wrap { border: none !important; }
"""


def enhance_and_show(prompt: str, style: str) -> str:
    """Enhance prompt and show preview."""
    if not prompt.strip():
        return ""
    result = brain.enhance(prompt, style.lower())
    return f"✨ {result['prompt']}"


def get_random_idea() -> str:
    """Get a random content idea."""
    import random
    ideas = brain.suggest_ideas("trending")
    return random.choice(ideas)


def create_demo_interface():
    """Create the main Gradio interface — Seedance 2.0 inspired."""
    
    # Connection handler
    def connect_to_colab(url):
        success, message = colab.connect(url)
        return message
    
    # Generate using Colab
    def generate_video(prompt, style, resolution, frames, aspect, seed, upscale, image=None):
        if not prompt.strip():
            return "❌ Please enter a prompt", None
        
        if not colab.is_connected:
            return "⚠️ Connect to Colab first! Open Advanced → paste your Colab URL.", None
        
        # Generate via Colab
        status, video_path = colab.generate(
            prompt=prompt,
            style=style.lower(),
            frames=int(frames),
            seed=int(seed),
            upscale=upscale
        )
        
        return status, video_path
    
    # Batch handler
    def run_batch(batch_json, upscale):
        """Run batch generation from JSON text."""
        if not batch_json.strip():
            return "❌ Please enter batch JSON"
        
        if not colab.is_connected:
            return "⚠️ Connect to Colab first!"
        
        try:
            data = json.loads(batch_json)
            jobs = data.get("jobs", data if isinstance(data, list) else [])
        except json.JSONDecodeError as e:
            return f"❌ Invalid JSON: {e}"
        
        results = []
        for i, job in enumerate(jobs):
            prompt = job.get("prompt", "")
            style = job.get("style", "cinematic")
            seed = job.get("seed", 42)
            
            results.append(f"[{i+1}/{len(jobs)}] Generating: {prompt[:50]}...")
            
            status, video_path = colab.generate(
                prompt=prompt,
                style=style,
                seed=seed,
                upscale=upscale
            )
            
            if video_path:
                results.append(f"  ✅ Done → {video_path}")
            else:
                results.append(f"  ❌ Failed: {status}")
        
        results.append(f"\n🏁 Batch complete: {len(jobs)} jobs processed")
        return "\n".join(results)
    
    # ─── BUILD UI ────────────────────────────────────────────────────────
    with gr.Blocks(
        css=CUSTOM_CSS,
        theme=gr.themes.Base(
            primary_hue=gr.themes.colors.neutral,
            secondary_hue=gr.themes.colors.neutral,
            neutral_hue=gr.themes.colors.neutral,
        ),
        title="VEDA – AI Video Generator"
    ) as demo:
        
        # ── Top Navigation ──
        gr.HTML("""
            <div class="top-nav">
                <div class="brand">
                    <span class="dot"></span>
                    VEDA
                </div>
                <div class="nav-links">
                    <a href="#">Generate</a>
                    <a href="#">Pricing</a>
                </div>
            </div>
        """)
        
        # ── Hero Section ──
        gr.HTML("""
            <div class="hero-section">
                <h1>VEDA 2.0</h1>
                <p>
                    Experience <em>AI-powered video creation</em>. 
                    Combine images, text, and style presets to generate cinematic content 
                    with <em>intelligent prompt enhancement</em>, seamless Colab GPU rendering, 
                    and <em>professional quality output</em>.
                </p>
            </div>
        """)
        
        # ── Main Two-Panel Layout ──
        with gr.Row(elem_classes=["main-panel"]):
            
            # ════ LEFT PANEL — Controls ════
            with gr.Column(scale=4, elem_classes=["controls-panel"]):
                
                # ── Mode Tabs: Image to Video / Text to Video ──
                with gr.Tabs():
                    
                    # ─── IMAGE TO VIDEO ───
                    with gr.TabItem("🖼 Image to Video"):
                        
                        # AI Model Selector
                        gr.HTML('<div class="section-label"><span class="icon">🤖</span> AI Model</div>')
                        model_dropdown_i2v = gr.Dropdown(
                            choices=["VEDA Pro • HD Quality", "VEDA Standard • Fast", "VEDA Lite • Preview"],
                            value="VEDA Pro • HD Quality",
                            label="",
                            show_label=False,
                            container=False,
                        )
                        
                        gr.HTML('<br>')
                        
                        # Image Upload
                        gr.HTML('<div class="section-label"><span class="icon">🖼</span> Images</div>')
                        image_upload = gr.Image(
                            label="",
                            show_label=False,
                            type="filepath",
                            height=140,
                            sources=["upload", "clipboard"],
                        )
                        gr.HTML('<p style="color: #666; font-size: 0.75rem; text-align: center; margin-top: 4px;">PNG, JPG, JPEG, WEBP</p>')
                        
                        # Prompt
                        gr.HTML('<div class="section-label"><span class="icon">✏️</span> Prompt</div>')
                        prompt_i2v = gr.Textbox(
                            label="",
                            show_label=False,
                            placeholder="Describe how you want your image to animate...",
                            lines=3,
                            max_lines=5,
                        )
                        
                        # Style
                        style_i2v = gr.Dropdown(
                            choices=["Cinematic", "Portrait", "Product", "Nature", "Aesthetic", "Reels"],
                            value="Cinematic",
                            label="Style",
                        )

                    # ─── TEXT TO VIDEO ───
                    with gr.TabItem("📝 Text to Video"):
                        
                        # AI Model Selector
                        gr.HTML('<div class="section-label"><span class="icon">🤖</span> AI Model</div>')
                        model_dropdown_t2v = gr.Dropdown(
                            choices=["VEDA Pro • HD Quality", "VEDA Standard • Fast", "VEDA Lite • Preview"],
                            value="VEDA Pro • HD Quality",
                            label="",
                            show_label=False,
                            container=False,
                        )
                        
                        gr.HTML('<br>')
                        
                        # Prompt
                        gr.HTML('<div class="section-label"><span class="icon">✏️</span> Prompt</div>')
                        prompt_t2v = gr.Textbox(
                            label="",
                            show_label=False,
                            placeholder="Describe the video you want to create...",
                            lines=4,
                            max_lines=6,
                        )
                        
                        # Enhanced Preview
                        enhanced_preview = gr.Textbox(
                            label="Enhanced Prompt",
                            interactive=False,
                            lines=2,
                            visible=True,
                        )
                        
                        # Style
                        style_t2v = gr.Dropdown(
                            choices=["Cinematic", "Portrait", "Product", "Nature", "Aesthetic", "Reels"],
                            value="Cinematic",
                            label="Style",
                        )
                
                gr.HTML('<hr style="border-color: #222; margin: 16px 0;">')
                
                # ── Resolution ──
                gr.HTML('<div class="section-label"><span class="icon">📐</span> Resolution</div>')
                resolution = gr.Radio(
                    choices=["480p", "720p"],
                    value="480p",
                    label="",
                    show_label=False,
                )
                
                # ── Duration ──
                gr.HTML('<div class="section-label"><span class="icon">⏱</span> Duration</div>')
                duration_slider = gr.Slider(
                    minimum=8,
                    maximum=24,
                    value=16,
                    step=4,
                    label="Frames",
                    info="",
                )
                
                # ── Aspect Ratio ──
                gr.HTML('<div class="section-label"><span class="icon">📐</span> Aspect Ratio</div>')
                aspect_ratio = gr.Radio(
                    choices=["Auto", "1:1", "4:5", "16:9", "9:16", "3:4"],
                    value="Auto",
                    label="",
                    show_label=False,
                )
                
                # ── Advanced Settings ──
                with gr.Accordion("⚙️ Advanced", open=False):
                    seed_input = gr.Number(value=42, label="Seed")
                    upscale_toggle = gr.Checkbox(
                        value=True,
                        label="🔬 Upscale to 1024px (Real-ESRGAN 4x)"
                    )
                    
                    gr.HTML('<hr style="border-color: #222; margin: 12px 0;">')
                    
                    # Colab Connection
                    gr.HTML("""
                        <div class="section-label"><span class="icon">🔗</span> Colab GPU Connection</div>
                        <p style="color: #666; font-size: 0.78rem; margin-bottom: 8px;">
                            Run VEDA Colab notebook → copy the gradio.live URL → paste below.
                        </p>
                    """)
                    colab_url = gr.Textbox(
                        label="Colab URL",
                        placeholder="https://xxxxx.gradio.live",
                    )
                    connect_btn = gr.Button("🔌 Connect", size="sm")
                    connection_status = gr.Textbox(
                        label="Status",
                        value="⚪ Not connected",
                        interactive=False,
                    )
                    
                    connect_btn.click(
                        fn=connect_to_colab,
                        inputs=[colab_url],
                        outputs=[connection_status]
                    )
                
                # ── Generate Button ──
                generate_btn = gr.Button(
                    "✨ Generate",
                    variant="primary",
                    elem_classes=["generate-btn"],
                )
                
                # Status bar
                gr.HTML("""
                    <div class="status-bar">
                        <span><span class="status-dot"></span> Available</span>
                    </div>
                """)
            
            # ════ RIGHT PANEL — Preview ════
            with gr.Column(scale=6, elem_classes=["preview-panel"]):
                status_text = gr.Textbox(
                    label="Status",
                    value="Ready — Connect to Colab to start generating",
                    interactive=False,
                )
                output_video = gr.Video(
                    label="Generated Video",
                    height=420,
                )
                
                # Quick Ideas
                gr.HTML('<hr style="border-color: #222; margin: 16px 0;">')
                gr.HTML('<div class="section-label" style="justify-content: center;">💡 Quick Ideas</div>')
                with gr.Row():
                    idea_btn = gr.Button("🎲 Random Idea", size="sm", variant="secondary")
                ideas_display = gr.Textbox(
                    label="Try this prompt",
                    value="beautiful sunset over ocean, golden light, waves, cinematic",
                    interactive=True,
                )
        
        # ── ADDITIONAL TABS — Batch & API ──
        gr.HTML('<div style="margin: 0 24px;">')
        with gr.Tabs():
            
            # ─── Batch Generation ───
            with gr.TabItem("📦 Batch Generation"):
                gr.HTML("""
                    <p style="color: #888; font-size: 0.85rem; margin-bottom: 12px;">
                        Paste a JSON array of prompts to generate multiple videos in sequence.
                    </p>
                """)
                
                batch_input = gr.Textbox(
                    label="Batch JSON",
                    placeholder='{"jobs": [{"prompt": "sunset", "style": "cinematic"}, ...]}',
                    lines=8,
                    value=json.dumps({
                        "jobs": [
                            {"prompt": "sunset over ocean, golden hour", "style": "cinematic", "seed": 42},
                            {"prompt": "coffee steam rising, cozy morning", "style": "product"},
                            {"prompt": "woman walking in autumn forest", "style": "portrait"}
                        ]
                    }, indent=2)
                )
                
                batch_upscale = gr.Checkbox(value=False, label="🔬 Upscale all outputs")
                batch_btn = gr.Button("🚀 Run Batch", variant="primary")
                
                batch_output = gr.Textbox(
                    label="Batch Progress",
                    interactive=False,
                    lines=10,
                )
                
                batch_btn.click(
                    fn=run_batch,
                    inputs=[batch_input, batch_upscale],
                    outputs=[batch_output]
                )
            
            # ─── API Reference ───
            with gr.TabItem("🌐 API"):
                gr.HTML("""
                    <p style="color: #888; font-size: 0.85rem; margin-bottom: 8px;">
                        VEDA includes a REST API for programmatic access. Start the API server:
                    </p>
                    <div style="background: #111; border: 1px solid #222; border-radius: 8px; padding: 14px; font-family: monospace; font-size: 0.82rem; color: #ccc; margin-bottom: 16px;">
                        <code>python -m veda_app.api</code><br>
                        Swagger docs: <code>http://localhost:8000/docs</code>
                    </div>
                    <p style="color: #888; font-size: 0.85rem; margin-bottom: 8px;"><strong>Endpoints:</strong></p>
                """)
                
                gr.Dataframe(
                    headers=["Method", "Endpoint", "Description"],
                    value=[
                        ["POST", "/api/generate", "Submit a generation job"],
                        ["GET", "/api/status/{job_id}", "Poll job status"],
                        ["GET", "/api/download/{job_id}", "Download completed video"],
                        ["GET", "/api/styles", "List available style presets"],
                    ],
                    interactive=False,
                )
                
                gr.HTML("""
                    <br>
                    <p style="color: #888; font-size: 0.85rem;"><strong>Example:</strong></p>
                    <div style="background: #111; border: 1px solid #222; border-radius: 8px; padding: 14px; font-family: monospace; font-size: 0.82rem; color: #ccc;">
curl -X POST http://localhost:8000/api/generate \\<br>
&nbsp;&nbsp;-H "Content-Type: application/json" \\<br>
&nbsp;&nbsp;-d '{"prompt": "sunset over ocean", "style": "cinematic"}'
                    </div>
                """)
        
        gr.HTML('</div>')
        
        # ── Footer ──
        gr.HTML("""
            <div class="veda-footer">
                <div class="footer-brand">
                    <h3><span class="dot"></span> VEDA</h3>
                    <p>
                        Create stunning AI videos with VEDA 2.0. Transform images 
                        and text into cinematic videos with advanced motion synthesis 
                        and professional quality.
                    </p>
                </div>
                <div class="footer-col">
                    <h4>Product</h4>
                    <a href="#">Generate</a>
                    <a href="#">Text to Video</a>
                    <a href="#">Image to Video</a>
                </div>
                <div class="footer-col">
                    <h4>Legal</h4>
                    <a href="#">Terms of Service</a>
                    <a href="#">Privacy Policy</a>
                    <a href="#">Contact Us</a>
                </div>
            </div>
            <div class="footer-copy">
                Copyright © 2026 VEDA. All rights reserved.
            </div>
        """)
        
        # ── Event Handlers ──
        prompt_t2v.change(
            fn=enhance_and_show,
            inputs=[prompt_t2v, style_t2v],
            outputs=[enhanced_preview]
        )
        style_t2v.change(
            fn=enhance_and_show,
            inputs=[prompt_t2v, style_t2v],
            outputs=[enhanced_preview]
        )
        
        idea_btn.click(fn=get_random_idea, outputs=[ideas_display])
        
        # Generate from Text to Video tab
        generate_btn.click(
            fn=generate_video,
            inputs=[prompt_t2v, style_t2v, resolution, duration_slider, aspect_ratio, seed_input, upscale_toggle],
            outputs=[status_text, output_video]
        )
    
    return demo


# Colab-compatible version with actual generation
def create_colab_interface(pipe, enhance_prompt):
    """Create interface for Colab with actual generation."""
    import torch
    import gc
    from PIL import ImageEnhance, Image
    import numpy as np
    import imageio
    import tempfile
    
    def generate_video(prompt, style, frames, seed, upscale):
        try:
            # Enhance prompt
            e = enhance_prompt(prompt, style.lower())
            
            gc.collect()
            torch.cuda.empty_cache()
            
            output = pipe(
                prompt=e["prompt"],
                negative_prompt=e["negative_prompt"],
                num_frames=int(frames),
                num_inference_steps=e["num_inference_steps"],
                guidance_scale=e["guidance_scale"],
                generator=torch.Generator("cpu").manual_seed(int(seed)),
            )
            
            video_frames = output.frames[0]
            
            if upscale:
                # Try Real-ESRGAN first, fall back to PIL
                try:
                    from veda_engine.core.upscaler import get_upscaler
                    upscaler = get_upscaler(scale=4)
                    video_frames = upscaler.upscale_frames(video_frames)
                except Exception:
                    video_frames = [
                        ImageEnhance.Sharpness(f.resize((1024, 1024), Image.LANCZOS)).enhance(1.3) 
                        for f in video_frames
                    ]
            
            # Save to temp file
            temp_path = tempfile.mktemp(suffix=".mp4")
            frames_np = [np.array(f) for f in video_frames]
            imageio.mimsave(temp_path, frames_np, fps=12, quality=9)
            
            return f"✅ Generated! Style: {style}, {len(video_frames)} frames", temp_path
            
        except Exception as ex:
            return f"❌ Error: {str(ex)}", None
    
    with gr.Blocks(
        css=CUSTOM_CSS,
        theme=gr.themes.Base(
            primary_hue=gr.themes.colors.neutral,
            secondary_hue=gr.themes.colors.neutral,
            neutral_hue=gr.themes.colors.neutral,
        ),
        title="VEDA – AI Video Generator"
    ) as demo:
        gr.HTML("""
            <div class="top-nav">
                <div class="brand"><span class="dot"></span> VEDA</div>
                <div class="nav-links"><a href="#">Generate</a></div>
            </div>
            <div class="hero-section">
                <h1>VEDA 2.0</h1>
                <p>AI Video Generator — Running on Colab GPU</p>
            </div>
        """)
        
        with gr.Row():
            with gr.Column():
                prompt = gr.Textbox(label="Prompt", placeholder="Describe your video...", lines=3)
                style = gr.Dropdown(
                    ["Cinematic", "Portrait", "Product", "Nature", "Aesthetic", "Reels"],
                    value="Cinematic", label="Style"
                )
                
                with gr.Accordion("⚙️ Settings", open=False):
                    frames = gr.Slider(8, 24, 16, step=4, label="Frames")
                    seed = gr.Number(42, label="Seed")
                    upscale = gr.Checkbox(True, label="🔬 Upscale (Real-ESRGAN 4x)")
                
                btn = gr.Button("✨ Generate", variant="primary", elem_classes=["generate-btn"])
        
        status = gr.Textbox(label="Status", value="Ready")
        video = gr.Video(label="Video")
        
        btn.click(generate_video, [prompt, style, frames, seed, upscale], [status, video])
    
    return demo


if __name__ == "__main__":
    print("[VEDA 2.0] AI Video Generator")
    print("Starting Seedance-style interface...")
    demo = create_demo_interface()
    demo.launch(share=False)
