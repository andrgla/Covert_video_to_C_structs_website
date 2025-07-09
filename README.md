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

### 1. Converting Images
To convert multiple images to an array of frames in one struct, thus making an animaton, it is important to **put all input images in one folder and name them in an alphabetich/numeric order.** 

**In the script:**
- Make sure you are saving the generated C code to the correct file: `c_output_path="frames_as_c_code/[your_outputfile].c"`, 
- Give it a fit name: `struct_variable_name="[your_animation_name]"`

**In the terminal:**
- Run the command `python3 pixelate_and_convert.py [name_of_folder_containing_input_pictures]` in terminal

### 2. Testing 

**View generated frames as pixelated grayscale images**
The generated images will appear in the òutput_images` file

**View generated C code**
To view the generated C-code in the terminal, a 

Compile: `gcc -o test_animation -I. test_c_struct.c frames_as_c_code/*.c -DTEST_ANIMATIONS_MAIN`
Run: `./test_animation <struct_name>`


