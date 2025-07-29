# Image & Video to C Animation Converter 🎞️➡️💻
## Pixelate Images and Convert to C Animation Structs

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

Make sure you have Python 3 installed. Then, install the necessary packages for converting a `.mov` file to a `.mp4` file using pip, it might also need you to install FFmpeg using homebrew:

```bash
pip install opencv-python Pillow
```


## ⚙️ Usage

### 1: From video
Upload a video in the `input_video` folder and run the following command:
`python3 pixelate_and_convert.py input_videos/<input_video_filename> --fps 30 --struct-name <struct_name>`

Be mindful that it might take 10 seconds until it displays in the terminal that it is working, so be patient.

### 1. Converting Images
To convert multiple images to an array of frames in one struct, thus making an animaton, it is important to **put all input images in one folder and name them in an alphabetich/numeric order.** 

**In the terminal:**
- Run the command `python3 pixelate_and_convert.py <folder_containing_input_pictures>` in terminal
- Then you will be asked to enter the name for your C struct and file, do so

After doing this will one C file in the `frames_as_c_code` folder appear, and multiple images of the pixelated grayscale input images appear in the `output_images` folder

### 2. Testing 

**View generated frames as pixelated grayscale images**

The generated images will appear in the òutput_images` file

**View generated C code**

To view the generated C-code in the terminal, a 

Compile: `gcc -o test_animation -I. test_c_struct.c frames_as_c_code/*.c -DTEST_ANIMATIONS_MAIN`
Run: `./test_animation <struct_name> <num_frames>`

## Script Details
**Image processing**

`filter_dark_pixels` is an image processing function that filters out dark noise and makes a smoother gradient between the darkest level (led turned off) and the remaining darkerst active pixels. The function gets active when .num_pixels is above a certain level. 

`enhance_contrast_if_many_active` adjusts the constrast annd is default on. Good for videoes taken on phone camera. Adjust how string you want the contrast with k


XOX Andrea

