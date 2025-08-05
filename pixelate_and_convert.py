import sys
import os
from PIL import Image
import re
import math
import cv2
import shutil
import subprocess

# =============================================================================
# --- SETTINGS ---
# =============================================================================

# -- Grid and Canvas Dimensions --
GRID_WIDTH = 18
GRID_HEIGHT = 11
CELL_WIDTH = 50 # Affects the output image size, not the data.
CELL_ASPECT_RATIO = 1.6 # Height/Width ratio for each cell (configurable aspect ratio)

# -- Sigmoid Contrast Enhancement --
# k: Controls the steepness of the contrast curve.
SIGMOID_K = 0.042
# center: The brightness value (0-255) that is the midpoint of the curve.
SIGMOID_CENTER = 175.0
# on: A master switch to turn contrast enhancement on or off.
ENHANCE_CONTRAST = True  # Re-enabled with fixed filtering

# -- Dark Pixel Filtering --
# threshold: Pixels at or below this brightness (0-255) will be set to 0.
FILTER_THRESHOLD = 5  # Less aggressive - was 10
# dimming_threshold: Pixels between FILTER_THRESHOLD and this value will be dimmed.
DIMMING_THRESHOLD = 15  # Less aggressive - was 30

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def validate_brightness(value):
    """Ensure brightness values are within valid 0-255 range."""
    return max(0, min(255, int(value)))

def get_processing_settings(custom_settings=None):
    """Get a complete settings dictionary with defaults."""
    default_settings = {
        'grid_width': GRID_WIDTH,
        'grid_height': GRID_HEIGHT,
        'enhance_contrast': ENHANCE_CONTRAST,
        'sigmoid_k': SIGMOID_K,
        'sigmoid_center': SIGMOID_CENTER,
        'filter_threshold': FILTER_THRESHOLD,
        'dimming_threshold': DIMMING_THRESHOLD,
        'cell_aspect_ratio': CELL_ASPECT_RATIO
    }
    
    if custom_settings:
        default_settings.update(custom_settings)
    
    return default_settings

# =============================================================================
# FFMPEG AND VIDEO CONVERSION
# =============================================================================
def check_ffmpeg():
    if shutil.which("ffmpeg") is None:
        print("❌ Error: ffmpeg is not installed or not in your PATH.")
        print("Please install ffmpeg to convert .mov files. On macOS, you can use Homebrew: brew install ffmpeg")
        return False
    return True

def convert_mov_to_mp4(mov_path):
    if not check_ffmpeg():
        return None

    mp4_path = os.path.splitext(mov_path)[0] + ".mp4"
    print(f"🔄 Found .mov file. Converting to '{os.path.basename(mp4_path)}'...")
    
    try:
        subprocess.run(
            ["ffmpeg", "-i", mov_path, "-c:v", "libx264", "-c:a", "aac", "-y", mp4_path],
            check=True,
            capture_output=True, 
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0 # Hides the console window on Windows
        )
        print("✅ Conversion successful!")
        return mp4_path
    except FileNotFoundError:
        print("❌ Error: ffmpeg command not found.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during ffmpeg conversion:")
        print(e.stderr)
        return None

# ===============================================
# SLICE IMAGE FUNCTION FROM MP4 VIDEOS
# ===============================================
def slice_video_to_frames(video_path, output_folder, frames_per_second=30):
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

def apply_filtering(image, settings):
    """Apply dark pixel filtering to an image."""
    filtered_image = image.copy()
    grid_width = settings['grid_width']
    grid_height = settings['grid_height']
    threshold = settings['filter_threshold']
    dimming_threshold = settings['dimming_threshold']
    
    pixels_changed = 0
    for y in range(grid_height):
        for x in range(grid_width):
            brightness = filtered_image.getpixel((x, y))
            if not isinstance(brightness, int) or brightness == 0:
                continue
                
            original_brightness = brightness
            
            if brightness <= threshold:
                # Set very dark pixels to black
                new_brightness = 0
            elif threshold < brightness <= dimming_threshold:
                # Gentle linear dimming instead of aggressive quadratic
                # Reduce brightness by 30% in the dimming range
                new_brightness = validate_brightness(brightness * 0.7)
            else:
                new_brightness = brightness
            
            if new_brightness != original_brightness:
                pixels_changed += 1
                filtered_image.putpixel((x, y), new_brightness)
    
    return filtered_image, pixels_changed

