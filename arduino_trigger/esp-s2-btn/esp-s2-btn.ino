#include <WiFi.h>
#include <WiFiUdp.h>

const char* ssid = " "; # replace with the SSID created on RPi
const char* password = " "; # replace with the password created
WiFiUDP Udp;

const int BUTTON_PIN = 4;

void setup()
{
  // Initilize hardware:
  Serial.begin(9600);
  WiFi.begin(ssid, password);
    while(WiFi.status() != WL_CONNECTED){
      delay(500);
      Serial.print(".");
    }
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  Serial.print("Press button 0 to connect to ");
}

void loop()
{
  delay(10);
  Udp.beginPacket("10.6.6.1", 8888);
  if (digitalRead(BUTTON_PIN) == LOW)
  { // Check if button has been pressed
    while (digitalRead(BUTTON_PIN) == LOW)
      ; // Wait for button to be released
      Serial.print("button pressed");
      Udp.print("button pressed");
      Udp.endPacket();
  }
  delay(5000);
}
