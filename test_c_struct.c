#include "frames_as_c_code.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// ============================================================================
// Animation Info Struct
// ============================================================================
typedef struct {
    const char* name;
    const animation_frame* frames;
    int num_frames;
} animation_t;

// ============================================================================
// Animation Registry
// ============================================================================
animation_t animations[] = {
    {"swirling_circle_animation", swirling_circle_animation, 26},
    {"all_icons", all_icons, 4},
    {"last_two", last_two, 2}
};
int num_animations = sizeof(animations) / sizeof(animations[0]);

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
    // Check for correct number of arguments (now accepts 2 or 3)
    if (argc < 2 || argc > 3) {
        fprintf(stderr, "Usage: %s <struct_name> [display_name]\n", argv[0]);
        fprintf(stderr, "The display_name is optional.\n");
        fprintf(stderr, "Available animations:\n");
        for (int i = 0; i < num_animations; i++) {
            fprintf(stderr, " - %s\n", animations[i].name);
        }
        return 1;
    }

    const char* struct_name = argv[1];
    // Use the struct_name as the display_name if one isn't provided.
    const char* display_name = (argc == 3) ? argv[2] : struct_name;
    const animation_frame* selected_frames = NULL;
    int selected_num_frames = 0;

    for (int i = 0; i < num_animations; i++) {
        if (strcmp(struct_name, animations[i].name) == 0) {
            selected_frames = animations[i].frames;
            selected_num_frames = animations[i].num_frames;
            break;
        }
    }

    if (selected_frames) {
        print_animation_frames(selected_frames, selected_num_frames, display_name);
    } else {
        fprintf(stderr, "Error: Unknown struct name '%s'\n", struct_name);
        return 1;
    }

    return 0;
}
#endif