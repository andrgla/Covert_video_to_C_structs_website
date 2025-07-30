# Image & Video to C Animation Converter 🎞️➡️💻
This tool helps you convert videos or images into C structs suitable for use in embedded animation projects. It pixelates images to a fixed grid, extracts brightness data, and generates C code for animation frames.

---

### ✨ Features
- **Video Slicing:** Automatically extracts frames from `.mp4` and `.mov` files at a specified FPS.
- **Pixelation & Grayscaling** Converts frames into a low-resolution grayscale format to a fixed grid (default: 18x11).
- **Smart Filtering:** Includes functions to enhance contrast and reduce dark-pixel noise.
- **Batch process** a directory of PNGs into a C array of animation frames.
- **C Code Generation:** Outputs a `.c` file with an array of `animation_frame structs`, ready to be used in your embedded project.
- **Visual Feedback:** Generates preview images of the processed frames in the `output_images` folder.

---
## 🚀 Getting Started
### Requirements
Make sure you have Python 3 installed. Then, install the necessary packages for converting a `.mov` file to a `.mp4` file using pip, it might also need you to install FFmpeg using homebrew:

```bash
pip install opencv-python Pillow
```
### File Structure
| Folder / File | Description |
| --- | --- |
| `input_videos/` | Place your source video files here. |
| `input_images/` | Place your source image folder or single image here. |
| `output_images/` | **Output:** Preview images of the processed, pixelated frames appear here. |
| `frames_as_c_code/` | **Output:** The generated `.c` files containing the animation structs. |
| `pixelate_and_convert.py` | The main Python script you will run. |
| `test_c_struct.c` | An optional C file to test and print your generated animation struct. |

## ⚙️ Usage

### 1: From video
Upload a video in the `input_videos/` folder and run the following command:
```bash
python3 pixelate_and_convert.py input_videos/<input_video_filename> --fps 30 --struct-name <struct_name>
```
Shortly after will a `.C` file with the chosen struct name appear in the `frames_as_c_code/` folder, and multiple images of the pixelated grayscale input images appear in the `output_images/` folder. 
>[!Note]
>Video processing can take a few moments to start. Please be patient after running the command!


### 1. Converting Images
Upload a video in the `input_images/`. To convert multiple images to an array of frames in one struct, thus making an animaton, it is important to **put all input images in one folder and name them in an alphabetich/numeric order.** Then run the command 

```bash
python3 pixelate_and_convert.py input_images/<folder_containing_input_pictures>
```
Then you will be asked to enter the name for your C struct and file, do so. After doing this will one C file in the `frames_as_c_code/` folder appear, and multiple images of the pixelated grayscale input images appear in the `output_images/` folder.

### 2. Testing 

**View generated C code**

To view the generated C-code in the terminal, a 

Compile: `gcc -o test_animation -I. test_c_struct.c frames_as_c_code/*.c -DTEST_ANIMATIONS_MAIN`
Run: `./test_animation <struct_name> <num_frames>`

<h2>🔧 Image Processing Tools</h2>
<p>This script uses several key functions to transform your source media into a pixelated animation. You can adjust the parameters within these functions in the <code>pixelate_and_convert.py</code> file to fine-tune the output.</p>
<br>

<table align="center">
    <thead>
        <tr>
            <th align="left" width="220px">Function</th>
            <th align="left" width="380px">Description</th>
            <th align="left" width="180px">Key Parameter</th>
            <th align="left" width="450px">Parameter Description</th>
            <th align="center" width="120px">Default Value</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan="1" style="vertical-align: top;"><h4>slice_video_to_frames()</h4></td>
            <td rowspan="1" style="vertical-align: top;">🎞️ <strong>Slices a video file</strong> into a sequence of individual image frames.</td>
            <td><code>frames_per_second</code></td>
            <td>Controls how many frames are extracted for each second of video.</td>
            <td align="center"><code>30</code></td>
        </tr>
        <tr>
            <td rowspan="3" style="vertical-align: top;"><h4>process_image()</h4></td>
            <td rowspan="3" style="vertical-align: top;">🖼️ <strong>Resizes and pixelates</strong> each frame to fit the target grid dimensions.</td>
            <td><code>grid_width</code></td>
            <td>Sets the horizontal resolution (number of pixels wide) of the output.</td>
            <td align="center"><code>18</code></td>
        </tr>
        <tr>
            <td><code>grid_height</code></td>
            <td>Sets the vertical resolution (number of pixels high) of the output.</td>
            <td align="center"><code>11</code></td>
        </tr>
        <tr>
            <td><code>cell_width</code></td>
            <td>Defines the width (in pixels) of each "cell" in the final upscaled preview image to change the porportions of the cells, thus enabling us to eg. make an almost quadratic 11x18 grid by making the proportions 2:1. The pixel height is set to a 100. </td>
            <td align="center"><code>50</code></td>
        </tr>
        <tr>
            <td rowspan="2" style="vertical-align: top;"><h4>filter_dark_pixels()</h4></td>
            <td rowspan="2" style="vertical-align: top;">⚫ <strong>Reduces noise</strong> by removing or dimming the darkest pixels that are below a certain brightness.</td>
            <td><code>threshold</code></td>
            <td>Any pixel with a brightness at or below this value will be turned off (set to 0).</td>
            <td align="center"><code>10</code></td>
        </tr>
        <tr>
            <td><code>dimming_threshold</code></td>
            <td>Pixels with brightness between <code>threshold</code> and this value will be dimmed.</td>
            <td align="center"><code>30</code></td>
        </tr>
        <tr>
            <td rowspan="2" style="vertical-align: top;"><h4>enhance_contrast_if_many_active()</h4></td>
            <td rowspan="2" style="vertical-align: top;">✨ <strong>Boosts the contrast</strong> of the image, which helps make details clearer, especially for camera footage.</td>
            <td><code>k</code></td>
            <td>Controls the steepness of the contrast curve. Higher values create stronger contrast.</td>
            <td align="center"><code>0.025</code></td>
        </tr>
        <tr>
            <td><code>center</code></td>
            <td>The midpoint of the brightness range where the contrast adjustment is centered.</td>
            <td align="center"><code>150.0</code></td>
        </tr>
    </tbody>
</table>

XOX Andrea

