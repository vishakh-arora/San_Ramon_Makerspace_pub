#include <FastLED.h>
#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <SerialFlash.h>

// GUItool: begin automatically generated code
AudioPlaySdWav           playSdWav1;     //xy=168,374
AudioOutputI2S           i2s1;           //xy=378,375
AudioConnection          patchCord1(playSdWav1, 0, i2s1, 0);
AudioConnection          patchCord2(playSdWav1, 1, i2s1, 1);
// GUItool: end automatically generated code
AudioControlSGTL5000     sgtl5000_1;

#define SDCARD_CS_PIN    BUILTIN_SDCARD
#define SDCARD_MOSI_PIN  11  // not actually used
#define SDCARD_SCK_PIN   13  // not actually used


#define MAX_LED 60
#define MAX_DELAY 150
#define TOUCH_THRESHOLD 2500

#define RESET_PIN 29
#define HIT_PIN 30

#define DATA_PIN 7
#define CLOCK_PIN 14

#define MAX_LEVEL 6
#define MAX_MISSES 6
#define HIT_DELAY 300

int light_move_delay = MAX_DELAY;
CRGB leds[MAX_LED];
int current_led = 0;
int direction = 1;
uint8_t hue = 0;
unsigned long lastUpdate;
int level = 0;
int misses = 0;
unsigned long lastTouchTime;

void reset() {
  light_move_delay = MAX_DELAY;
  current_led = 0;
  direction = 1;
  lastUpdate = 0;
  hue = 0;
  level = 1;
  clearall(0,0,0);
  misses = 0;
}

void setup() {
  AudioMemory(8);
  sgtl5000_1.enable();
  sgtl5000_1.volume(0.5);
  SPI.setMOSI(SDCARD_MOSI_PIN);
  SPI.setSCK(SDCARD_SCK_PIN);
  if (!(SD.begin(SDCARD_CS_PIN))) {
    while (1) {
      Serial.println("Unable to access the SD card");
      delay(500);
    }
  }  
  FastLED.addLeds<APA102,DATA_PIN,CLOCK_PIN>(leds,MAX_LED);
  FastLED.setBrightness(80);
  reset();
}

void fadeall() { for(int i = 0; i < MAX_LED; i++) { leds[i].nscale8(250); } }
void clearall( byte r, byte g, byte b) { for(int i = 0; i < MAX_LED; i++) { leds[i] = CRGB(r,g,b); } }
void cylon() { 
  static uint8_t hue = 0;
  // First slide the led in one direction
  for(int i = 0; i < MAX_LED; i++) {
    // Set the i'th led to red 
    leds[i] = CHSV(hue++, 255, 255);
    // Show the leds
    FastLED.show(); 
    // now that we've shown the leds, reset the i'th led to black
    // leds[i] = CRGB::Black;
    fadeall();
    // Wait a little bit before we loop around and do it again
    delay(10);
  }

  // Now go in the other direction.  
  for(int i = (MAX_LED)-1; i >= 0; i--) {
    // Set the i'th led to red 
    leds[i] = CHSV(hue++, 255, 255);
    // Show the leds
    FastLED.show();
    // now that we've shown the leds, reset the i'th led to black
    // leds[i] = CRGB::Black;
    fadeall();
    // Wait a little bit before we loop around and do it again
    delay(10);
  }
}
void hit() {
  level++;
  playTune("LEVELUP.WAV");
  delay(2000);
  if (level == MAX_LEVEL) {
    playTune("LEVELFIN.WAV");
    for (int i=0;i<6;i++)
      cylon();
    //delay(6000);
    reset();
  }
  light_move_delay = 0.65 * light_move_delay;
}

void miss() {
  playTune("DOWN.WAV");
  misses++;
  Serial.print("misses: ");
  Serial.println(misses);
  if (misses == MAX_MISSES) {
    playTune("OVER.WAV");
    //for (int i=0;i<1;i++)
    clearall(0,0,255);
    FastLED.show();
    delay(5000);
    reset();
  }

}


void checkForHit() {
  int hitTouch = touchRead( HIT_PIN);
  Serial.println( hitTouch);
  if (hitTouch >= TOUCH_THRESHOLD && (millis() - lastTouchTime) > HIT_DELAY) {
    lastTouchTime = millis();
    if (current_led == MAX_LED/2) {
      hit();
    }
    else {
      miss();
    }
  }
}

void playTune(const char *name) {
  // if (!playSdWav1.isPlaying()) {
    playSdWav1.play(name);
  // }
}

void checkReset() {
  int resetTouch = touchRead( RESET_PIN);
  if (resetTouch > TOUCH_THRESHOLD) {
    reset();
  }
}

int getNext(int led) {
  led = led + direction;
  if (led < 0) {
    direction = 1;
    led = 0;
  }
  else if (led >= MAX_LED) {
    direction = -1;
    led = MAX_LED - 1;
  }
  return led;
}

void showLed() {
  if ((millis() - lastUpdate) > light_move_delay) {
    int prev_led = current_led;
    leds[prev_led] = CRGB::Black;
      
    current_led = getNext(prev_led);
    leds[current_led] = CHSV( hue++, 255, 255);
    FastLED.show();
      
    lastUpdate = millis();
  }
}
void loop() {
  showLed();
  checkForHit();
  checkReset();
}
