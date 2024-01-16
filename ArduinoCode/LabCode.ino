// Includes set
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 32 // OLED display height, in pixels
#define OLED_RESET     4 // Reset pin # (or -1 if sharing Arduino reset pin)
#define LOGO_HEIGHT   16
#define LOGO_WIDTH    16

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// constants set
const int buttonPinGreen = 2;     // the number of the pushbutton pin
const int buttonPinRed = 3;     // the number of the pushbutton pin
const int ledPinRed =  9;      // the number of the LED pin
const int ledPinGreen =  8;      // the number of the LED pin
// variables will change:
int buttonStateRed = 0;         // variable for reading the pushbutton status
int buttonStateGreen = 0;         // variable for reading the pushbutton status

void setup() {
  Serial.begin(9600);
  

  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3C for 128x32
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }  
  // initialize the LED pin as an output:
  pinMode(ledPinRed, OUTPUT);
  pinMode(ledPinGreen, OUTPUT);
  // initialize the pushbutton pin as an input:
  pinMode(buttonPinGreen, INPUT);
  pinMode(buttonPinRed, INPUT);

  //LED TEST
  pinMode(LED_BUILTIN, OUTPUT);
  
  // Show initial display buffer contents on the screen --
  // the library initializes this with an Adafruit splash screen.
  display.display();
  delay(2000);            // Pause for 2 seconds
  display.clearDisplay(); // Clear the buffer
  
}
void loop() {
  // read the state of the pushbutton value:
  buttonStateRed = digitalRead(buttonPinRed);
  buttonStateGreen = digitalRead(buttonPinGreen);
  homeFunOled();

  
  if (buttonStateRed == HIGH) {
    // turn LED on:
    Serial.println("RedButton");
    waitFunOled();
    digitalWrite(ledPinRed, HIGH);
    delay(200);
    
  } else if (buttonStateGreen == HIGH) {
    // turn LED on:
    digitalWrite(ledPinGreen, HIGH);
    waitFunOled();
    Serial.println("GreenButton");
    while(!Serial.available() ){ //Esperar respuesta serial (otra opcion: //delay(2000);//esperar 2 segundos para respuesta)
    }    
    if (Serial.available()>0) {
      int val = char(Serial.read())-'0';
      if(val == 1){
        Serial.write("OPEN\n");
        digitalWrite(LED_BUILTIN, HIGH);
        openFunOled();
        delay(1000);
        digitalWrite(LED_BUILTIN, LOW);
        Serial.read(); //Para limpiar Serial
        }
       else{
        Serial.write("ERROR\n");
        tryFunOled();
        delay(1000);
        Serial.read(); //Para limpiar Serial
       }
      }        
    
    delay(200);
    
  } else {
    // turn LED off:
    digitalWrite(ledPinRed, LOW);
    digitalWrite(ledPinGreen, LOW);
  }
  // Added the delay so that we can see the output of button
  delay(100);
}

//Funcion para imprimir texto (Texto, coordinada x0, coordenada y0, tamaño, wrappe)
void textPrint(String text, int x0, int y0,int size, boolean d) {  
  display.setCursor(x0,y0);
  display.setTextColor(WHITE);
  display.setTextSize(size);  
  display.println(text);
  if(d){
    display.display();
  }
}

void waitFunOled(){
  //Oled 
  display.clearDisplay();
  textPrint("Please wait...", 4, 3, 1, false);  
  display.drawRect(1, 1, 126,31, WHITE);
  display.display();
}

void tryFunOled(){
  //Oled 
  display.clearDisplay();
  textPrint("Try Again...", 4, 3, 1, false);  
  display.drawRect(1, 1, 126,31, WHITE);
  display.display();
}

void openFunOled(){
  //Oled 
  display.clearDisplay();
  textPrint("Opening...", 4, 3, 1, false);  
  display.drawRect(1, 1, 126,31, WHITE);
  display.display();
}

void homeFunOled(){
  //Oled 
  display.clearDisplay();
  textPrint("Red button: Save", 4, 3, 1, false);  
  textPrint("Green button: Detect", 4, 11, 1, false);  
  display.drawRect(1, 1, 126,31, WHITE);
  display.display();
}
