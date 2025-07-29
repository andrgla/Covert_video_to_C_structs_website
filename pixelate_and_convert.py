import sys
import os
from PIL import Image
import re
import math
import cv2

# ===============================================
# SLICE IMAGE FUNCTION FROM MP4 VIDEOS
# ===============================================
def slice_video_to_frames(video_path, output_folder, frames_per_second=30):
    """
    Extracts frames from a video at a specified rate.

    Args:
        video_path (str): The full path to the input MP4 video file.
        output_folder (str): The directory to save the extracted frames.
        frames_per_second (int): The number of frames to extract for each second of video.
    """
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file at '{video_path}'")
        return

    # Get video properties
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_in_seconds = total_frames / original_fps

    print(f"Video Info: {original_fps:.2f} FPS, {total_frames} total frames, {duration_in_seconds:.2f}s duration.")
    print(f"Slicing video to {frames_per_second} frames per second...")

    # Calculate the total number of frames to generate
    num_output_frames = int(duration_in_seconds * frames_per_second)
    saved_frame_count = 0

    # Loop through the desired number of output frames
    for i in range(num_output_frames):
        # Calculate the timestamp for this new frame
        target_timestamp = i / frames_per_second
        
        # Calculate the corresponding frame index in the original video
        source_frame_index = round(target_timestamp * original_fps)

        # Prevent seeking beyond the last frame
        if source_frame_index >= total_frames:
            break

        # Set the video capture to the specific frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, source_frame_index)
        
        ret, frame = cap.read()
        if ret:
            # Save the captured frame as a PNG image
            output_filename = os.path.join(output_folder, f"frame_{saved_frame_count:05d}.png")
            cv2.imwrite(output_filename, frame)
            saved_frame_count += 1
        else:
            # Break the loop if a frame cannot be read
            print(f"Warning: Could not read frame at index {source_frame_index}. Stopping.")
            break
            
    # Release the video capture object
    cap.release()
    print(f"✅ Success! Extracted {saved_frame_count} frames to '{output_folder}'.")


# ===============================================
# FILTER DARK PIXELS FUNCTION
# ===============================================
def filter_dark_pixels(small_pixelated, grid_width, grid_height, max_pixels=150, threshold=10, dimming_threshold=30):
    """
    Filters and dims pixels based on brightness thresholds.

    - Pixels with brightness <= `threshold` are set to 0.
    - Pixels with brightness between `threshold` and `dimming_threshold` are dimmed.
    """
    filtered_image = small_pixelated.copy()

    for y in range(grid_height):
        for x in range(grid_width):
            brightness = filtered_image.getpixel((x, y))

            if not isinstance(brightness, int) or brightness == 0:
                continue

            if brightness <= threshold:
                filtered_image.putpixel((x, y), 0)
            elif threshold < brightness <= dimming_threshold:
                new_brightness = brightness - (brightness**2 * (1 / dimming_threshold))
                filtered_image.putpixel((x, y), int(max(0, new_brightness)))

    return filtered_image

# ===============================================
# ENHANCE CONTRAST FUNCTION
# ===============================================
def enhance_contrast_if_many_active(frames, grid_width=18, grid_height=11, on=True):
    """
    Optionally applies contrast enhancement to frames if the average number of active pixels is high.
    If 'on' is False, this function does nothing and returns the frames unchanged.
    """
    if not on:
        return frames

    if on is True:
        k = 0.025  # Steepness (weaker contrast, half as strong as before)
        center = 150.0
        for img in frames:
            for y in range(grid_height):
                for x in range(grid_width):
                    val = img.getpixel((x, y))
                    x_f = float(val)
                    sigmoid = 1.0 / (1.0 + math.exp(-k * (x_f - center)))
                    new_val = int(sigmoid * 255.0)
                    img.putpixel((x, y), new_val)
    return frames


