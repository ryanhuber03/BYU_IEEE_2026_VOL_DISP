#ifndef IMG_RENDER_H
#define IMG_RENDER_H
#include <stdint.h>

/*
Loads an image into the current draw buffer
@param imgBuf the image buffer, 8 frames each frame being 8 bytes long
@returns nothing
*/
void loadImage(uint8_t* imgBuf);

// Initializes the renderer
void initImgRender();

// sets the current frame
void setFrame(uint8_t frame);

// renders a row
void tickImg();

#endif