/**
 * Marlin 3D Printer Firmware
 * Copyright (c) 2020 MarlinFirmware [https://github.com/MarlinFirmware/Marlin]
 *
 * Based on Sprinter and grbl.
 * Copyright (c) 2011 Camiel Gubbels / Erik van der Zalm
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 */

/**
 * module/servo.cpp
 */

#include "../inc/MarlinConfig.h"

#if HAS_SERVOS

#include "servo.h"

HAL_SERVO_LIB servo[NUM_SERVOS];

TERN_(EDITABLE_SERVO_ANGLES, uint16_t servo_angles[NUM_SERVOS][2]);

void servo_init() {
  #if NUM_SERVOS >= 1 && HAS_SERVO_0
    servo[0].attach(SERVO0_PIN);
    servo[0].detach(); // Just set up the pin. We don't have a position yet. Don't move to a random position.
  #endif
  #if NUM_SERVOS >= 2 && HAS_SERVO_1
    servo[1].attach(SERVO1_PIN);
    servo[1].detach();
  #endif
  #if NUM_SERVOS >= 3 && HAS_SERVO_2
    servo[2].attach(SERVO2_PIN);
    servo[2].detach();
  #endif
  #if NUM_SERVOS >= 4 && HAS_SERVO_3
    servo[3].attach(SERVO3_PIN);
    servo[3].detach();
  #endif
  #if NUM_SERVOS >= 5 && HAS_SERVO_4  //Dondi here and below
    servo[4].attach(SERVO4_PIN);
    servo[4].detach();
  #endif  
  #if NUM_SERVOS >= 6 && HAS_SERVO_5
    servo[5].attach(SERVO5_PIN);
    servo[5].detach();
  #endif    
  #if NUM_SERVOS >= 7 && HAS_SERVO_6
    servo[6].attach(SERVO6_PIN);
    servo[6].detach();
  #endif     
  #if NUM_SERVOS >= 8 && HAS_SERVO_7
    servo[7].attach(SERVO7_PIN);
    servo[7].detach();
  #endif     
  #if NUM_SERVOS >= 9 && HAS_SERVO_8
    servo[8].attach(SERVO8_PIN);
    servo[8].detach();
  #endif     
  #if NUM_SERVOS >= 10 && HAS_SERVO_9
    servo[9].attach(SERVO9_PIN);
    servo[9].detach();
  #endif       
  #if NUM_SERVOS >= 11 && HAS_SERVO_10
    servo[10].attach(SERVO10_PIN);
    servo[10].detach();
  #endif    
  #if NUM_SERVOS >= 12 && HAS_SERVO_11
    servo[11].attach(SERVO11_PIN);
    servo[11].detach();
  #endif    
  
   //Dondi here and above
}

#endif // HAS_SERVOS
