// Advanced Microcontroller-based Audio Workshop
//
// http://www.pjrc.com/store/audio_tutorial_kit.html
// https://hackaday.io/project/8292-microcontroller-audio-workshop-had-supercon-2015
// 
// Part 3-1: Peak Detection


///////////////////////////////////
// copy the Design Tool code here
///////////////////////////////////
#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <SerialFlash.h>
//#include <Adafruit_DotStar.h>
#include "FastLED.h"

#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <SerialFlash.h>
//


#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <SerialFlash.h>

//// GUItool: begin automatically generated code
//AudioPlaySdWav           playSdWav1;     //xy=1538.75,3058
//AudioAnalyzePeak         peak2;          //xy=1676.75,3189
//AudioOutputI2S           i2s1;           //xy=1700.75,2991
//AudioAnalyzePeak         peak1;          //xy=1723.75,3079
//AudioConnection          patchCord1(playSdWav1, 0, peak1, 0);
//AudioConnection          patchCord2(playSdWav1, 0, i2s1, 0);
//AudioConnection          patchCord3(playSdWav1, 1, peak2, 0);
//AudioConnection          patchCord4(playSdWav1, 1, i2s1, 1);
//AudioControlSGTL5000     sgtl5000_1;     //xy=1764.75,3282
//// GUItool: end automatically generated code

#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <SerialFlash.h>

#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <SerialFlash.h>

// GUItool: begin automatically generated code
AudioPlaySdWav           playSdWav1;     //xy=69,584
AudioEffectDelay         delay2;         //xy=350.5,769
AudioEffectDelay         delay1;         //xy=378.5,458
AudioMixer4              mixer2;         //xy=507.5,426
AudioMixer4              mixer3;         //xy=512.5,493
AudioMixer4              mixer5;         //xy=548.5,839
AudioMixer4              mixer4;         //xy=563.5,760
AudioMixer4              mixer6;         //xy=686.5,631
AudioMixer4              mixer1;         //xy=690.5,556
AudioAnalyzePeak         peak2;          //xy=806.25,668.25
AudioAnalyzePeak         peak1;          //xy=826.25,515.25
AudioOutputI2SQuad       i2s_quad1;      //xy=864.5,584
AudioConnection          patchCord1(playSdWav1, 0, delay1, 0);
AudioConnection          patchCord2(playSdWav1, 0, mixer1, 3);
AudioConnection          patchCord3(playSdWav1, 1, delay2, 0);
AudioConnection          patchCord4(playSdWav1, 1, mixer6, 0);
AudioConnection          patchCord5(delay2, 0, mixer4, 0);
AudioConnection          patchCord6(delay2, 1, mixer4, 1);
AudioConnection          patchCord7(delay2, 2, mixer4, 2);
AudioConnection          patchCord8(delay2, 3, mixer4, 3);
AudioConnection          patchCord9(delay2, 4, mixer5, 0);
AudioConnection          patchCord10(delay2, 5, mixer5, 1);
AudioConnection          patchCord11(delay2, 6, mixer5, 2);
AudioConnection          patchCord12(delay2, 7, mixer5, 3);
AudioConnection          patchCord13(delay1, 0, mixer2, 0);
AudioConnection          patchCord14(delay1, 1, mixer2, 1);
AudioConnection          patchCord15(delay1, 2, mixer2, 2);
AudioConnection          patchCord16(delay1, 3, mixer2, 3);
AudioConnection          patchCord17(delay1, 4, mixer3, 0);
AudioConnection          patchCord18(delay1, 5, mixer3, 1);
AudioConnection          patchCord19(delay1, 6, mixer3, 2);
AudioConnection          patchCord20(delay1, 7, mixer3, 3);
AudioConnection          patchCord21(mixer2, 0, mixer1, 1);
AudioConnection          patchCord22(mixer3, 0, mixer1, 2);
AudioConnection          patchCord23(mixer5, 0, mixer6, 2);
AudioConnection          patchCord24(mixer4, 0, mixer6, 1);
AudioConnection          patchCord25(mixer6, 0, i2s_quad1, 2);
AudioConnection          patchCord26(mixer6, 0, i2s_quad1, 3);
AudioConnection          patchCord27(mixer6, peak2);
AudioConnection          patchCord28(mixer1, 0, i2s_quad1, 0);
AudioConnection          patchCord29(mixer1, 0, i2s_quad1, 1);
AudioConnection          patchCord30(mixer1, peak1);
AudioControlSGTL5000     sgtl5000_1;     //xy=775.5,774
// GUItool: end automatically generated code

