#include <Arduino.h>
#include "pinout.h"
// #include "STM32TimerInterrupt.h"
#include "ImgRender.h"
#include <SoftwareSerial.h>

SoftwareSerial ftdiSerial(PC_10, PC_11);

uint8_t image[8][8];

static uint8_t currFrame = 0;

// STM32Timer rowUpdateTimer(TIM1);
#define ROW_UPDATE_TIMER_US 5000L // 5ms
// STM32Timer frameUpdateTimer(TIM1);
#define FRAME_UPDATE_TIMER_US (ROW_UPDATE_TIMER_US * 8) // 40ms

void tickImgUpdate();
void frameUpdate();


void setup() {
  Serial.begin(115200);
  ftdiSerial.begin(115200);

  Serial.println("Starting VolDisp");
  ftdiSerial.println("Starting VolDisp");
  initImgRender();
  loadImage(image[0]);
  setFrame(currFrame);
  // if (!rowUpdateTimer.attachInterruptInterval(ROW_UPDATE_TIMER_US, tickImgUpdate)) {
  //   Serial.println("Failed to set row timer");
  // }
  // if (!frameUpdateTimer.attachInterruptInterval(FRAME_UPDATE_TIMER_US, frameUpdate)) {
  //   Serial.println("Failed to set frame timer");
  // }
  Serial.print("Started VolDisp @ ");
  Serial.print(millis());
  Serial.println("ms");
}

void loop() {
  tickImg();
  Serial.println("hello 0");
  ftdiSerial.println("Going");

  delay(1000);
}

void tickImgUpdate(){
  tickImg();
}

void frameUpdate(){
  currFrame++;
  if(currFrame >= 8){
    currFrame = 0;
  }
  setFrame(currFrame);
  // TODO: Drive motor
}
