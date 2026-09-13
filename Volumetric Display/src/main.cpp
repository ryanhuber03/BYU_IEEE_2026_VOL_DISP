#include <Arduino.h>
#include "pinout.h"

#define NUM_ROWS 8
#define NUM_COLS 8

const uint8_t LEDRowDriver[NUM_ROWS] = {PA_15, PC_8 , PB_12, PB_3 , PB_6 , PB_7 , PB_9 , PB_8 };
const uint8_t LEDColDriver[NUM_COLS] = {PD_0 , PD_2 , PD_8 , PD_9 , PC_7 , PB_15, PB_14, PB_13};


void setup() {
  Serial.begin(9600);
  Serial.println("Starting VolDisp");
  for(uint32_t pin = 0; pin < NUM_ROWS; pin++){
    pinMode(LEDRowDriver[pin], OUTPUT);
    digitalWrite(LEDRowDriver[pin], pin % 2);
  }
  for(uint32_t pin = 0; pin < NUM_COLS; pin++){
    pinMode(LEDColDriver[pin], OUTPUT);
    digitalWrite(LEDColDriver[pin], pin % 2);
  }
  Serial.print("Started VolDisp @ ");
  Serial.print(millis());
  Serial.println("ms");
}

void loop() {

}

