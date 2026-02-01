#!/usr/bin/env python3
# Generate or edit images using Google Gemini API
import os
import sys
import argparse
import uuid
import time
import subprocess
from functools import wraps

# Auto-check dependencies on import
try:
    from dotenv import load_dotenv
    from google import genai
    from google.genai import types
    from PIL import Image
    from io import BytesIO
except ImportError as e:
    print(f"❌ 缺少依赖: {e}")
    print("🔧 正在自动安装依赖...\n")

    # Get script directory and run setup_dependencies.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    setup_script = os.path.join(script_dir, "setup_dependencies.py")

    if os.path.exists(setup_script):
        result = subprocess.run([sys.executable, setup_script])
        if result.returncode == 0:
            print("\n✅ 依赖安装完成，请重新运行此脚本")
        else:
            print("\n❌ 依赖安装失败，请手动运行:")
            print(f"   python3 {setup_script}")
        sys.exit(1)
    else:
        print(f"❌ 未找到 setup_dependencies.py: {setup_script}")
        print("请手动安装依赖: pip install google-genai Pillow python-dotenv")
        sys.exit(1)

# Import shared configuration
try:
    from config import ASPECT_RATIO_MAP, RETRY_CONFIG
except ImportError:
    # Fallback if config.py not found
    ASPECT_RATIO_MAP = {
        "1024x1024": "1:1",
        "832x1248": "2:3",
        "1248x832": "3:2",
        "864x1184": "3:4",
        "1184x864": "4:3",
        "896x1152": "4:5",
        "1152x896": "5:4",
        "768x1344": "9:16",
        "1344x768": "16:9",
        "1536x672": "21:9",
    }
    RETRY_CONFIG = {
        "max_attempts": 3,
        "initial_delay": 2,
        "backoff_factor": 1.5,
        "retriable_errors": ["SSL", "ConnectionError", "TimeoutError", "NetworkError", "500", "502", "503", "504"]
    }

# Priority: Environment variable > .nanobanana.env file
# This prevents configuration inconsistency issues
api_key = os.getenv("GEMINI_API_KEY")

# Fallback: Load from ~/.nanobanana.env if environment variable not set
if not api_key:
    dotenv_path = os.path.expanduser("~/.nanobanana.env")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
        api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "Missing GEMINI_API_KEY. Please either:\n"
        "  1. Set environment variable: export GEMINI_API_KEY=your_key_here\n"
        "  2. Or create ~/.nanobanana.env with: GEMINI_API_KEY=your_key_here\n"
        "Priority: Environment variable > .nanobanana.env file"
    )

# CRITICAL FIX: Remove GOOGLE_API_KEY from environment to prevent conflicts
# google.genai library prioritizes GOOGLE_API_KEY over explicit api_key parameter
# This prevents using an exhausted GOOGLE_API_KEY when GEMINI_API_KEY is valid
if "GOOGLE_API_KEY" in os.environ:
    del os.environ["GOOGLE_API_KEY"]

# Initialize Gemini client
client = genai.Client(api_key=api_key)


