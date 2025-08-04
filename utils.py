import pixelate_and_convert
import os

# Function that generates a video of all images in subfolder in output_images/
def generate_video(subfolder):
    # Get all images in subfolder
    images = [f for f in os.listdir(subfolder) if f.endswith('.png')]
    # Sort images by name
    images.sort()
    # Generate video
    pixelate_and_convert.generate_video(images, subfolder)
