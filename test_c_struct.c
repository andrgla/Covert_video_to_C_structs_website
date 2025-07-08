#include "animations.h"
#include <stdio.h>

// ============================================================================
// gcc -DTEST_ANIMATIONS_MAIN -Ilp5860_driver lp5860_driver/display/animations/test_animations.c lp5860_driver/display/animations/animations.c -o test_animations && ./test_animations

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

void print_loading_animation_frames(const animation_frame* frames, int num_frames) {
    printf("Testing Loading Animation Frames Display\n");
    printf("========================================\n");
    for (int i = 0; i < num_frames; i++) {
        char frame_name[50];
        snprintf(frame_name, sizeof(frame_name), "Loading Animation Frame %d", i);
        print_animation_frame(&frames[i], frame_name);
    }
}

#ifdef TEST_ANIMATIONS_MAIN
extern const animation_frame loading_animation_frames[12];
int main() {
    print_loading_animation_frames(swirling_circle_animation, 26);
    return 0;
}
#endif