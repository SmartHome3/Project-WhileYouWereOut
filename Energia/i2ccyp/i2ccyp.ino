#include <Wire.h>

#pragma pack(1)
typedef struct  /* Structure that holds the sensor values */
{
    unsigned char motionDetected;
    unsigned char distance;
    unsigned int SensorRawValue;
    unsigned int highThreshold;
    unsigned int lowThreshold;
    unsigned int temperature;
    unsigned int illuminance;
    unsigned int humidity;
    
}psoc_data;

psoc_data obj;


void setup()
{
  // put your setup code here, to run once:
  Wire.begin();
  Serial.begin(9600);
  Serial.println("Starting UP");
}

void loop()
{
  // put your main code here, to run repeatedly:
  unsigned char *ptr = (unsigned char*) &obj;
  Wire.requestFrom(0x08,14);
  while(Wire.available()){
    unsigned char c=Wire.read();
    *ptr = c;
    ptr++;
   //Serial.print(c+0x30);
   //Serial.print(" "); 
  }
  Serial.println();
  Serial.println("-----------------------------");
  if(obj.motionDetected>0){
    Serial.println("Motion Detected");
  }else{
    Serial.println("No Movement");
  }
  Serial.println(obj.temperature);
  Serial.println(obj.illuminance);
  delay(500);
}
