#include "motorDriver.h"
#include <stdint.h>
#include "main.h"

static uint8_t currDrivePhase = -1;

static GPIO_TypeDef* motorHPinMatrix[3] = {
	GPIOA,  GPIOA,  GPIOA
};

static GPIO_TypeDef* motorLPinMatrix[3] = {
	GPIOA,  GPIOA,  GPIOA
};

static uint16_t motorHPins[3] = {
		GPIO_PIN_5, GPIO_PIN_7, GPIO_PIN_11
};

static uint16_t motorLPins[3] = {
		GPIO_PIN_6, GPIO_PIN_8, GPIO_PIN_9
};

void motorInit(){
	GPIO_InitTypeDef gpio = {0};

	// Set the initial level before switching to output mode (avoids a glitch)
	for(uint8_t pin = 0; pin < 3; pin++){
		HAL_GPIO_WritePin(motorHPinMatrix[pin], motorHPins[pin], GPIO_PIN_SET); // LED0
		HAL_GPIO_WritePin(motorLPinMatrix[pin], motorLPins[pin], GPIO_PIN_SET); // LED0
	}
    gpio.Mode  = GPIO_MODE_OUTPUT_PP;   // push-pull output
    gpio.Speed = GPIO_SPEED_FREQ_HIGH;

    for(uint8_t pin = 0; pin < 3; pin++){
		gpio.Pin = motorHPins[pin];
		HAL_GPIO_Init(motorHPinMatrix[pin], &gpio);
		HAL_GPIO_TogglePin(motorHPinMatrix[pin], gpio.Pin);

		gpio.Pin = motorLPins[pin];
		HAL_GPIO_Init(motorLPinMatrix[pin], &gpio);
		HAL_GPIO_TogglePin(motorLPinMatrix[pin], gpio.Pin);
    }
}

void incMotor(){

	switch(currDrivePhase){
	case -1:
		HAL_GPIO_TogglePin(motorHPinMatrix[2], motorHPins[2]);
		HAL_GPIO_TogglePin(motorLPinMatrix[1], motorLPins[1]);
		break;
	case 0:
		// turn off previous
		HAL_GPIO_TogglePin(motorHPinMatrix[2], motorHPins[2]);
		HAL_GPIO_TogglePin(motorLPinMatrix[1], motorLPins[1]);
		// turn on next
		HAL_GPIO_TogglePin(motorHPinMatrix[0], motorHPins[0]);
		HAL_GPIO_TogglePin(motorLPinMatrix[2], motorLPins[2]);
		break;
	case 1:
		// turn off previous
		HAL_GPIO_TogglePin(motorHPinMatrix[0], motorHPins[0]);
		HAL_GPIO_TogglePin(motorLPinMatrix[2], motorLPins[2]);
		// turn on next
		HAL_GPIO_TogglePin(motorHPinMatrix[1], motorHPins[1]);
		HAL_GPIO_TogglePin(motorLPinMatrix[0], motorLPins[0]);
		break;
	case 2:
		// turn off previous
		HAL_GPIO_TogglePin(motorHPinMatrix[1], motorHPins[1]);
		HAL_GPIO_TogglePin(motorLPinMatrix[0], motorLPins[0]);
		// turn on next
		HAL_GPIO_TogglePin(motorHPinMatrix[2], motorHPins[2]);
		HAL_GPIO_TogglePin(motorLPinMatrix[1], motorLPins[1]);
		break;
	default:

		break;

	}


	currDrivePhase++;
	if(currDrivePhase >= 3){
		currDrivePhase = 0;
	}
}
