import json
import os
import re
import subprocess
from typing import List
from PIL import Image, ImageDraw, ImageFont, ImageOps
import gradio as gr

# Read in the JSON file containing the comic information
with open("comic.json") as f:
    comic_info = json.load(f)["response"]

# Example format of comic information, the panel_count is variable, reccommend 1 - 4 panels for best results.
#{
#    "response": {
#        "image": "A {panel_count}-panel comic in the style of {comic_style}. Panel 1: {panel_1_description}. Panel 2: {panel_2_description}. Panel 3: {panel_3_description}.",
#        "caption": "Panel 1: '{panel_1_caption}'. Panel 2: '{panel_2_caption}'. Panel 3: '{panel_3_caption}'."
#    }
#}

# Extract the image and caption information for each panel
panels = [p.strip() for p in comic_info["caption"].split(".") if p.strip()]
style_info = re.findall("style of (.*). Panel", comic_info["image"])[0]
descriptions = re.findall("Panel \d+: (.*?)(?:\.|$)", comic_info["image"])

# Define the full path to the images directory
images_dir = os.path.join(os.getcwd(), "images")

# Ensure the images directory exists
if not os.path.exists(images_dir):
    os.makedirs(images_dir)

# Generate an image for each panel using stable diffusion and save as a new file
images: List[Image.Image] = []
for i, (desc, cap) in enumerate(zip(descriptions, panels)):
    # Combine description and caption for the prompt
    prompt = f"{desc} {cap}"

    # Use txt2img.py script to generate the image for the panel
    cmd = f"python -m stable_diffusion.scripts.txt2img --prompt '{prompt}' --scale 7.5 --ckpt {style_info} --outdir {images_dir}"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        print(f"Error generating image for panel {i+1}: {result.stderr}")

    # Load the generated image using Pillow
    image = Image.open(os.path.join(images_dir, f"{i+1}.png"))
    images.append(image)

# Combine the loaded images with the corresponding captions to create the final comic
comic = Image.new("RGB", (images[0].width * len(images), images[0].height))
for i, (image, caption) in enumerate(zip(images, panels)):
    draw = ImageDraw.Draw(comic)
    # Add the image to the comic
    comic.paste(image, (i * image.width, 0))
    # Add the caption to the comic
    font = ImageFont.truetype("arial.ttf", size=20)
    text_size = draw.textsize(caption.strip(), font=font)
    text_bg = Image.new("RGBA", (text_size[0] + 20, text_size[1] + 10), (0, 0, 0, 128))
    comic.paste(ImageOps.colorize(text_bg, "black", "black"), (i * image.width + 5, image.height - 60), text_bg)
    draw.text((i * image.width + 10, image.height - 50), caption.strip(), font=font, fill=(255, 255, 255))

# Use Gradio to display the final comic
def display_comic() -> Image.Image:
    return comic

gr.Interface(fn=display_comic, inputs=None, outputs="image").launch()

# Save the final comic as a PNG image
comic.save("final_comic.png")
