"""
VEDA Colab Client - Connect to Colab's Gradio API for remote video generation.
"""

from gradio_client import Client
from typing import Optional, Tuple
import os
import tempfile
import shutil


class ColabClient:
    """
    Client to connect local VEDA app to a running Colab notebook.
    Uses Gradio's Client API to send prompts and receive generated videos.
    """
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.colab_url: Optional[str] = None
        self._is_connected = False
    
    def connect(self, colab_url: str) -> Tuple[bool, str]:
        """
        Connect to a Colab Gradio endpoint.
        
        Args:
            colab_url: The Gradio share URL (e.g., https://xxxxx.gradio.live)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Clean the URL
            url = colab_url.strip()
            if not url:
                return False, "❌ Please enter a Colab URL"
            
            # Add https if missing
            if not url.startswith("http"):
                url = f"https://{url}"
            
            # Try to connect
            self.client = Client(url)
            self.colab_url = url
            self._is_connected = True
            
            return True, f"✅ Connected to Colab!"
            
        except Exception as e:
            self._is_connected = False
            return False, f"❌ Connection failed: {str(e)}"
    
    def disconnect(self):
        """Disconnect from Colab."""
        self.client = None
        self.colab_url = None
        self._is_connected = False
    
    @property
    def is_connected(self) -> bool:
        return self._is_connected and self.client is not None
    
    def generate(
        self,
        prompt: str,
        style: str = "cinematic",
        frames: int = 16,
        seed: int = 42,
        upscale: bool = True
    ) -> Tuple[str, Optional[str]]:
        """
        Generate video using Colab's GPU.
        
        Args:
            prompt: Text prompt for video generation
            style: Style preset (cinematic, portrait, etc.)
            frames: Number of frames
            seed: Random seed
            upscale: Whether to upscale output
            
        Returns:
            Tuple of (status_message, video_path or None)
        """
        if not self.is_connected:
            return "❌ Not connected to Colab. Please enter URL and connect first.", None
        
        try:
            # Try different API endpoint names that Gradio might use
            api_names_to_try = [
                None,  # Use default/first endpoint
                "/generate",
                "/generate_0", 
                "/generate_video",
                0,  # First function by index
            ]
            
            result = None
            last_error = None
            
            for api_name in api_names_to_try:
                try:
                    if api_name is None:
                        # Try calling without specifying api_name (uses first available)
                        result = self.client.predict(
                            prompt,
                            style.lower(),
                            frames,
                            seed,
                            upscale,
                        )
                    elif isinstance(api_name, int):
                        # Try by index
                        result = self.client.predict(
                            prompt,
                            style.lower(),
                            frames,
                            seed,
                            upscale,
                            fn_index=api_name
                        )
                    else:
                        result = self.client.predict(
                            prompt,
                            style.lower(),
                            frames,
                            seed,
                            upscale,
                            api_name=api_name
                        )
                    break  # Success!
                except Exception as e:
                    last_error = str(e)
                    if "Cannot find" not in last_error:
                        # Different error, re-raise
                        raise
                    continue
            
            if result is None:
                return f"❌ Could not find generate endpoint: {last_error}", None
            
            # Result is typically (status_text, video_path)
            if isinstance(result, tuple) and len(result) >= 2:
                status, video_path = result[0], result[1]
                
                if video_path:
                    # Copy to local temp file if it's a remote path
                    local_path = self._download_video(video_path)
                    return status, local_path
                
                return status, None
            
            # Single return value
            return "✅ Generated!", result if isinstance(result, str) else None
            
        except Exception as e:
            error_msg = str(e)
            if "queue" in error_msg.lower():
                return "⏳ Colab is busy. Please wait and try again.", None
            return f"❌ Generation failed: {error_msg}", None
    
    def _download_video(self, remote_path: str) -> Optional[str]:
        """Download video from Gradio's file server to local temp."""
        try:
            # If it's already a local path, return it
            if os.path.exists(remote_path):
                return remote_path
            
            # For Gradio, the path is already downloaded by the client
            return remote_path
            
        except Exception as e:
            print(f"Download error: {e}")
            return None


# Singleton instance
_colab_client = ColabClient()


def get_colab_client() -> ColabClient:
    """Get the global Colab client instance."""
    return _colab_client
