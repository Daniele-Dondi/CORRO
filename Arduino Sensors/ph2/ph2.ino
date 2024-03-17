/*
 # Based on the code written by
 # Editor : YouYou
 # Ver    : 1.0
 # Product: analog pH meter
 # SKU    : SEN0161
 # Modified by Daniele Dondi
*/
#define SensorPin A0            //pH meter Analog output to Arduino Analog Input 0
#define Sensor2Pin A1            //ORP combined electrode Analog output to Arduino Analog Input 1
#define LED 13
#define samplingInterval 20  //sampling interval in ms
#define printInterval 500  //serial writing interval in ms
#define ArrayLength  40    //the output value is an average over arraylength
int pHArray[ArrayLength];   //Store the average value of the sensor 1
int pHArray2[ArrayLength];   //Store the average value of the sensor 2
int pHArrayIndex=0;    
void setup(void)
{
  pinMode(LED,OUTPUT);  
  Serial.begin(9600);  
}
void loop(void)
{
  static unsigned long samplingTime = millis();
  static unsigned long printTime = millis();
  static float pHValue,voltage,voltage2;
  if(millis()-samplingTime > samplingInterval)
  {
      pHArrayIndex++;
      pHArray[pHArrayIndex]=analogRead(SensorPin);
      pHArray2[pHArrayIndex]=analogRead(Sensor2Pin);      
      if(pHArrayIndex>=ArrayLength)pHArrayIndex=0;
      voltage = averagearray(pHArray, ArrayLength)*5.0/1024;
      voltage2 = averagearray(pHArray2, ArrayLength)*5.0/1024;      
      samplingTime=millis();
  }
  if(millis() - printTime > printInterval)   //Every printinterval milliseconds, print voltages, toggle the state of the LED indicator
  {
        Serial.print(voltage,4);
        Serial.print("\t");        
        Serial.println(voltage2,4);        
        digitalWrite(LED,digitalRead(LED)^1);
        printTime=millis();
  }
}

double averagearray(int* arr, int number){
  int i;
  double avg;
  long amount=0;
  if(number<=0){
    Serial.println("Error! number must be a positive integer\n");
    return 0;
  }
    for(i=1;i<=number;i++)
      amount+=arr[i];
    avg = (float)amount/(number);
  
  return avg;
}
