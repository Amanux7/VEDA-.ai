"""
VEDA Web UI - Minimalist Video Generator
Clean, simple interface for video creation.
Supports local preview and Colab GPU generation.
"""

import gradio as gr
from typing import Optional
import os

# Import Prompt Brain and Colab Client
from veda_engine.core.prompt_brain import PromptBrain, STYLES
from veda_app.colab_client import get_colab_client

brain = PromptBrain()
colab = get_colab_client()

# Custom CSS for minimalist design
CUSTOM_CSS = """
:root {
    --primary: #6366f1;
    --bg: #0f0f0f;
    --surface: #1a1a1a;
    --text: #ffffff;
    --text-muted: #888888;
}

.gradio-container {
    max-width: 800px !important;
    margin: auto !important;
    font-family: 'Inter', sans-serif !important;
}

.main-title {
    text-align: center;
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #6366f1, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}

.subtitle {
    text-align: center;
    color: var(--text-muted);
    font-size: 1rem;
    margin-bottom: 2rem;
}

.generate-btn {
    background: linear-gradient(135deg, #6366f1, #a855f7) !important;
    border: none !important;
    font-size: 1.1rem !important;
    padding: 12px 32px !important;
}

.idea-chip {
    background: var(--surface);
    border: 1px solid #333;
    border-radius: 20px;
    padding: 8px 16px;
    cursor: pointer;
    transition: all 0.2s;
}

.idea-chip:hover {
    border-color: var(--primary);
}
"""


def enhance_and_show(prompt: str, style: str) -> str:
    """Enhance prompt and show preview."""
    result = brain.enhance(prompt, style.lower())
    return f"✨ {result['prompt']}"


def get_random_idea() -> str:
    """Get a random content idea."""
    import random
    ideas = brain.suggest_ideas("trending")
    return random.choice(ideas)