def apply_contrast_enhancement(image, settings):
    """Apply sigmoid contrast enhancement to an image."""
    if not settings['enhance_contrast']:
        return image, 0
    
    enhanced_image = image.copy()
    grid_width = settings['grid_width']
    grid_height = settings['grid_height']
    k = settings['sigmoid_k']
    center = settings['sigmoid_center']
    
    pixels_enhanced = 0
    for y in range(grid_height):
        for x in range(grid_width):
            val = enhanced_image.getpixel((x, y))
            x_f = float(val)
            sigmoid = 1.0 / (1.0 + math.exp(-k * (x_f - center)))
            new_val = validate_brightness(sigmoid * 255.0)
            
            if new_val != val:
                pixels_enhanced += 1
                enhanced_image.putpixel((x, y), new_val)
    
    return enhanced_image, pixels_enhanced

def get_pixel_stats(image, settings):
    """Get statistics about pixel values in an image."""
    grid_width = settings['grid_width']
    grid_height = settings['grid_height']
    
    pixels = []
    for y in range(grid_height):
        for x in range(grid_width):
            pixels.append(image.getpixel((x, y)))
    
    if not pixels:
        return {'min': 0, 'max': 0, 'avg': 0, 'count': 0}
    
    return {
        'min': min(pixels),
        'max': max(pixels),
        'avg': sum(pixels) / len(pixels),
        'count': len(pixels)
    }

def save_preview_image(image, path, settings, scale=10):
    """Save a preview image with correct aspect ratio."""
    grid_width = settings['grid_width']
    grid_height = settings['grid_height']
    cell_aspect_ratio = settings['cell_aspect_ratio']
    
    preview_cell_width = scale
    preview_cell_height = int(scale * cell_aspect_ratio)
    preview_image = image.resize(
        (grid_width * preview_cell_width, grid_height * preview_cell_height), 
        Image.Resampling.NEAREST
    )
    preview_image.save(path)
    return preview_image.size

def save_enhanced_preview(enhanced_frame, output_dir, filename, settings=None):
    """Save a preview image that shows the final processed result with contrast enhancement."""
    if settings is None:
        settings = {
            'grid_width': GRID_WIDTH, 
            'grid_height': GRID_HEIGHT,
            'cell_aspect_ratio': CELL_ASPECT_RATIO
        }
    
    grid_width = settings.get('grid_width', GRID_WIDTH)
    grid_height = settings.get('grid_height', GRID_HEIGHT)
    cell_aspect_ratio = settings.get('cell_aspect_ratio', CELL_ASPECT_RATIO)
    
    print(f"💫 Saving enhanced preview for {filename} with contrast settings:")
    print(f"   - Enhance contrast: {settings.get('enhance_contrast', True)}")
    print(f"   - Sigmoid K: {settings.get('sigmoid_k', 0.042)}")
    print(f"   - Sigmoid center: {settings.get('sigmoid_center', 175.0)}")
    print(f"   - Cell aspect ratio: 1:{cell_aspect_ratio}")
    
    # Scale up the enhanced frame to a reasonable preview size with correct aspect ratio
    preview_scale = 10
    preview_cell_width = preview_scale
    preview_cell_height = int(preview_scale * cell_aspect_ratio)
    preview_image = enhanced_frame.resize(
        (grid_width * preview_cell_width, grid_height * preview_cell_height), 
        Image.Resampling.NEAREST
    )
    
    # Save the enhanced preview
    base_name = os.path.splitext(filename)[0]
    preview_path = os.path.join(output_dir, f"{base_name}_final_enhanced.png")
    preview_image.save(preview_path)
    print(f"✨ Final enhanced preview saved: {preview_path}")

