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
extern const animation_frame test1[240];
extern const animation_frame test2[240];
extern const animation_frame test3gridsize[240];

extern const animation_frame my_animation_claude[1];
extern const animation_frame my_animation_claudeee[1];
extern const animation_frame my_animation_claud[1];
extern const animation_frame video1[240];
extern const animation_frame video2[240];
extern const animation_frame video[240];
extern const animation_frame video[80];
extern const animation_frame tiktok[150];
extern const animation_frame my_animation[407];
extern const animation_frame my_animation[83];
extern const animation_frame my_animation[408];
extern const animation_frame my_animation[240];
extern const animation_frame my_animation_1[408];
extern const animation_frame my_animation[1036];
extern const animation_frame my_animation_test[83];
extern const animation_frame my_animation[28];
