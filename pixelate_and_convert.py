import sys
import os
from PIL import Image
import re
import math
import cv2
import shutil
import subprocess

# ===============================================
# FFMPEG AND VIDEO CONVERSION
# ===============================================
def check_ffmpeg():
    """Checks if ffmpeg is installed and in the system's PATH."""
    if shutil.which("ffmpeg") is None:
        print("❌ Error: ffmpeg is not installed or not in your PATH.")
        print("Please install ffmpeg to convert .mov files. On macOS, you can use Homebrew: brew install ffmpeg")
        return False
    return True

def convert_mov_to_mp4(mov_path):
    """Converts a .mov file to .mp4 using ffmpeg."""
    if not check_ffmpeg():
        return None

    # Create the new path for the .mp4 file in the same directory
    mp4_path = os.path.splitext(mov_path)[0] + ".mp4"
    
    print(f"🔄 Found .mov file. Converting to '{os.path.basename(mp4_path)}'...")
    
    try:
        # Use subprocess to run the ffmpeg command.
        # -y overwrites the output file if it exists.
        # -loglevel error suppresses all output except for critical errors.
        result = subprocess.run(
            ["ffmpeg", "-i", mov_path, "-c:v", "libx264", "-c:a", "aac", "-y", mp4_path],
            check=True,
            capture_output=True, 
            text=True
        )
        print("✅ Conversion successful!")
        return mp4_path
    except FileNotFoundError:
        # This case is already handled by check_ffmpeg, but it's good practice to have it.
        print("❌ Error: ffmpeg command not found.")
        return None
    except subprocess.CalledProcessError as e:
        # This catches errors from the ffmpeg process itself (e.g., invalid input file).
        print(f"❌ Error during ffmpeg conversion:")
        print(e.stderr)
        return None

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
    os.makedirs(output_folder, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file at '{video_path}'")
        return

    original_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_in_seconds = total_frames / original_fps

    print(f"Video Info: {original_fps:.2f} FPS, {total_frames} total frames, {duration_in_seconds:.2f}s duration.")
    print(f"Slicing video to {frames_per_second} frames per second...")

    num_output_frames = int(duration_in_seconds * frames_per_second)
    saved_frame_count = 0

    for i in range(num_output_frames):
        target_timestamp = i / frames_per_second
        source_frame_index = round(target_timestamp * original_fps)

        if source_frame_index >= total_frames:
            break

        cap.set(cv2.CAP_PROP_POS_FRAMES, source_frame_index)
        
        ret, frame = cap.read()
        if ret:
            output_filename = os.path.join(output_folder, f"frame_{saved_frame_count:05d}.png")
            cv2.imwrite(output_filename, frame)
            saved_frame_count += 1
        else:
            print(f"Warning: Could not read frame at index {source_frame_index}. Stopping.")
            break
            
    cap.release()
    print(f"✅ Success! Extracted {saved_frame_count} frames to '{output_folder}'.")


# ===============================================
# IMAGE PROCESSING FUNCTIONS
# ===============================================
def filter_dark_pixels(small_pixelated, grid_width, grid_height, threshold=10, dimming_threshold=30):
    """Filters and dims pixels based on brightness thresholds."""
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

def enhance_contrast_if_many_active(frames, grid_width=18, grid_height=11, on=True):
    """Optionally applies contrast enhancement to frames."""
    if not on:
        return frames
    k = 0.03  
    center = 175.0
    for img in frames:
        for y in range(grid_height):
            for x in range(grid_width):
                val = img.getpixel((x, y))
                x_f = float(val)
                sigmoid = 1.0 / (1.0 + math.exp(-k * (x_f - center)))
                new_val = int(sigmoid * 255.0)
                img.putpixel((x, y), new_val)
    return frames

def process_image(input_path, output_path, grid_width=18, grid_height=11, cell_width=50, return_pixelated=False):
    """Processes a single image: resizes, pixelates, and saves it."""
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
    original_img = original_img.convert('L')
    
    original_width, original_height = original_img.size
    scale_factor = max(canvas_width / original_width, canvas_height / original_height)
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)
    resized_img = original_img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    paste_x = (canvas_width - new_width) // 2
    paste_y = (canvas_height - new_height) // 2
    background.paste(resized_img, (paste_x, paste_y))

    small_pixelated = background.resize((grid_width, grid_height), Image.Resampling.LANCZOS)
    small_pixelated = filter_dark_pixels(small_pixelated, grid_width, grid_height)
    final_image = small_pixelated.resize((canvas_width, canvas_height), Image.Resampling.NEAREST)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_image.save(output_path)

    if return_pixelated:
        return small_pixelated

# ===============================================
# C CODE GENERATION
# ===============================================
def generate_c_struct_array(frame_data_list, grid_width, grid_height, c_output_path, struct_variable_name):
    """Generate a C struct array from multiple frame data."""
    c_code = [
        '// Generated by the pixelator script.\n',
        '#include "frames_as_c_code.h"\n\n',
        f'animation_frame const {struct_variable_name}[{len(frame_data_list)}] = {{\n'
    ]

    for small_pixelated, frame_number in frame_data_list:
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

        c_code.extend(['        },\n', '    },\n'])
    c_code.append('};\n')

    os.makedirs(os.path.dirname(c_output_path), exist_ok=True)
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

