#!/usr/bin/env python3
# Generate or edit images using Google Gemini API
import os
import argparse
import uuid
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

# Load environment variables: env var > ~/.claude/env.json > ~/.nanobanana.env (legacy)
api_key = os.getenv("GEMINI_API_KEY") or ""

if not api_key:
    env_json_path = os.path.expanduser("~/.claude/env.json")
    if os.path.exists(env_json_path):
        try:
            import json
            with open(env_json_path) as f:
                val = json.load(f).get("gemini_api_key", "")
            if val and not str(val).startswith("your-"):
                api_key = val
        except Exception:
            pass

if not api_key:
    load_dotenv(os.path.expanduser("~") + "/.nanobanana.env")
    api_key = os.getenv("GEMINI_API_KEY") or ""

if not api_key:
    raise ValueError(
        "Missing GEMINI_API_KEY. Configure in one of:\n"
        "  1. ~/.claude/env.json (recommended): set gemini_api_key\n"
        "  2. Environment variable: export GEMINI_API_KEY=your_key\n"
        "  3. ~/.nanobanana.env: GEMINI_API_KEY=your_key (legacy)"
    )

# Initialize Gemini client
client = genai.Client(api_key=api_key)

# Aspect ratio to resolution mapping
ASPECT_RATIO_MAP = {
    "1024x1024": "1:1",  # 1:1
    "832x1248": "2:3",  # 2:3
    "1248x832": "3:2",  # 3:2
    "864x1184": "3:4",  # 3:4
    "1184x864": "4:3",  # 4:3
    "896x1152": "4:5",  # 4:5
    "1152x896": "5:4",  # 5:4
    "768x1344": "9:16",  # 9:16
    "1344x768": "16:9",  # 16:9
    "1536x672": "21:9",  # 21:9
}


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
        default="768x1344",
        choices=list(ASPECT_RATIO_MAP.keys()),
        help="Size/aspect ratio of the generated image (default: 768x1344 / 9:16)",
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
        print(f"Generating image (size: {args.size}) with prompt: {args.prompt}")
        contents.append(args.prompt)

    # Generate or edit image with config
    response = client.models.generate_content(
        model=args.model,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            tools=[types.Tool(google_search=types.GoogleSearch())],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=args.resolution,
            ),
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
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

            image.save(args.output)
            image_saved = True
            print(f"\n\nImage saved to: {args.output}")

    if not image_saved:
        print(
            "\n\nWarning: No image data found in the API response. This usually means the model returned only text. Please try again with a different prompt to make image generation more clear."
        )


if __name__ == "__main__":
    main()
