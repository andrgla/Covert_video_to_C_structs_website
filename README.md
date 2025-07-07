# Convert_from_images_to_animations_in_C
## Pixelate Images and Convert to C Animation Structs

This tool helps you convert PNG images (or a sequence of images) into C structs suitable for use in embedded animation projects. It pixelates images to a fixed grid, extracts brightness data, and generates C code for animation frames.

---

### Features

- **Pixelate images** to a fixed grid (default: 18x11).
- **Batch process** a directory of PNGs into a C array of animation frames.
- **Single image** conversion supported.
- **Outputs C structs** ready for use in microcontroller or embedded projects.

---

## Usage

### 1. Convert a Single Image
To convert a single image

### 2. Convert Multiple Images
To convert multiple images to an array of frames in one struct, thus making an animaton, it is important to **put all input images in one folder and name them in an alphabetich/numeric order.** 

**In the script:**
- Make sure you are saving the generated C code to the correct file: `c_output_path="frames_as_c_code/[your_outputfile].c"`, 
- Give it a fit name: `struct_variable_name="[your_animation_name]"`

**In the terminal:**
- Run the command `python3 pixelate_and_convert.py [name_of_folder_containing_input_pictures]` in terminal
