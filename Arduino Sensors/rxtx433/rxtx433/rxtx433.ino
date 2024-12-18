/*
  Example for different sending methods
  
  https://github.com/sui77/rc-switch/
  
*/

#include <RCSwitch.h>

RCSwitch mySwitch = RCSwitch();

void setup() {   //dondi

  Serial.begin(9600);
  
  // Transmitter is connected to Arduino Pin #10  
  mySwitch.enableTransmit(10);
  //mySwitch.enableReceive(0);  // Receiver on interrupt 0 => that is pin #2
  
  
}

void SendData(int code,int nbits,int protocol){
  // Optional set protocol (default is 1, will work for most outlets)
   mySwitch.setProtocol(protocol);

  // Optional set pulse length.
  // mySwitch.setPulseLength(320);
  
  // Optional set number of transmission repetitions.
   mySwitch.setRepeatTransmit(5);
   mySwitch.send(code, nbits);
   delay(300);  
}

void loop() {
  while (Serial.available() > 0) {
    String command = Serial.readString();
    command.trim();
     if (command.indexOf("SEND")==0){
      int pos=command.indexOf(" ");
      if (pos>-1)
      {
       String tmp=command.substring(pos+1);
       pos=tmp.indexOf(" ");
       if (pos>-1){
        String tmp2=tmp.substring(pos+1);
        tmp=tmp.substring(0,pos); //data
        pos=tmp2.indexOf(" ");
        if (pos>-1){
         String tmp3=tmp2.substring(pos+1);
         tmp2=tmp2.substring(0,pos);
         int code=tmp.toInt();
         int nbits=tmp2.toInt();
         int protocol=tmp3.toInt();
         if ((code==0)or(nbits==0)or(protocol==0)){
          Serial.println("Wrong data");    
         }
         else{
           mySwitch.enableTransmit(10);
           mySwitch.disableReceive();
           SendData(code,nbits,protocol);
           Serial.println("OK");    
         }
        }
       }
      }
     }
    else if (command.indexOf("LISTEN")==0){
        mySwitch.disableTransmit();
        mySwitch.enableReceive(0);  // Receiver on interrupt 0 => that is pin #2

    } 
    else{
      Serial.println("Usage: SEND data bits protocol");    
    }
    }    
  if (mySwitch.available()) {
    
    Serial.print("Received ");
    Serial.print( mySwitch.getReceivedValue() );
    Serial.print(" / ");
    Serial.print( mySwitch.getReceivedBitlength() );
    Serial.print("bit ");
    Serial.print("Protocol: ");
    Serial.println( mySwitch.getReceivedProtocol() );

    mySwitch.resetAvailable();
  }

  /* See Example: TypeA_WithDIPSwitches 
  mySwitch.switchOn("11111", "00010");
  delay(1000);
  mySwitch.switchOff("11111", "00010");
  delay(1000); */

  /* Same switch as above, but using decimal code 
  mySwitch.send(1361, 24);
  delay(1000);  
  mySwitch.send(1364, 24);
  delay(1000);  

  /* Same switch as above, but using binary code 
  mySwitch.send("000000000001010100010001");
  delay(1000);  
  mySwitch.send("000000000001010100010100");
  delay(1000);

  /* Same switch as above, but tri-state code 
  mySwitch.sendTriState("00000FFF0F0F");
  delay(1000);  
  mySwitch.sendTriState("00000FFF0FF0");
  delay(1000);*/

  delay(2000);
}
