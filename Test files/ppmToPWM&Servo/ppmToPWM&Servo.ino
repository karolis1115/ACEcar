#include <PPMReader.h>
#include <Servo.h>

Servo steer;


int motorPWM = 11;
int INA = 13;
int INB = 12;


byte interruptPin = 3;
byte channelAmount = 6;

PPMReader ppm(interruptPin, channelAmount);

void setup() {

  steer.attach(10);
  pinMode(INA,OUTPUT);
  pinMode(INB,OUTPUT);
  pinMode(motorPWM,OUTPUT);
}

void loop() {

  int motorvalue = ppm.latestValidChannelValue(2, 1500);
  int servovalue = ppm.latestValidChannelValue(4, 1500);
  int motorForward = map(motorvalue,1500,2000,0,255);
  int motorBackward =  map(motorvalue,1500,1000,0,255);
  int servoconverted = map(servovalue,1000,2000,0,180);

  if(motorvalue > 1500){
    digitalWrite(INA,HIGH);
    digitalWrite(INB,LOW);
    analogWrite(motorPWM,motorForward);
  }

  if(motorvalue < 1500){
    digitalWrite(INA,LOW);
    digitalWrite(INB,HIGH);
    analogWrite(motorPWM,motorBackward);
  }
  steer.write(servoconverted);
}