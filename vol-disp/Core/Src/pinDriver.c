/*
 * pinDriver.c
 *
 *  Created on: Sep 23, 2026
 *      Author: InventorKid
 */
#include "pinDriver.h"
#include "main.h"

static GPIO_TypeDef* LEDsGPIOMatrix[16] = {
	GPIOB,  GPIOB,  GPIOB,  GPIOB,  GPIOB,  GPIOB,  GPIOC,  GPIOA,
	//GPIOA,  GPIOC,  GPIOB,  GPIOB,  GPIOB,  GPIOB,  GPIOB,  GPIOB,
	GPIOD,  GPIOD,  GPIOD,  GPIOD,  GPIOC,  GPIOB,  GPIOB,  GPIOB
};

static uint16_t LEDsGPIOMatrixPin[16] = {
		GPIO_PIN_8, GPIO_PIN_9, GPIO_PIN_7, GPIO_PIN_6, GPIO_PIN_3, GPIO_PIN_12,  GPIO_PIN_8,  GPIO_PIN_15,
		//GPIO_PIN_15, GPIO_PIN_8, GPIO_PIN_12, GPIO_PIN_3, GPIO_PIN_6, GPIO_PIN_7,  GPIO_PIN_9,  GPIO_PIN_8,
		GPIO_PIN_0,  GPIO_PIN_2, GPIO_PIN_8,  GPIO_PIN_9, GPIO_PIN_7, GPIO_PIN_15, GPIO_PIN_13, GPIO_PIN_14};

void GPIO_Outputs_Init(void)
{
    GPIO_InitTypeDef gpio = {0};

    // Enable the clocks for the three ports
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();
    __HAL_RCC_GPIOD_CLK_ENABLE();

    // Set the initial level before switching to output mode (avoids a glitch)
    for(uint8_t pin = 0; pin < 16; pin++){
    	HAL_GPIO_WritePin(LEDsGPIOMatrix[pin], LEDsGPIOMatrixPin[pin], GPIO_PIN_SET); // LED0
    }

    gpio.Mode  = GPIO_MODE_OUTPUT_PP;   // push-pull output
    gpio.Pull  = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;

    for(uint8_t pin = 0; pin < 16; pin++){
		gpio.Pin = LEDsGPIOMatrixPin[pin]; // LED0
		HAL_GPIO_Init(LEDsGPIOMatrix[pin], &gpio);
		HAL_GPIO_TogglePin(LEDsGPIOMatrix[pin], gpio.Pin);
    }
}

// globals for storing LED line states
static bool LEDsOn[16];

void setLEDState (int pinNumber, bool on) {
	if(on != LEDsOn[pinNumber]){
		HAL_GPIO_TogglePin(LEDsGPIOMatrix[pinNumber], LEDsGPIOMatrixPin[pinNumber]);
		LEDsOn[pinNumber] = on;
	}
}