def retry_on_error(max_attempts=None, initial_delay=None, backoff_factor=None):
    """
    Decorator to retry function calls on specific errors with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts (default from RETRY_CONFIG)
        initial_delay: Initial delay in seconds (default from RETRY_CONFIG)
        backoff_factor: Multiplier for delay on each retry (default from RETRY_CONFIG)
    """
    max_attempts = max_attempts or RETRY_CONFIG["max_attempts"]
    initial_delay = initial_delay or RETRY_CONFIG["initial_delay"]
    backoff_factor = backoff_factor or RETRY_CONFIG["backoff_factor"]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_str = str(e)

                    # Check if error is retriable
                    is_retriable = any(
                        err_pattern in error_str
                        for err_pattern in RETRY_CONFIG["retriable_errors"]
                    )

                    if not is_retriable or attempt >= max_attempts:
                        raise

                    print(f"⚠️  Attempt {attempt}/{max_attempts} failed: {error_str[:100]}")
                    print(f"   Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                    delay *= backoff_factor

        return wrapper
    return decorator


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Generate or edit images using Google Gemini API"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="Prompt for image generation or editing",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=f"nanobanana-{uuid.uuid4()}.png",
        help="Output image filename (default: nanobanana-<UUID>.png)",
    )
    parser.add_argument(
        "--input", type=str, nargs="*", help="Input image files for editing (optional)"
    )
    parser.add_argument(
        "--size",
        type=str,
        default="1344x768",
        choices=list(ASPECT_RATIO_MAP.keys()),
        help="Size/aspect ratio of the generated image (default: 1344x768 / 16:9 - landscape cover)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-3-pro-image-preview",
        choices=["gemini-3-pro-image-preview", "gemini-2.5-flash-image"],
        help="Model to use for image generation (default: gemini-3-pro-image-preview)",
    )
    parser.add_argument(
        "--resolution",
        type=str,
        default="1K",
        choices=["1K", "2K", "4K"],
        help="Resolution of the generated image (default: 1K)",
    )
    parser.add_argument(
        "--enhance",
        action="store_true",
        help="Automatically enhance the prompt using Gemini before generation",
    )

    args = parser.parse_args()

    # Get aspect ratio from size
    aspect_ratio = ASPECT_RATIO_MAP.get(args.size, "16:9")

    # Build contents list for the API call
    contents = []

    # Check if input images are provided
    if args.input and len(args.input) > 0:
        # Use images.generate_content() with images for editing
        print(f"Editing images with prompt: {args.prompt}")
        print(f"Input images: {args.input}")
        print(f"Aspect ratio: {aspect_ratio} ({args.size})")

        # Add prompt first
        contents.append(args.prompt)

        # Add all input images
        for img_path in args.input:
            image = Image.open(img_path)
            contents.append(image)
    else:
        # Prompt enhancement logic
        final_prompt = args.prompt
        if args.enhance:
            print(f"✨ Enhancing prompt: {args.prompt}")
            try:
                final_prompt = enhance_prompt(client, args.prompt)
                print(f"🚀 Enhanced prompt: {final_prompt}")
            except Exception as e:
                print(f"⚠️  Prompt enhancement failed: {e}")
                print(f"   Using original prompt.")

        print(f"Generating image (size: {args.size}) with prompt: {final_prompt}")
        contents.append(final_prompt)

    # Generate image with retry logic
    generate_image_with_retry(args.model, contents, aspect_ratio, args.resolution, args.output)


def enhance_prompt(client, original_prompt):
    """
    Enhance the prompt using Gemini text model.
    """
    system_instruction = (
        "You are an expert AI art prompt engineer. "
        "Your task is to rewrite the input prompt into a detailed, high-quality image generation prompt "
        "suitable for a technical blog article. "
        "Style requirements: Minimalist, modern, flat design, tech-focused, professional, high resolution, "
        "clean lines, soft lighting, tech blue and orange color scheme (optional). "
        "Avoid text in images. "
        "Output ONLY the enhanced prompt, no explanations."
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=original_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
            max_output_tokens=200,
        )
    )

    if response.text:
        return response.text.strip()
    return original_prompt



@retry_on_error()
def generate_image_with_retry(model, contents, aspect_ratio, resolution, output_path):
    """
    Generate or edit image with automatic retry on network/SSL errors.

    Args:
        model: Model name
        contents: Content list (prompt + optional images)
        aspect_ratio: Aspect ratio string
        resolution: Resolution (1K, 2K, 4K)
        output_path: Output file path
    """
    # Generate or edit image with config
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=resolution,
            ),
        ),
    )

    if (
        response.candidates is None
        or len(response.candidates) == 0
        or response.candidates[0].content is None
        or response.candidates[0].content.parts is None
    ):
        raise ValueError("No data received from the API.")

    # Extract image from response
    image_saved = False
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(f"{part.text}", end="")
        elif part.inline_data is not None and part.inline_data.data is not None:
            image = Image.open(BytesIO(part.inline_data.data))

            image.save(output_path)
            image_saved = True
            print(f"\n\nImage saved to: {output_path}")

    if not image_saved:
        print(
            "\n\nWarning: No image data found in the API response. This usually means the model returned only text. Please try again with a different prompt to make image generation more clear."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
