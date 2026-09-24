/*
 * pinRenderer.c
 *
 *  Created on: Sep 23, 2026
 *      Author: InventorKid
 */


#include "pinDriver.h"
#include "pinRenderer.h"
#include <stdint.h>
#include <stdbool.h>

#define NUM_ROWS 8
#define NUM_COLS 8

const uint8_t LEDColDriver[NUM_ROWS] = {0, 1 , 2, 3 , 4 , 5 , 6 , 7 };
const uint8_t LEDRowDriver[NUM_COLS] = {8 , 9 , 10 , 11 , 12 , 13, 14, 15};

static uint8_t* imgBuffer = 0x0;
static volatile uint8_t currFrame = 0;
static uint8_t row = 0;

void loadImage(uint8_t* imgBuf){
    imgBuffer = imgBuf;
}

void initImgRender(){
    tickImg();
}

void setFrame(uint8_t frame){
	currFrame = frame;
    row = 0;
}

void tickImg(){
	static uint8_t lastRow = 0;

	setLEDState(LEDRowDriver[lastRow], 0);
    for(uint32_t pin = 0; pin < NUM_COLS; pin++){
    	if(imgBuffer == 0x0){
    		setLEDState(LEDColDriver[pin], (pin + row) % 2);
    	} else {
    		setLEDState(LEDColDriver[pin], (imgBuffer[row + currFrame * NUM_ROWS] >> pin) & 0x01);
    	}
    }
	setLEDState(LEDRowDriver[row], 1);

    lastRow = row;
    row += 1;
    if(row >= NUM_ROWS){
        row = 0;
    }
}

void incFrame() {
	currFrame ++;
	if (currFrame >= 8) {
		currFrame = 0;
	}
}
