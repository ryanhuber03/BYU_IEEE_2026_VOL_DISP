/*
 * pinDriver.h
 *
 *  Created on: Sep 23, 2026
 *      Author: InventorKid
 */

#ifndef PIN_DRIVER_H
#define PIN_DRIVER_H
#include <stdbool.h>


void GPIO_Outputs_Init(void);

void setLEDState(int pinNumber, bool on);
#endif