#define TOUCH_LIMIT 2000
float vol = 0.3;
const char* const songs[] = { "GODSPLAN.WAV", "NICE.WAV", "MINE.WAV", "DREAMS.WAV", "SATURDAY.WAV","BETTER.WAV","SICKO.WAV","WASTED.WAV"};
int num_songs = sizeof(songs) / sizeof(songs[0]);
int current_song;
int cap_delay = 100;
//#define NUMPIXELS 60 // Number of LEDs in strip
//Adafruit_DotStar strip = Adafruit_DotStar(NUMPIXELS, DOTSTAR_RGB);

// Use these with the Teensy SD Card
#define SDCARD_CS_PIN    BUILTIN_SDCARD
#define SDCARD_MOSI_PIN  11
#define SDCARD_SCK_PIN   13

// Because conditional #includes don't work w/Arduino sketches...
// #include <SPI.h>         // COMMENT OUT THIS LINE FOR GEMMA OR TRINKET
//#include <avr/power.h> // ENABLE THIS LINE FOR GEMMA OR TRINKET
#define MAX_LED  60
// Define the array of leds
CRGB leds[MAX_LED];

// Here's how to control the LEDs from any two pins:
#define DATA_PIN    7
#define CLOCK_PIN   14

void setupLed() {
  LEDS.addLeds<APA102,DATA_PIN,CLOCK_PIN,RGB>(leds,MAX_LED);
  LEDS.setBrightness(5);
  for (int i = 0; i < MAX_LED; i++)
    leds[i] = CHSV(0,0,0);
  FastLED.show();
}

void setup() {
  delay(1000);
  // Serial.begin(9600);
  AudioMemory(8);
  sgtl5000_1.enable();
  sgtl5000_1.volume(vol);
  SPI.setMOSI(SDCARD_MOSI_PIN);
  SPI.setSCK(SDCARD_SCK_PIN);
  if (!(SD.begin(SDCARD_CS_PIN))) {
    while (1) {
      Serial.println("Unable to access the SD card");
      delay(500);
    }
  }


  mixer3.gain(0, 0.4);
  mixer3.gain(1, 0.4);
  mixer3.gain(2, 0.4);
  mixer3.gain(3, 0.4);
  mixer2.gain(0, 0.4);
  mixer2.gain(1, 0.4);
  mixer2.gain(2, 0.4);
  mixer2.gain(3, 0.4);
  mixer1.gain(0, 0.0); // default = do not listen to direct signal
  mixer1.gain(1, 1); // ch1 is output of mixer1
  mixer1.gain(2, 1); // ch2 is output of mixer2
  
  delay(1000); 
  setupLed();
  randomSeed(analogRead(0)); 
}

elapsedMillis msecs;

void rightForward(int startPos, int endPos) {
  static uint8_t hue = 0;
  for(int i = startPos; i >= endPos; i--) {
    // Set the i'th led to red 
    leds[i] = CHSV(hue++, 255, 255);
    // Show the leds
    FastLED.show();
    // Wait a little bit before we loop around and do it again
    delay(5);
  }
}

void leftForward(int startPos, int endPos) {
    static uint8_t hue = 0;
    for(int i = startPos; i < endPos; i++) {
      // Set the i'th led to red 
      leds[i] = CHSV(hue++, 255, 255);
      // Show the leds
      FastLED.show();
      // Wait a little bit before we loop around and do it again
      delay(5);
    }
}

void leftBack(int startPos, int endPos) {
  static uint8_t hue = 0;
  // Now go in the other direction.  
  for(int i = startPos; i >= endPos; i--) {
    // Set the i'th led to red 
    leds[i] = CHSV(hue++, 255, 255);
    // Show the leds
    FastLED.show();
    // now that we've shown the leds, reset the i'th led to black
    leds[i] = CRGB::Black;
    // fadeall();
    // Wait a little bit before we loop around and do it again
    delay(5);
  }
}

void rightBack(int startPos, int endPos) {
  static uint8_t hue = 0;
  // Now go in the other direction.  
  for(int i = startPos; i <= endPos; i++) {
    // Set the i'th led to red 
    leds[i] = CHSV(hue++, 255, 255);
    // Show the leds
    FastLED.show();
    // now that we've shown the leds, reset the i'th led to black
    leds[i] = CRGB::Black;
    // fadeall();
    // Wait a little bit before we loop around and do it again
    delay(5);
  }
}