# ===============================================
# PROCESS IMAGE FUNCTION
# ===============================================
def process_image(input_path, output_path, grid_width=18, grid_height=11, cell_width=50,
                  struct_variable_name="animation_frame", frame_number=0, return_pixelated=False):
    try:
        original_img = Image.open(input_path)
    except FileNotFoundError:
        print(f"Error: The file '{input_path}' was not found.")
        return
    except Exception as e:
        print(f"Error opening or processing image: {e}")
        return

    cell_height = int(cell_width * 1.6)
    canvas_width = grid_width * cell_width
    canvas_height = grid_height * cell_height

    background = Image.new('L', (canvas_width, canvas_height), 0)
    print(f"Created a black canvas with {grid_width}:{grid_height} grid, each cell {cell_width}x{cell_height}.")

    original_img = original_img.convert('L')
    original_width, original_height = original_img.size

    scale_factor = max(canvas_width / original_width, canvas_height / original_height)
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)

    resized_img = original_img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    paste_x = (canvas_width - new_width) // 2
    paste_y = (canvas_height - new_height) // 2

    background.paste(resized_img, (paste_x, paste_y))
    print("Centered and resized the original image onto the canvas (cropped to fill).")

    small_pixelated = background.resize((grid_width, grid_height), Image.Resampling.LANCZOS)
    print(f"Pixelated the image down to {grid_width}x{grid_height} pixels.")

    small_pixelated = filter_dark_pixels(small_pixelated, grid_width, grid_height)

    final_image = small_pixelated.resize((canvas_width, canvas_height), Image.Resampling.NEAREST)
    print("Scaled the pixelated image up for viewing.")

    output_dir = "output_images"
    os.makedirs(output_dir, exist_ok=True)
    output_full_path = os.path.join(output_dir, os.path.basename(output_path))

    final_image.save(output_full_path)
    print(f"Successfully saved the processed image to '{output_full_path}'")

    if return_pixelated:
        return small_pixelated

# ===============================================
# GENERATE C STRUCT ARRAY FUNCTION
# ===============================================
def generate_c_struct_array(frame_data_list, grid_width, grid_height, c_output_path, struct_variable_name):
    """Generate a C struct array from multiple frame data."""
    c_code = [
        '// Generated by the pixelator script.\n',
        '#include "frames_as_c_code.h"\n\n',
        f'animation_frame const {struct_variable_name}[{len(frame_data_list)}] = {{\n'
    ]

    for small_pixelated, frame_number in frame_data_list:
        # Apply dark pixel filtering
        small_pixelated = filter_dark_pixels(small_pixelated, grid_width, grid_height)
        
        # Apply contrast enhancement if needed (for individual frame processing)
        # This is a backup in case the main enhancement wasn't applied
        frame_list = [small_pixelated]
        enhanced_frame = enhance_contrast_if_many_active(frame_list, grid_width, grid_height)[0]
        
        pixels = []
        for y in range(grid_height):
            for x in range(grid_width):
                brightness = enhanced_frame.getpixel((x, y))
                if brightness > 0:
                    pixels.append({'x': x, 'y': y, 'brightness': brightness})

        c_code.extend([
            '    {\n',
            f'        .frame_number = {frame_number},\n',
            f'        .num_pixels = {len(pixels)},\n',
            '        .brightness_levels = {\n'
        ])

        for p in pixels:
            c_code.append(f'            [ANIMATION_PIXEL_INDEX({p["y"]}, {p["x"]})] = {p["brightness"]},\n')

        c_code.extend([
            '        },\n',
            '    },\n'
        ])

    c_code.append('};\n')

    output_dir = os.path.dirname(c_output_path)
    os.makedirs(output_dir, exist_ok=True)
    with open(c_output_path, 'w') as f:
        f.write("".join(c_code))
    print(f"Successfully saved C struct array to '{c_output_path}'")

    header_path = os.path.join(os.path.dirname(c_output_path), "..", "frames_as_c_code.h")
    declaration = f"extern const animation_frame {struct_variable_name}[{len(frame_data_list)}];\n"
    try:
        with open(header_path, 'r') as h_file:
            if declaration in h_file.read():
                print(f"Declaration for {struct_variable_name} already in {header_path}")
                return
    except FileNotFoundError:
        pass

    with open(header_path, 'a') as h_file:
        h_file.write(declaration)
        print(f"Appended extern declaration for {struct_variable_name} to {header_path}")

