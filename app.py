from flask import Flask, request, render_template, send_from_directory
import os
import shutil
import zipfile
from werkzeug.utils import secure_filename
# Import the functions from your original script
from pixelate_and_convert import slice_video_to_frames, process_image_and_generate_c_code, process_directory_and_generate_c_code

# --- Flask App Setup ---
app = Flask(__name__)
# Configure a directory to temporarily store uploaded files
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Web Page Route ---
@app.route('/')
def index():
    """
    Serves the main HTML page.
    """
    return render_template('index.html')

# --- File Upload and Processing Route ---
@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handles file uploads, processes them, and returns the C code.
    """
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    if file:
        # Securely save the uploaded file
        filename = secure_filename(file.filename)
        # Create a unique temporary directory for this request to avoid conflicts
        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], filename + "_temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        saved_path = os.path.join(temp_dir, filename)
        file.save(saved_path)

        struct_name = request.form.get('struct_name', 'my_animation')
        c_code_output = ""
        error_message = ""

        # Extract settings from form
        settings = {
            'grid_width': int(request.form.get('grid_width', 18)),
            'grid_height': int(request.form.get('grid_height', 11)),
            'enhance_contrast': request.form.get('enhance_contrast') == 'on',
            'sigmoid_k': float(request.form.get('sigmoid_k', 0.042)),
            'sigmoid_center': float(request.form.get('sigmoid_center', 175.0)),
            'filter_threshold': int(request.form.get('filter_threshold', 5)),
            'dimming_threshold': int(request.form.get('dimming_threshold', 15)),
            'fps': int(request.form.get('fps', 30)),
            'video_fps': int(request.form.get('video_fps', 10)),
            'generate_video': request.form.get('generate_video') == 'on',
            'cell_aspect_ratio': float(request.form.get('cell_aspect_ratio', 1.6))
        }
        
        # Debug output to see what settings are being used
        print(f"🔧 Processing with settings: {settings}")
        print(f"🎯 Struct name: {struct_name}")
        print(f"📁 File: {filename}")

        try:
            # --- Logic to handle different file types ---
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Process a single image
                c_code_output = process_image_and_generate_c_code(saved_path, struct_name, settings)
            
            elif filename.lower().endswith(('.mp4', '.mov')):
                # Process a video file
                temp_frames_dir = os.path.join(temp_dir, "frames")
                os.makedirs(temp_frames_dir, exist_ok=True)
                
                print(f"Slicing video: {saved_path} into {temp_frames_dir}")
                slice_video_to_frames(saved_path, temp_frames_dir, settings['fps'])
                
                # Check if frames were actually extracted
                extracted_frames = os.listdir(temp_frames_dir)
                print(f"Found {len(extracted_frames)} frames after slicing.")

                if not extracted_frames:
                    error_message = "Could not extract any frames from the video. Please check if the video file is valid or if FFmpeg is correctly installed."
                else:
                    c_code_output = process_directory_and_generate_c_code(temp_frames_dir, struct_name, settings)

            elif filename.lower().endswith('.zip'):
                # Process a zip file of images
                temp_zip_dir = os.path.join(temp_dir, "zip_contents")
                os.makedirs(temp_zip_dir, exist_ok=True)
                
                with zipfile.ZipFile(saved_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_zip_dir)
                
                # Find the directory containing the images
                image_folder = temp_zip_dir
                # If the zip contains a single folder, use that folder
                if len(os.listdir(temp_zip_dir)) == 1 and os.path.isdir(os.path.join(temp_zip_dir, os.listdir(temp_zip_dir)[0])):
                    image_folder = os.path.join(temp_zip_dir, os.listdir(temp_zip_dir)[0])

                c_code_output = process_directory_and_generate_c_code(image_folder, struct_name, settings)
            
            else:
                error_message = "Unsupported file type. Please upload a video, image, or zip file."

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
        
        finally:
            # Clean up the temporary directory
            shutil.rmtree(temp_dir)

        # --- Render the result ---
        if error_message:
            return render_template('index.html', error=error_message)
        else:
            return render_template('index.html', c_code=c_code_output, struct_name=struct_name)

# --- Favicon Route (Optional) ---
@app.route('/favicon.ico')
def favicon():
    """
    Serves the favicon to prevent 404 errors in the browser console.
    """
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# --- Video Serving Routes ---
@app.route('/videos')
def list_videos():
    """
    Lists all generated animation videos.
    """
    videos = []
    output_base = "output_images"
    
    if os.path.exists(output_base):
        for folder in os.listdir(output_base):
            folder_path = os.path.join(output_base, folder)
            if os.path.isdir(folder_path):
                for file in os.listdir(folder_path):
                    if file.endswith('.mp4') and not file.endswith('_old.mp4'):
                        videos.append({
                            'name': file,
                            'folder': folder,
                            'path': f"/video/{folder}/{file}",
                            'size': os.path.getsize(os.path.join(folder_path, file))
                        })
    
    return render_template('videos.html', videos=videos)

@app.route('/video/<folder>/<filename>')
def serve_video(folder, filename):
    """
    Serves a generated video file with proper headers for browser playback.
    """
    video_path = os.path.join("output_images", folder)
    full_video_path = os.path.join(video_path, filename)
    
    if not os.path.exists(full_video_path):
        return "Video not found", 404
    
    # Get file size for proper range requests
    file_size = os.path.getsize(full_video_path)
    
    # Handle range requests (important for video streaming)
    range_header = request.headers.get('Range', None)
    if range_header:
        byte_start, byte_end = parse_range_header(range_header, file_size)
        
        def generate():
            with open(full_video_path, 'rb') as f:
                f.seek(byte_start)
                remaining = byte_end - byte_start + 1
                while remaining:
                    chunk_size = min(8192, remaining)  # 8KB chunks
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk
        
        response = app.response_class(
            generate(),
            206,  # Partial Content
            headers={
                'Content-Range': f'bytes {byte_start}-{byte_end}/{file_size}',
                'Accept-Ranges': 'bytes',
                'Content-Length': str(byte_end - byte_start + 1),
                'Content-Type': 'video/mp4',
                'Cache-Control': 'no-cache',
            }
        )
        return response
    else:
        # Full file request
        response = send_from_directory(
            video_path, 
            filename, 
            mimetype='video/mp4',
            as_attachment=False
        )
        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['Cache-Control'] = 'no-cache'
        return response

def parse_range_header(range_header, file_size):
    """Parse the Range header and return start and end bytes."""
    range_match = range_header.replace('bytes=', '').split('-')
    byte_start = int(range_match[0]) if range_match[0] else 0
    byte_end = int(range_match[1]) if range_match[1] else file_size - 1
    return byte_start, byte_end

# --- Main execution ---
if __name__ == '__main__':
    # Runs the Flask app on a dynamically assigned free port
    app.run(debug=True, port=0)