void lights(float leftNumber) { 
  static uint8_t hue = 0;
  int led_brightness = 100;//((1-leftNumber)*90)+5;
  //Serial.print("x");
  // First slide the led in one direction
  LEDS.setBrightness(led_brightness);
  
  int mid = MAX_LED/2;
  int numLed = (leftNumber * mid)*(0.95);
  int right_mid = mid -1;
  leftForward( mid, mid+numLed);
  rightForward(right_mid, right_mid-numLed);
  leftBack(mid+numLed-1,mid);
  rightBack( right_mid-numLed, right_mid);
}


void printSerial(float leftPeak) {//, float rightPeak) {
     int count=0;
      for (count=0; count < MAX_LED-leftPeak; count++) {
        Serial.print(" ");
      }
      
      while (count++ < MAX_LED) {
        Serial.print("<");
        
      }
//      Serial.print("||");
//      for (count=0; count < rightPeak; count++) {
//        Serial.print(">");
//      }
//      while (count++ < MAX_LED) {
//        Serial.print(" ");
//      }
      Serial.print(leftPeak);
//      Serial.print(", ");
//      Serial.print(rightPeak);
      Serial.println();
}
float MAX_VOLUME = 0.6;
float INC_VOLUME = 0.05;
void checkVolume() {
    int read_vol_up = touchRead(30);     
    int read_vol_down = touchRead(29);    
    if ( read_vol_up > TOUCH_LIMIT && vol+INC_VOLUME <= MAX_VOLUME) {
        vol = vol + INC_VOLUME;
        Serial.print("volume = ");
        Serial.println(vol);
        sgtl5000_1.volume(vol);
    }
    else if (read_vol_down > TOUCH_LIMIT && vol-INC_VOLUME >= 0){
        vol = vol - INC_VOLUME;
        sgtl5000_1.volume(vol);
        Serial.print("volume = ");
        Serial.println(vol);
    }
}

void checkPeak() {
    if (peak1.available()) { // && peak2.available()) {
      msecs = 0;
      float leftNumber = peak1.read();
      lights(leftNumber);
    //  printSerial(leftNumber);
//      float rightNumber = peak2.read();
//      lights_right(rightNumber);
//       printSerial(leftPeak, rightPeak);
    }
}

void play_song() {

  if (playSdWav1.isPlaying() == false) {
    int next_song;
      do {
        next_song = (current_song + 1) % num_songs;
        // random(0, num_songs);
        }
      while (current_song == next_song);
      
    current_song = next_song;
    playSdWav1.play(songs[current_song]);
    Serial.print("Now playing ");
    Serial.println(songs[current_song]);
    delay(10); // wait for library to parse WAV info
  }
}

void change_song() {
    if (playSdWav1.isPlaying() == true && touchRead(0) > TOUCH_LIMIT) {
        playSdWav1.stop();
        delay(1000);
        play_song();
    }
}

void add_delay() {
 int delay_up = touchRead(30);
 int delay_down = touchRead(29);
 if ( delay_up > TOUCH_LIMIT || delay_down > TOUCH_LIMIT) {
   if (playSdWav1.isPlaying() == true && delay_up > TOUCH_LIMIT && cap_delay + 50 <= 400) {
      Serial.println(delay_up);
      cap_delay = cap_delay + 50;
      Serial.print("added delay = ");
      Serial.println(cap_delay);
      
    }
    else if (playSdWav1.isPlaying() == true && delay_down > TOUCH_LIMIT && cap_delay - 50 >= 0) {
      Serial.println(delay_down);
      cap_delay = cap_delay - 50;
      Serial.print("removed delay = ");
      Serial.println(cap_delay);
      
    }
    delay1.delay(0, cap_delay);
    delay1.delay(1, cap_delay);
    delay1.delay(2, cap_delay);
    delay1.delay(3, cap_delay);
    delay1.delay(4, cap_delay);
    delay1.delay(5, cap_delay);
    delay1.delay(6, cap_delay);
    delay1.delay(7, cap_delay);
    
    delay2.delay(0, cap_delay);
    delay2.delay(1, cap_delay);
    delay2.delay(2, cap_delay);
    delay2.delay(3, cap_delay);
    delay2.delay(4, cap_delay);
    delay2.delay(5, cap_delay);
    delay2.delay(6, cap_delay);
    delay2.delay(7, cap_delay);
    delay(500);
    }
}
  
void loop() {
  play_song();
  change_song();
 // add_delay();
  
  if (msecs > 20) {
    checkPeak();
  }
  checkVolume();
}
