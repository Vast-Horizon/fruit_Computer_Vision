'''The warning you received, UserWarning: Palette images with Transparency expressed in bytes should be converted to RGBA images,
indicates that some of the images in your dataset have transparency expressed in a format that might not be handled optimally by your image processing pipeline.

Use this script to sort this out
'''

from PIL import Image
import os

def convert_to_rgba(image_dir):
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if file.endswith(".png"):  # Assuming the images are PNGs
                img_path = os.path.join(root, file)
                img = Image.open(img_path)
                if img.mode in ('P', 'LA') or (img.mode == 'RGBA' and img.info.get("transparency", None)):
                    img = img.convert("RGBA")
                    img.save(img_path)
                    print(f"Converted {img_path} to RGBA")

# Convert images in train, test, and validation folders
convert_to_rgba('dataset/kritik_seth/train')
convert_to_rgba('dataset/kritik_seth/test')
convert_to_rgba('dataset/kritik_seth/validation')
