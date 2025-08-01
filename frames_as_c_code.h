#ifndef FRAMES_AS_C_CODE_H
#define FRAMES_AS_C_CODE_H

#include <stdint.h>

// ============================================================================
// Animation Struct and Constants
// ============================================================================

#define ANIMATION_MAX_ACTIVE_PIXELS (18 * 11)
#define ANIMATION_MATRIX_WIDTH 18
#define ANIMATION_MATRIX_HEIGHT 11

// Macro to convert 2D coordinates to a 1D array index.
#define ANIMATION_PIXEL_INDEX(y, x) ((y) * ANIMATION_MATRIX_WIDTH + (x))

// The struct definition for a single animation frame.
typedef struct {
    uint8_t brightness_levels[ANIMATION_MAX_ACTIVE_PIXELS];
    uint8_t frame_number; // Index of this frame in an animation
    uint8_t num_pixels;
} animation_frame;

// ============================================================================
// Extern Declarations for Animation Data
// ============================================================================

// Declaration for the animation data, allowing it to be accessed from other files.

#endif // FRAMES_AS_C_CODE_H

extern const animation_frame scary_man[240];
