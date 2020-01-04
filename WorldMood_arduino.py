#include <Adafruit_NeoPixel.h>

int i;
char payload[100];
String message, numberStr;
int n[4];
char c;
bool check = false;

int pixelPin = 7;
int numPix = 19;

int prevComma, nowComma;

Adafruit_NeoPixel pixels = Adafruit_NeoPixel(numPix, pixelPin, NEO_GRB + NEO_KHZ800);


void setup() {

  Serial.begin(9600);
  pixels.begin();

}

void loop() {

  // Ricezione payload da python

  i = 0;
  check = false;

  while (1) {
    if (Serial.available()) {

      c = Serial.read();
      payload[i] = c;
      i++;

      if (c == '&') {
        check = true;
        payload[i] = '\0';
        message = String(payload);
        //Serial.println(message);
        break;
      }
    }
  }

  // Decodifica stringa
  if (check) {

    prevComma = message.indexOf(',');
    numberStr = message.substring(0, prevComma);
    n[0] = numberStr.toInt();
    Serial.println(n[0]);

    i = 0;

    while (1) {
      i++;
      nowComma = message.indexOf(',', prevComma + 1);
      numberStr = message.substring(prevComma + 1, nowComma);
      if (numberStr == "&") {
        break;
      }
      n[i] = numberStr.toInt();
      Serial.println(n[i]);
      prevComma = nowComma;
    }
  }

  // Aggiornamento neopixel
  if (check) {

    
    pixels.setPixelColor(n[3], pixels.Color(n[0], n[1], n[2])); 
    pixels.show();

  }

}
