import sys
from PIL import Image
import os

def process_image(input_path, output_path, grid_width=18, grid_height=11, cell_width=50):
    """
    Centers an image in a rectangular grid, converts it to grayscale,
    and pixelates it to the specified grid dimensions.
    Each cell is rectangular: height = 1.8 * width.

    Args:
        input_path (str): The path to the input image file.
        output_path (str): The path to save the processed image file.
        grid_width (int): The number of horizontal cells in the final grid.
        grid_height (int): The number of vertical cells in the final grid.
        cell_width (int): The width of each cell in pixels (height will be 1.8x this).
    """
    try:
        # 1. Open the original image
        original_img = Image.open(input_path)
    except FileNotFoundError:
        print(f"Error: The file '{input_path}' was not found.")
        return
    except Exception as e:
        print(f"Error opening or processing image: {e}")
        return

    # 2. Define cell and canvas sizes
    cell_height = int(cell_width * 1.8)
    canvas_width = grid_width * cell_width
    canvas_height = grid_height * cell_height
    target_aspect = canvas_width / canvas_height

    # Create a new image canvas in grayscale ('L' mode) with a white background (255)
    background = Image.new('L', (canvas_width, canvas_height), 255)
    print(f"Created a white canvas with {grid_width}:{grid_height} grid, each cell {cell_width}x{cell_height}.")

    # 3. Center the original image on the canvas without distortion
    original_img = original_img.convert('L') # Convert image to grayscale first
    original_width, original_height = original_img.size
    original_aspect = original_width / original_height

    # Determine scaling to fill the canvas (crop longer side)
    scale_factor = max(canvas_width / original_width, canvas_height / original_height)
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)

    # For resampling filters:
    resample_lanczos = Image.Resampling.LANCZOS
    resample_nearest = Image.Resampling.NEAREST

    # Resize the image using a high-quality filter
    resized_img = original_img.resize((new_width, new_height), resample_lanczos)
    
    # Calculate position to paste the resized image to center it (crop overflow)
    paste_x = (canvas_width - new_width) // 2
    paste_y = (canvas_height - new_height) // 2
    
    # Paste with cropping (crop the overflowing part)
    background.paste(resized_img, (paste_x, paste_y))
    print("Centered and resized the original image onto the canvas (cropped to fill).")

    # 4. Pixelate the image to the 11x18 grid
    # First, resize down to the target grid size. This averages the colors.
    # We use a smooth filter to get a good average color for each pixel block.
    small_pixelated = background.resize((grid_width, grid_height), resample_lanczos)
    print(f"Pixelated the image down to {grid_width}x{grid_height} pixels.")

    # 5. Scale the small image back up to a viewable size
    # Use NEAREST filter to create the sharp, blocky pixel effect.
    final_image = small_pixelated.resize((canvas_width, canvas_height), resample_nearest)
    print("Scaled the pixelated image up for viewing.")

    # 6. Save the final image in the output_images folder
    output_dir = "output_images"
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.basename(output_path)
    output_full_path = os.path.join(output_dir, output_filename)

    final_image.save(output_full_path)
    print(f"Successfully saved the processed image to '{output_full_path}'")

    print(f"File size: {os.path.getsize(output_full_path)} bytes")

    print(f"Successfully processed image to '{output_full_path}'")


if __name__ == "__main__":
    # --- USAGE ---
    # Provide the input and output file paths here
    # Or pass them as command-line arguments

    if len(sys.argv) == 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        process_image(input_file, output_file)
    else:
        # --- !! CHANGE THESE LINES !! ---
        # Replace 'my_image.jpg' with the path to your picture
        input_file = "my_image.jpg"
        # The output file will be created
        output_file = "pixelated_output.png"
        print("Usage: python pixelate_image.py <input_file> <output_file>")
        print(f"Using default files: '{input_file}' and '{output_file}'\n")
        process_image(input_file, output_file)
        