def generate_video(output_dir, struct_name, fps=10, settings=None):
    """Generate a video from the processed preview images."""
    try:
        # Get all main processed images (not the extra preview versions)
        preview_files = []
        for filename in os.listdir(output_dir):
            if filename.endswith('.png') and not filename.endswith('_raw.png') and not filename.endswith('_final.png'):
                preview_files.append(filename)
        
        if not preview_files:
            print("⚠️  No processed images found for video generation")
            print(f"   🔍 Searched for *.png files in {output_dir}")
            # Debug: show what files are actually there
            all_files = [f for f in os.listdir(output_dir) if f.endswith('.png')]
            print(f"   📁 Found {len(all_files)} PNG files: {all_files[:5]}..." if len(all_files) > 5 else f"   📁 Found files: {all_files}")
            return None
        
        # Sort files by frame number
        preview_files.sort(key=extract_number)
        
        if len(preview_files) < 2:
            print("⚠️  Need at least 2 frames to generate a video")
            return None
        
        # Get video dimensions from first image
        first_image_path = os.path.join(output_dir, preview_files[0])
        first_image = cv2.imread(first_image_path)
        if first_image is None:
            print(f"❌ Could not read first image: {first_image_path}")
            return None
        
        height, width, layers = first_image.shape
        
        # Create video writer - use mp4v for OpenCV compatibility, convert later if needed
        video_path = os.path.join(output_dir, f"{struct_name}_animation.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
        
        if not video_writer.isOpened():
            print("❌ Could not create video writer")
            return None
        
        print(f"🎬 Generating video with {len(preview_files)} frames at {fps} FPS...")
        
        # Add each frame to video
        for i, filename in enumerate(preview_files):
            image_path = os.path.join(output_dir, filename)
            frame = cv2.imread(image_path)
            
            if frame is not None:
                video_writer.write(frame)
                if (i + 1) % 10 == 0:  # Progress update every 10 frames
                    print(f"   📹 Added frame {i + 1}/{len(preview_files)}")
            else:
                print(f"⚠️  Could not read frame: {image_path}")
        
        # Release video writer
        video_writer.release()
        
        # Verify video was created
        if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
            print(f"✅ Video successfully generated: {video_path}")
            
            # Convert to web-compatible H.264 format if ffmpeg is available
            if shutil.which("ffmpeg"):
                temp_path = video_path + "_temp.mp4"
                web_path = video_path
                
                try:
                    # Move original to temp
                    os.rename(video_path, temp_path)
                    
                    # Convert to H.264
                    print("🔄 Converting to web-compatible H.264 format...")
                    subprocess.run([
                        "ffmpeg", "-i", temp_path, "-c:v", "libx264", 
                        "-preset", "fast", "-crf", "23", "-pix_fmt", "yuv420p", 
                        web_path, "-y"
                    ], check=True, capture_output=True, text=True)
                    
                    # Remove temp file
                    os.remove(temp_path)
                    print("✅ Video converted to web-compatible format")
                    
                except subprocess.CalledProcessError as e:
                    print(f"⚠️  H.264 conversion failed: {e.stderr}")
                    # Restore original if conversion failed
                    if os.path.exists(temp_path):
                        os.rename(temp_path, video_path)
                except Exception as e:
                    print(f"⚠️  Conversion error: {str(e)}")
                    # Restore original if conversion failed
                    if os.path.exists(temp_path):
                        os.rename(temp_path, video_path)
            else:
                print("ℹ️  ffmpeg not available - video in basic MP4 format")
            
            return video_path
        else:
            print("❌ Video generation failed")
            return None
            
    except Exception as e:
        print(f"❌ Error generating video: {str(e)}")
        return None

def process_single_image_to_grid(input_path, settings):
    """
    Process a single image into a pixelated grid.
    Returns the final processed image that matches what will be in the C struct.
    """
    try:
        original_img = Image.open(input_path)
    except FileNotFoundError:
        print(f"Error: The file '{input_path}' was not found.")
        return None
    except Exception as e:
        print(f"Error opening or processing image: {e}")
        return None

    # Extract settings
    grid_width = settings['grid_width']
    grid_height = settings['grid_height']
    cell_aspect_ratio = settings['cell_aspect_ratio']
    
    # Calculate canvas dimensions
    cell_height = int(CELL_WIDTH * cell_aspect_ratio)
    canvas_width = grid_width * CELL_WIDTH
    canvas_height = grid_height * cell_height

    # Create background and resize original image to fit
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

    # Create the initial pixelated version
    raw_pixelated = background.resize((grid_width, grid_height), Image.Resampling.LANCZOS)
    
    print(f"📊 Raw pixelated stats: {get_pixel_stats(raw_pixelated, settings)}")
    
    # Apply filtering
    filtered_image, pixels_filtered = apply_filtering(raw_pixelated, settings)
    print(f"📊 After filtering: {get_pixel_stats(filtered_image, settings)} ({pixels_filtered} pixels changed)")
    
    # Apply contrast enhancement
    final_image, pixels_enhanced = apply_contrast_enhancement(filtered_image, settings)
    print(f"📊 Final result: {get_pixel_stats(final_image, settings)} ({pixels_enhanced} pixels enhanced)")
    
    # Validate all pixel values are in valid range
    stats = get_pixel_stats(final_image, settings)
    if stats['min'] < 0 or stats['max'] > 255:
        print(f"⚠️  WARNING: Pixel values out of range! Min: {stats['min']}, Max: {stats['max']}")
    
    return {
        'raw': raw_pixelated,
        'filtered': filtered_image, 
        'final': final_image,
        'stats': {
            'pixels_filtered': pixels_filtered,
            'pixels_enhanced': pixels_enhanced
        }
    }

def process_image(input_path, output_path, return_pixelated=False, settings=None):
    """Main image processing function - now uses the refactored pipeline."""
    settings = get_processing_settings(settings)
    
    result = process_single_image_to_grid(input_path, settings)
    if not result:
        return None
    
    raw_pixelated = result['raw']
    final_image = result['final']
    
    # Save preview images
    base_name = os.path.splitext(output_path)[0]
    
    # Remove extra preview files - user doesn't want _raw.png and _final.png versions
    # Just save the main processed image
    
    # Save the full-scale final image
    cell_height = int(CELL_WIDTH * settings['cell_aspect_ratio'])
    canvas_width = settings['grid_width'] * CELL_WIDTH
    canvas_height = settings['grid_height'] * cell_height
    full_scale_final = final_image.resize((canvas_width, canvas_height), Image.Resampling.NEAREST)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    full_scale_final.save(output_path)

    return final_image if return_pixelated else None

# ===============================================
# C CODE GENERATION
# ===============================================
def validate_c_struct_data(frame_data_list, settings):
    """Validate that all pixel data is suitable for C struct generation."""
    grid_width = settings['grid_width']
    grid_height = settings['grid_height']
    total_pixels = grid_width * grid_height
    
    print(f"🔍 Validating C struct data for {len(frame_data_list)} frames...")
    
    for frame_idx, (enhanced_frame, frame_number) in enumerate(frame_data_list):
        pixels_out_of_range = 0
        active_pixels = 0
        
        for y in range(grid_height):
            for x in range(grid_width):
                brightness = enhanced_frame.getpixel((x, y))
                
                if not isinstance(brightness, int):
                    print(f"⚠️  Frame {frame_idx}: Non-integer brightness at ({x},{y}): {brightness}")
                
                if brightness < 0 or brightness > 255:
                    pixels_out_of_range += 1
                    print(f"⚠️  Frame {frame_idx}: Brightness out of range at ({x},{y}): {brightness}")
                
                if brightness > 0:
                    active_pixels += 1
        
        if pixels_out_of_range > 0:
            print(f"❌ Frame {frame_idx}: {pixels_out_of_range} pixels out of valid range!")
        
        print(f"✅ Frame {frame_idx}: {active_pixels}/{total_pixels} active pixels, all in valid range")

def generate_c_struct_array(frame_data_list, c_output_path, struct_variable_name, settings):
    """Generate C struct array with validation."""
    settings = get_processing_settings(settings)
    
    # Validate data before generating C code
    validate_c_struct_data(frame_data_list, settings)
    
    grid_width = settings['grid_width']
    grid_height = settings['grid_height']
    
    c_code = [
        '// Generated by the pixelator script.\n',
        f'// This C struct contains the processed pixel data from the main .png images.\n',
        '#include "frames_as_c_code.h"\n\n',
        f'const animation_frame {struct_variable_name}[{len(frame_data_list)}] = {{\n'
    ]

    for enhanced_frame, frame_number in frame_data_list:
        pixels = []
        for y in range(grid_height):
            for x in range(grid_width):
                brightness = enhanced_frame.getpixel((x, y))
                # Ensure brightness is valid and integer
                brightness = validate_brightness(brightness)
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
    print(f"✅ C struct array saved to '{c_output_path}'")
    print("🔗 The C struct contains the same data as the main .png images")

    # Update header file
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
def process_frames(input_dir, struct_name, custom_settings=None):
    """Processes a directory of frames, generates C code, and cleans up."""
    settings = get_processing_settings(custom_settings)
    
    frame_data_list = []
    output_animation_dir = os.path.join("output_images", struct_name)
    os.makedirs(output_animation_dir, exist_ok=True)
    
    filenames = sorted([f for f in os.listdir(input_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))], key=extract_number)
    total_files = len(filenames)
    
    if total_files > 0:
        print(f"🖼️  Processing {total_files} frames from '{os.path.basename(input_dir)}'...")
        print(f"⚙️  Settings: Grid={settings['grid_width']}x{settings['grid_height']}, "
              f"Contrast={'ON' if settings['enhance_contrast'] else 'OFF'}, "
              f"Filter={settings['filter_threshold']}/{settings['dimming_threshold']}")
        
        for i, filename in enumerate(filenames):
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_animation_dir, filename)
            
            final_pixelated = process_image(input_file, output_file, return_pixelated=True, settings=settings)
            if final_pixelated:
                frame_data_list.append((final_pixelated, i))
            
            progress = i + 1
            bar_length = 40
            percent = progress / total_files
            filled_len = int(bar_length * percent)
            bar = '█' * filled_len + '-' * (bar_length - filled_len)
            sys.stdout.write(f'\r  [{bar}] {progress}/{total_files} frames processed')
            sys.stdout.flush()
        print()

    if frame_data_list:
        c_output_path = f"frames_as_c_code/{struct_name}.c"
        generate_c_struct_array(frame_data_list, c_output_path, struct_name, settings)
        
        # Generate video from preview images
        video_fps = settings.get('video_fps', 10)  # Use video-specific FPS
        generate_video_enabled = settings.get('generate_video', True)
        
        if generate_video_enabled:
            video_path = generate_video(output_animation_dir, struct_name, video_fps, settings)
            if video_path:
                print(f"🎬 Animation video saved to: {video_path}")
            else:
                print("⚠️  Video generation failed or skipped (need multiple frames)")
        else:
            print("ℹ️  Video generation disabled in settings")
        
        print(f"\n✅ Successfully created animation '{struct_name}' with {len(frame_data_list)} frames")
        print(f"📁 C code saved to: {c_output_path}")
        print(f"🖼️  Preview images saved to: {output_animation_dir}")

