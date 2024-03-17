

// Hx711.DOUT - pin #A1
// Hx711.SCK - pin #A0

#include "hx711.h"
#define calibration_factor -9580.00/2.2 //This value is obtained by using the SparkFun_HX711_Calibration sketch

Hx711 scale(A1, A0);

void setup() {
  scale.setScale(calibration_factor);
  Serial.begin(9600);

}

void loop() {

  Serial.print(scale.getGram(), 1);
  Serial.println(" ");


}