# ===============================================
# MAIN EXECUTION
# ===============================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python pixelate_and_convert.py <input_directory>")
        print("  python pixelate_and_convert.py <video_file> --fps <frames_per_second>")
        print("  python pixelate_and_convert.py <video_file> --fps 10 --struct-name my_animation")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    # --- Video Processing Logic ---
    if input_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        
        # Handle .mov conversion
        if input_path.lower().endswith('.mov'):
            converted_path = convert_mov_to_mp4(input_path)
            if converted_path:
                input_path = converted_path  # Update path to the new .mp4 file
            else:
                print("Aborting due to conversion failure.")
                sys.exit(1)

        fps = 10
        struct_name = None
        
        for i in range(2, len(sys.argv)):
            if sys.argv[i] == '--fps' and i + 1 < len(sys.argv):
                fps = int(sys.argv[i + 1])
            elif sys.argv[i] == '--struct-name' and i + 1 < len(sys.argv):
                struct_name = sys.argv[i + 1]
        
        if struct_name is None:
            video_name = os.path.splitext(os.path.basename(input_path))[0]
            struct_name = re.sub(r'[^a-zA-Z0-9_]', '_', video_name).lower()
        
        temp_frames_dir = f"temp_frames_{struct_name}"
        
        print(f"🎬 Processing video: {input_path}")
        print(f"📊 FPS: {fps}, Struct name: {struct_name}")
        
        slice_video_to_frames(input_path, temp_frames_dir, fps)
        
        if os.path.exists(temp_frames_dir):
            frame_data_list = []
            grid_width, grid_height = 18, 11
            output_animation_dir = os.path.join("output_images", struct_name)
            os.makedirs(output_animation_dir, exist_ok=True)
            
            filenames = sorted([f for f in os.listdir(temp_frames_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))], key=extract_number)
            total_files = len(filenames)
            
            if total_files > 0:
                print(f"🖼️  Processing {total_files} extracted frames...")
                for i, filename in enumerate(filenames):
                    input_file = os.path.join(temp_frames_dir, filename)
                    output_file = os.path.join(output_animation_dir, filename)
                    
                    small_pixelated = process_image(input_file, output_file, grid_width=grid_width, grid_height=grid_height, return_pixelated=True)
                    if small_pixelated:
                        frame_data_list.append((small_pixelated, i))
                    
                    progress = i + 1
                    bar_length = 40
                    percent = progress / total_files
                    filled_len = int(bar_length * percent)
                    bar = '█' * filled_len + '-' * (bar_length - filled_len)
                    sys.stdout.write(f'\r  [{bar}] {progress}/{total_files} frames processed')
                    sys.stdout.flush()
                print()

            if frame_data_list:
                print("Applying contrast enhancement if needed...")
                frame_images = [fd[0] for fd in frame_data_list]
                enhanced_frames = enhance_contrast_if_many_active(frame_images, grid_width, grid_height)
                enhanced_frame_data_list = [(enhanced_frames[i], fd[1]) for i, fd in enumerate(frame_data_list)]
                
                c_output_path = f"frames_as_c_code/{struct_name}.c"
                generate_c_struct_array(enhanced_frame_data_list, grid_width, grid_height, c_output_path, struct_name)
                
                print(f"\n✅ Successfully created animation '{struct_name}' with {len(frame_data_list)} frames")
                print(f"📁 C code saved to: {c_output_path}")
                print(f"🖼️  Preview images saved to: {output_animation_dir}")
            
            shutil.rmtree(temp_frames_dir)
            print(f"🗑️  Cleaned up temporary frames from {temp_frames_dir}")
            
    # --- Image Directory Processing Logic ---
    elif os.path.isdir(input_path):
        input_dir = input_path
        grid_width, grid_height = 18, 11

        struct_name = input("Enter the name for your C struct and file: ")
        output_animation_dir = os.path.join("output_images", struct_name)
        os.makedirs(output_animation_dir, exist_ok=True)
        
        frame_data_list = []
        filenames = sorted([f for f in os.listdir(input_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))], key=extract_number)
        total_files = len(filenames)
        
        if total_files > 0:
            print(f"🖼️  Processing {total_files} images from '{input_dir}'...")
            for i, filename in enumerate(filenames):
                input_file = os.path.join(input_dir, filename)
                output_file = os.path.join(output_animation_dir, filename)
                
                small_pixelated = process_image(input_file, output_file, grid_width=grid_width, grid_height=grid_height, return_pixelated=True)
                if small_pixelated:
                    frame_data_list.append((small_pixelated, i))

                progress = i + 1
                bar_length = 40
                percent = progress / total_files
                filled_len = int(bar_length * percent)
                bar = '█' * filled_len + '-' * (bar_length - filled_len)
                sys.stdout.write(f'\r  [{bar}] {progress}/{total_files} images processed')
                sys.stdout.flush()
            print()

        if frame_data_list:
            print("Applying contrast enhancement if needed...")
            frame_images = [fd[0] for fd in frame_data_list]
            enhanced_frames = enhance_contrast_if_many_active(frame_images, grid_width, grid_height)
            enhanced_frame_data_list = [(enhanced_frames[i], fd[1]) for i, fd in enumerate(frame_data_list)]
            
            c_output_path = f"frames_as_c_code/{struct_name}.c"
            generate_c_struct_array(enhanced_frame_data_list, grid_width, grid_height, c_output_path, struct_name)
            
            print(f"\n✅ Successfully created animation '{struct_name}' with {len(frame_data_list)} frames")
            print(f"📁 C code saved to: {c_output_path}")
            print(f"🖼️  Preview images saved to: {output_animation_dir}")

    else:
        print(f"Error: Input '{input_path}' is not a valid video file or directory.")
