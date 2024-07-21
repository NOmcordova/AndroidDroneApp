#include <Servo.h>
#define pingPin 7
#define echoPin 8

int first = 0;
int exist = 0;
int back = 0;
Servo servo;

void setup()
{
  Serial.begin(9600);
  pinMode(pingPin,OUTPUT);
  pinMode(echoPin,INPUT);
  servo.attach(6);
  servo.write(0);
}
void loop()
{
  if(first == 0)
  {
    delay(40000);
    first = 1;
  }
  //pulse
  digitalWrite(pingPin,LOW);
  delay(2);
  digitalWrite(pingPin,HIGH);
  delay(100);
  digitalWrite(pingPin,LOW);
  //measuring time
  long time = pulseIn(echoPin,HIGH);
  //calculating the direction
  long cm = MicroSecondsToCentimeters(time);
  Serial.println(cm);
  if(cm > 130)
  {
    exist = 1;
  }
  if(exist == 1 && cm<110 && back<110)
  {
    servo.write(360);
    delay(1000);
    servo.write(0);
  }
  back = cm;
  delay(500);
}

long MicroSecondsToCentimeters(long time)
{
  return time/29/2;
}