def extract_number(filename):
    match = re.search(r'(\d+)', filename)
    return int(match.group(1)) if match else -1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python pixelate_and_convert.py <input_directory>")
        print("  python pixelate_and_convert.py <video_file> --fps <frames_per_second>")
        print("  python pixelate_and_convert.py <video_file> --fps 10 --struct-name my_animation")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    # Check if it's a video file
    if input_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        # Handle video file
        fps = 10  # default
        struct_name = None
        
        # Parse additional arguments
        for i in range(2, len(sys.argv)):
            if sys.argv[i] == '--fps' and i + 1 < len(sys.argv):
                fps = int(sys.argv[i + 1])
            elif sys.argv[i] == '--struct-name' and i + 1 < len(sys.argv):
                struct_name = sys.argv[i + 1]
        
        if struct_name is None:
            # Derive struct name from video filename
            video_name = os.path.splitext(os.path.basename(input_path))[0]
            struct_name = video_name.replace('-', '_').replace(' ', '_').lower()
        
        # Create temporary directory for frames
        temp_frames_dir = f"temp_frames_{struct_name}"
        
        print(f"🎬 Processing video: {input_path}")
        print(f"📊 FPS: {fps}, Struct name: {struct_name}")
        
        # Slice video to frames
        slice_video_to_frames(input_path, temp_frames_dir, fps)
        
        # Process the extracted frames
        if os.path.exists(temp_frames_dir):
            frame_data_list = []
            grid_width = 18
            grid_height = 11
            
            filenames = sorted(
                [f for f in os.listdir(temp_frames_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))],
                key=extract_number
            )
            
            print(f"🖼️  Processing {len(filenames)} extracted frames...")
            for i, filename in enumerate(filenames):
                input_file = os.path.join(temp_frames_dir, filename)
                output_file = os.path.join("output_images", f"{struct_name}_{filename}")
                print(f"Processing frame {i+1}/{len(filenames)}: {filename}")
                small_pixelated = process_image(input_file, output_file, grid_width=grid_width,
                                              grid_height=grid_height, frame_number=i, return_pixelated=True)
                if small_pixelated:
                    frame_data_list.append((small_pixelated, i))
            
            if frame_data_list:
                # Apply contrast enhancement if many pixels are active
                print("Applying contrast enhancement if needed...")
                frame_images = [frame_data[0] for frame_data in frame_data_list]
                enhanced_frames = enhance_contrast_if_many_active(frame_images, grid_width, grid_height)
                
                # Update frame_data_list with enhanced frames
                enhanced_frame_data_list = []
                for i, (_, frame_number) in enumerate(frame_data_list):
                    enhanced_frame_data_list.append((enhanced_frames[i], frame_number))
                
                # Generate C struct array
                c_output_path = f"frames_as_c_code/{struct_name}.c"
                
                generate_c_struct_array(
                    enhanced_frame_data_list,
                    grid_width=grid_width,
                    grid_height=grid_height,
                    c_output_path=c_output_path,
                    struct_variable_name=struct_name
                )
                
                print(f"\n✅ Successfully created animation '{struct_name}' with {len(frame_data_list)} frames")
                print(f"📁 C code saved to: {c_output_path}")
                print(f"🖼️  Preview images saved to: output_images/{struct_name}_*")
                
                # Clean up temporary frames
                import shutil
                shutil.rmtree(temp_frames_dir)
                print(f"🗑️  Cleaned up temporary frames from {temp_frames_dir}")
            
    elif os.path.isdir(input_path):
        # Handle directory of images (existing functionality)
        input_dir = input_path
        output_dir = "output_images"
        os.makedirs(output_dir, exist_ok=True)
        frame_data_list = []
        grid_width = 18
        grid_height = 11

        filenames = sorted(
            [f for f in os.listdir(input_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))],
            key=extract_number
        )
        for i, filename in enumerate(filenames):
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_dir, filename)
            print(f"Processing {input_file}...")
            small_pixelated = process_image(input_file, output_file, grid_width=grid_width,
                                          grid_height=grid_height, frame_number=i, return_pixelated=True)
            if small_pixelated:
                frame_data_list.append((small_pixelated, i))

        if frame_data_list:
            # Apply contrast enhancement if many pixels are active
            print("Applying contrast enhancement if needed...")
            frame_images = [frame_data[0] for frame_data in frame_data_list]
            enhanced_frames = enhance_contrast_if_many_active(frame_images, grid_width, grid_height)
            
            # Update frame_data_list with enhanced frames
            enhanced_frame_data_list = []
            for i, (_, frame_number) in enumerate(frame_data_list):
                enhanced_frame_data_list.append((enhanced_frames[i], frame_number))
            
            # Prompt user for the struct and file name
            struct_name = input("Enter the name for your C struct and file: ")
            
            # Construct the output path dynamically
            c_output_path = f"frames_as_c_code/{struct_name}.c"
            
            generate_c_struct_array(
                enhanced_frame_data_list,
                grid_width=grid_width,
                grid_height=grid_height,
                c_output_path=c_output_path,
                struct_variable_name=struct_name
            )

    else:
        print("Error: Input must be either a directory of images or a video file (.mp4, .avi, .mov, .mkv)")
        print("Usage:")
        print("  python pixelate_and_convert.py <input_directory>")
        print("  python pixelate_and_convert.py <video_file> --fps <frames_per_second>")
        print("  python pixelate_and_convert.py <video_file> --fps 10 --struct-name my_animation")