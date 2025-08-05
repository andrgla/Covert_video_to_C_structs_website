# backend/app.py

from flask import Flask, request, send_from_directory, jsonify, send_file
import os
import shutil
import zipfile
from werkzeug.utils import secure_filename
# Import the new preview function
from pixelate_and_convert import (
    slice_video_to_frames, 
    process_image_and_generate_c_code, 
    process_directory_and_generate_c_code,
    generate_live_preview
)

# --- Flask App Setup ---
# Use app.root_path to make paths relative to the backend folder
app = Flask(__name__, static_folder=None) 
UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- API Routes ---

@app.route('/api/preview', methods=['POST', 'GET'])
def preview_image():
    """
    Processes an example image with the provided settings and returns the result.
    Accepts GET for the initial load and POST for updates.
    """
    if request.method == 'POST':
        # Get settings from the JSON body of the request
        settings = request.get_json()
    else: # For the initial GET request
        settings = {}

    # Parse and validate settings from the frontend
    parsed_settings = {
        'grid_width': int(settings.get('grid_width', 18)),
        'grid_height': int(settings.get('grid_height', 11)),
        'enhance_contrast': settings.get('enhance_contrast', True),
        'sigmoid_k': float(settings.get('sigmoid_k', 0.042)),
        'sigmoid_center': float(settings.get('sigmoid_center', 175.0)),
        'filter_threshold': int(settings.get('filter_threshold', 5)),
        'dimming_threshold': int(settings.get('dimming_threshold', 15)),
        'cell_aspect_ratio': float(settings.get('cell_aspect_ratio', 1.6))
    }

    example_image_path = os.path.join(app.root_path, 'example_image.png')
    if not os.path.exists(example_image_path):
        return "Example image not found on server.", 404

    # Generate the preview image in memory
    img_io = generate_live_preview(example_image_path, parsed_settings)
    
    if img_io:
        return send_file(img_io, mimetype='image/png')
    else:
        return "Failed to generate preview.", 500


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handles file uploads, processes them, and returns the C code as JSON.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for upload'}), 400

    if file:
        filename = secure_filename(file.filename)
        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], filename + "_temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        saved_path = os.path.join(temp_dir, filename)
        file.save(saved_path)

        struct_name = request.form.get('struct_name', 'my_animation')
        c_code_output = ""
        error_message = ""
        
        settings = {
            'grid_width': int(request.form.get('grid_width', 18)),
            'grid_height': int(request.form.get('grid_height', 11)),
            'enhance_contrast': request.form.get('enhance_contrast') == 'true',
            'sigmoid_k': float(request.form.get('sigmoid_k', 0.042)),
            'sigmoid_center': float(request.form.get('sigmoid_center', 175.0)),
            'filter_threshold': int(request.form.get('filter_threshold', 5)),
            'dimming_threshold': int(request.form.get('dimming_threshold', 15)),
            'fps': int(request.form.get('fps', 30)),
            'video_fps': int(request.form.get('video_fps', 10)),
            'generate_video': request.form.get('generate_video') == 'true',
            'cell_aspect_ratio': float(request.form.get('cell_aspect_ratio', 1.6))
        }
        
        try:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                c_code_output = process_image_and_generate_c_code(saved_path, struct_name, settings)
            
            elif filename.lower().endswith(('.mp4', '.mov')):
                temp_frames_dir = os.path.join(temp_dir, "frames")
                os.makedirs(temp_frames_dir, exist_ok=True)
                slice_video_to_frames(saved_path, temp_frames_dir, settings['fps'])
                if not os.listdir(temp_frames_dir):
                    error_message = "Could not extract frames from video."
                else:
                    c_code_output = process_directory_and_generate_c_code(temp_frames_dir, struct_name, settings)

            elif filename.lower().endswith('.zip'):
                temp_zip_dir = os.path.join(temp_dir, "zip_contents")
                os.makedirs(temp_zip_dir, exist_ok=True)
                with zipfile.ZipFile(saved_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_zip_dir)
                c_code_output = process_directory_and_generate_c_code(temp_zip_dir, struct_name, settings)

            else:
                error_message = "Unsupported file type."

        except Exception as e:
            print(f"An error occurred during processing: {str(e)}")
            error_message = f"An internal error occurred: {str(e)}"
        
        finally:
            shutil.rmtree(temp_dir)

        if error_message:
            return jsonify({'error': error_message}), 500
        
        if not c_code_output or "Error:" in c_code_output:
             return jsonify({'error': c_code_output or "C-code generation failed."}), 500
        
        else:
            return jsonify({'c_code': c_code_output, 'struct_name': struct_name})

# --- (Keep the video serving routes as they are, but use app.root_path) ---
# ... from line 140 to the end of the file ...
@app.route('/api/videos')
def list_videos():
    """
    Lists all generated animation videos.
    """
    videos = []
    output_base = os.path.join(app.root_path, "output_images")
    
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
    
    return jsonify(videos)

@app.route('/video/<folder>/<filename>')
def serve_video(folder, filename):
    """
    Serves a generated video file.
    """
    video_path = os.path.join(app.root_path, "output_images", folder)
    return send_from_directory(video_path, filename)

# --- Main execution ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)