# ===============================================
# WRAPPER FUNCTIONS FOR FLASK APP
# ===============================================
def process_image_and_generate_c_code(image_path, struct_name, custom_settings=None):
    """Processes a single image and generates C code for it."""
    settings = get_processing_settings(custom_settings)
    
    # Create a temporary directory to hold the single image
    temp_dir = f"temp_single_image_{struct_name}"
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Copy the image to temp directory with a standard name
        temp_image_path = os.path.join(temp_dir, "frame_00000.png")
        
        # Process the image and get the final pixelated version
        final_pixelated = process_image(image_path, temp_image_path, return_pixelated=True, settings=settings)
        
        if not final_pixelated:
            return "Error: Could not process the image."
        
        # Create frame data list with single frame
        frame_data_list = [(final_pixelated, 0)]
        
        # Generate C code with validation
        c_output_path = f"frames_as_c_code/{struct_name}.c"
        generate_c_struct_array(frame_data_list, c_output_path, struct_name, settings)
        
        # Note: Video generation skipped for single images (need multiple frames)
        print("ℹ️  Video generation skipped - single image processing")
        
        # Read and return the generated C code
        with open(c_output_path, 'r') as f:
            return f.read()
            
    except Exception as e:
        return f"Error processing image: {str(e)}"
    finally:
        # Clean up temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def process_directory_and_generate_c_code(directory_path, struct_name, custom_settings=None):
    """Processes a directory of images and generates C code."""
    settings = get_processing_settings(custom_settings)
    
    try:
        frame_data_list = []
        output_animation_dir = os.path.join("output_images", struct_name)
        os.makedirs(output_animation_dir, exist_ok=True)
        
        filenames = sorted([f for f in os.listdir(directory_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))], key=extract_number)
        
        if not filenames:
            return "Error: No image files found in directory."
        
        # Process all images
        for i, filename in enumerate(filenames):
            input_file = os.path.join(directory_path, filename)
            output_file = os.path.join(output_animation_dir, filename)
            
            final_pixelated = process_image(input_file, output_file, return_pixelated=True, settings=settings)
            if final_pixelated:
                frame_data_list.append((final_pixelated, i))
        
        if not frame_data_list:
            return "Error: Could not process any images."
        
        # Generate C code
        c_output_path = f"frames_as_c_code/{struct_name}.c"
        generate_c_struct_array(frame_data_list, c_output_path, struct_name, settings)
        
        # Generate video from preview images if we have multiple frames
        if len(frame_data_list) > 1:
            generate_video_enabled = settings.get('generate_video', True)
            if generate_video_enabled:
                video_fps = settings.get('video_fps', 10)
                video_path = generate_video(output_animation_dir, struct_name, video_fps, settings)
                if video_path:
                    print(f"🎬 Generated animation video: {os.path.basename(video_path)}")
                else:
                    print("⚠️  Video generation failed")
            else:
                print("ℹ️  Video generation disabled in settings")
        else:
            print("ℹ️  Video generation skipped - need multiple frames")
        
        # Read and return the generated C code
        with open(c_output_path, 'r') as f:
            return f.read()
            
    except Exception as e:
        return f"Error processing directory: {str(e)}"

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
        if input_path.lower().endswith('.mov'):
            converted_path = convert_mov_to_mp4(input_path)
            if converted_path:
                input_path = converted_path
            else:
                print("Aborting due to conversion failure.")
                sys.exit(1)

        fps = 10
        struct_name = None
        
        # Command-line argument parsing
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == '--fps' and i + 1 < len(sys.argv):
                try:
                    fps = int(sys.argv[i + 1])
                    i += 2
                except ValueError:
                    print(f"Error: Invalid FPS value '{sys.argv[i+1]}'. Must be an integer.")
                    sys.exit(1)
            elif sys.argv[i] == '--struct-name' and i + 1 < len(sys.argv):
                struct_name = sys.argv[i + 1]
                i += 2
            else:
                print(f"Warning: Ignoring unrecognized argument '{sys.argv[i]}'")
                i += 1
        
        if struct_name is None:
            video_name = os.path.splitext(os.path.basename(input_path))[0]
            struct_name = re.sub(r'[^a-zA-Z0-9_]', '_', video_name).lower()
        
        temp_frames_dir = f"temp_frames_{struct_name}"
        
        print(f"🎬 Processing video: {input_path}")
        print(f"📊 FPS: {fps}, Struct name: {struct_name}")
        
        slice_video_to_frames(input_path, temp_frames_dir, fps)
        
        if os.path.exists(temp_frames_dir) and os.listdir(temp_frames_dir):
            process_frames(temp_frames_dir, struct_name)
            shutil.rmtree(temp_frames_dir)
            print(f"🗑️  Cleaned up temporary frames from {temp_frames_dir}")
        else:
            print("No frames were extracted. Aborting.")
            if os.path.exists(temp_frames_dir):
                shutil.rmtree(temp_frames_dir)

    # --- Image Directory Processing Logic ---
    elif os.path.isdir(input_path):
        struct_name_input = input("Enter the name for your C struct and file: ")
        struct_name = re.sub(r'[^a-zA-Z0-9_]', '_', struct_name_input).lower()
        if not struct_name:
            print("Invalid struct name. Aborting.")
            sys.exit(1)
        process_frames(input_path, struct_name)
    else:
        print(f"Error: Input '{input_path}' is not a valid video file or directory.")