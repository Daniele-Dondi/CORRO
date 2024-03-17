int analogPin = A0; 

long val = 0;  // variable to store the value read

void setup() {
  Serial.begin(9600);           //  setup serial
}

void loop() {
  val=0;

  for (int i = 0; i <= 60; i++) {
   val = val + analogRead(analogPin);  // read the input pin
   delay(10);
  }
  val=val/60;
  Serial.println(val);          // write value
}
