#include "frames_as_c_code.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// ============================================================================
// Print a single animation frame to the console
// ============================================================================
void print_animation_frame(const animation_frame* frame, const char* frame_name) {
    printf("\n=== %s (11x18 LED Matrix) ===\n", frame_name);
    printf("Frame Index: %d\n", frame->frame_number);
    printf("Legend: ' '=OFF, '.'=dim, 'o'=med, 'O'=bright, '@'=brightest\n\n");

    // Print column headers
    printf("    ");
    for (int col = 0; col < ANIMATION_MATRIX_WIDTH; col++) {
        printf("%2d ", col);
    }
    printf("\n");

    // Print the matrix
    for (int row = 0; row < ANIMATION_MATRIX_HEIGHT; row++) {
        printf("%2d: ", row);
        for (int col = 0; col < ANIMATION_MATRIX_WIDTH; col++) {
            int index = (row * ANIMATION_MATRIX_WIDTH) + col;
            uint8_t brightness = frame->brightness_levels[index];

            char symbol;
            if (brightness == 0) {
                symbol = ' ';  // OFF
            } else if (brightness <= 63) {
                symbol = '.';  // Very dim (1–63)
            } else if (brightness <= 127) {
                symbol = 'o';  // Dim (64–127)
            } else if (brightness <= 191) {
                symbol = 'O';  // Medium (128–191)
            } else {
                symbol = '@';  // Brightest (192–255)
            }

            printf(" %c ", symbol);
        }
        printf("\n");
    }

    printf("\n=== End of %s ===\n\n", frame_name);
}

// ============================================================================
// Print all frames of a given animation
// ============================================================================
void print_animation_frames(const animation_frame* frames, int num_frames, const char* animation_name) {
    printf("Testing %s Animation Frames Display\n", animation_name);
    printf("========================================\n");
    for (int i = 0; i < num_frames; i++) {
        char frame_name[50];
        snprintf(frame_name, sizeof(frame_name), "%s Frame %d", animation_name, i);
        print_animation_frame(&frames[i], frame_name);
    }
}

// ============================================================================
// Main function to select and test animations
// ============================================================================

#ifdef TEST_ANIMATIONS_MAIN
int main(int argc, char *argv[]) {
    if (argc != 4) {
        fprintf(stderr, "Usage: %s <struct_name> <num_frames> <display_name>\n", argv[0]);
        fprintf(stderr, "Example: %s swirling_circle_animation 26 \"Swirling Circle\"\n", argv[0]);
        return 1;
    }

    // User provides the struct name as a symbol, so we need to use macros to resolve it.
    // This requires the user to type the actual C symbol name, e.g. swirling_circle_animation

    // Parse arguments
    const char* struct_name = argv[1];
    int num_frames = atoi(argv[2]);
    const char* display_name = argv[3];

    // Use a macro to convert the struct name string to a symbol
    // This is a hack: we require the user to type the actual symbol name, and use ifdefs to resolve it
    // (Alternatively, you could use a script to generate a lookup table, but this is the simplest way.)

    // clang/gcc extension: statement expressions, or use a macro
    // We'll use a series of if/else to match the symbol name to the actual symbol

    if (strcmp(struct_name, "all_icons") == 0) {
        print_animation_frames(all_icons, num_frames, display_name);
    } else {
        fprintf(stderr, "Error: Unknown struct name '%s'\n", struct_name);
        return 1;
    }

    return 0;
}
#endif