def create_demo_interface():
    """Create the main Gradio interface with Colab integration."""
    
    # Connection handler
    def connect_to_colab(url):
        success, message = colab.connect(url)
        return message
    
    # Generate using Colab
    def generate_video(prompt, style, frames, seed, upscale):
        if not prompt.strip():
            return "❌ Please enter a prompt", None
        
        if not colab.is_connected:
            return "⚠️ Connect to Colab first! Run the notebook and paste the URL above.", None
        
        # Generate via Colab
        status, video_path = colab.generate(
            prompt=prompt,
            style=style.lower(),
            frames=int(frames),
            seed=int(seed),
            upscale=upscale
        )
        
        return status, video_path
    
    with gr.Blocks(css=CUSTOM_CSS, theme=gr.themes.Soft(primary_hue="indigo")) as demo:
        
        # Header
        gr.HTML("""
            <div class="main-title">🎬 VEDA</div>
            <div class="subtitle">AI Video Generator</div>
        """)
        
        # Colab Connection Section
        with gr.Accordion("🔗 Connect to Colab GPU", open=True):
            gr.HTML("""
                <p style='color: #888; font-size: 0.9rem;'>
                    Run the Colab notebook, copy the <code>gradio.live</code> URL, and paste it below.
                </p>
            """)
            with gr.Row():
                colab_url = gr.Textbox(
                    label="Colab URL",
                    placeholder="https://xxxxx.gradio.live",
                    scale=3
                )
                connect_btn = gr.Button("🔌 Connect", scale=1)
            connection_status = gr.Textbox(
                label="Status",
                value="⚪ Not connected",
                interactive=False
            )
            connect_btn.click(
                fn=connect_to_colab,
                inputs=[colab_url],
                outputs=[connection_status]
            )
        
        gr.HTML("<hr style='border-color: #333; margin: 1rem 0;'>")
        
        with gr.Row():
            with gr.Column(scale=2):
                # Prompt Input
                prompt_input = gr.Textbox(
                    label="What do you want to create?",
                    placeholder="woman smiling, sunset beach, coffee steam...",
                    lines=2,
                    max_lines=3
                )
                
                # Style Selector
                style_dropdown = gr.Dropdown(
                    choices=["Cinematic", "Portrait", "Product", "Nature", "Aesthetic", "Reels"],
                    value="Cinematic",
                    label="Style"
                )
                
                # Enhanced Preview
                enhanced_preview = gr.Textbox(
                    label="Enhanced Prompt",
                    interactive=False,
                    lines=2
                )
                
                # Settings (collapsed by default)
                with gr.Accordion("⚙️ Advanced Settings", open=False):
                    frames_slider = gr.Slider(8, 24, value=16, step=4, label="Frames")
                    seed_input = gr.Number(value=42, label="Seed")
                    upscale_toggle = gr.Checkbox(value=True, label="Upscale to 1024px")
                
                # Generate Button
                generate_btn = gr.Button("✨ Generate Video", variant="primary", elem_classes=["generate-btn"])
        
        gr.HTML("<hr style='border-color: #333; margin: 2rem 0;'>")
        
        # Quick Ideas Section
        gr.HTML("<p style='color: #888; text-align: center;'>💡 Quick Ideas</p>")
        
        with gr.Row():
            idea_btn = gr.Button("🎲 Random Idea", size="sm")
        
        # Ideas Gallery
        ideas_display = gr.Textbox(
            label="Try this prompt",
            value="beautiful sunset over ocean, golden light, waves, cinematic",
            interactive=True
        )
        
        gr.HTML("<hr style='border-color: #333; margin: 2rem 0;'>")
        
        # Output Section
        with gr.Row():
            with gr.Column():
                status_text = gr.Textbox(label="Status", value="Ready - Connect to Colab to generate", interactive=False)
                output_video = gr.Video(label="Generated Video")
        
        # Event Handlers
        prompt_input.change(
            fn=enhance_and_show,
            inputs=[prompt_input, style_dropdown],
            outputs=[enhanced_preview]
        )
        
        style_dropdown.change(
            fn=enhance_and_show,
            inputs=[prompt_input, style_dropdown],
            outputs=[enhanced_preview]
        )
        
        idea_btn.click(
            fn=get_random_idea,
            outputs=[ideas_display]
        )
        
        ideas_display.change(
            fn=lambda x: x,
            inputs=[ideas_display],
            outputs=[prompt_input]
        )
        
        generate_btn.click(
            fn=generate_video,
            inputs=[prompt_input, style_dropdown, frames_slider, seed_input, upscale_toggle],
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
                negative_prompt=e["negative"],
                num_frames=int(frames),
                num_inference_steps=e["steps"],
                guidance_scale=e["guidance"],
                generator=torch.Generator("cpu").manual_seed(int(seed)),
            )
            
            video_frames = output.frames[0]
            
            if upscale:
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
    
    with gr.Blocks(css=CUSTOM_CSS, theme=gr.themes.Soft(primary_hue="indigo")) as demo:
        gr.HTML("""
            <div class="main-title">🎬 VEDA</div>
            <div class="subtitle">AI Video Generator</div>
        """)
        
        with gr.Row():
            with gr.Column():
                prompt = gr.Textbox(label="Prompt", placeholder="woman smiling...", lines=2)
                style = gr.Dropdown(
                    ["Cinematic", "Portrait", "Product", "Nature", "Aesthetic", "Reels"],
                    value="Cinematic", label="Style"
                )
                
                with gr.Accordion("⚙️ Settings", open=False):
                    frames = gr.Slider(8, 24, 16, step=4, label="Frames")
                    seed = gr.Number(42, label="Seed")
                    upscale = gr.Checkbox(True, label="Upscale")
                
                btn = gr.Button("✨ Generate", variant="primary")
        
        status = gr.Textbox(label="Status", value="Ready")
        video = gr.Video(label="Video")
        
        btn.click(generate_video, [prompt, style, frames, seed, upscale], [status, video])
    
    return demo


if __name__ == "__main__":
    print("🎬 VEDA Web UI")
    print("Starting local demo mode...")
    demo = create_demo_interface()
    demo.launch(share=False)
