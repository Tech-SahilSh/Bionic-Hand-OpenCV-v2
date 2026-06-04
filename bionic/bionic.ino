#include <ESP32Servo.h>  // Use ESP32Servo instead of Servo.h

#define NUM_SERVOS 5

Servo thumbServo;
Servo indexServo;
Servo middleServo;
Servo ringServo;
Servo pinkyServo;

// ESP32 pins for servos
const int THUMB_PIN = 13;
const int INDEX_PIN = 12;
const int MIDDLE_PIN = 14;
const int RING_PIN = 27;
const int PINKY_PIN = 26;

// Servo positions
const int THUMB_CLOSE_POS = 0;
const int INDEX_CLOSE_POS = 160;
const int MIDDLE_CLOSE_POS = 160;
const int RING_CLOSE_POS = 0;
const int PINKY_CLOSE_POS = 0;

const int THUMB_OPEN_POS = 90;
const int INDEX_OPEN_POS = 0;
const int MIDDLE_OPEN_POS = 0;
const int RING_OPEN_POS = 170;
const int PINKY_OPEN_POS = 170;

void setup() {
  Serial.begin(9600);
  Serial.println("ESP32 Ready! Waiting for finger commands...");

  // Attach servos
  thumbServo.attach(THUMB_PIN);
  indexServo.attach(INDEX_PIN);
  middleServo.attach(MIDDLE_PIN);
  ringServo.attach(RING_PIN);
  pinkyServo.attach(PINKY_PIN);

  // Initialize hand (all fingers open)
  setIndividualFingerPositions(0b11111);
}

void loop() {
  if (Serial.available() > 0) {
    byte fingerStates = Serial.read();
    Serial.print("Received finger states (byte): ");
    Serial.println(fingerStates, BIN);

    setIndividualFingerPositions(fingerStates);
  }
}

void setIndividualFingerPositions(byte states) {
  thumbServo.write((states & (1 << 0)) ? THUMB_OPEN_POS : THUMB_CLOSE_POS);
  indexServo.write((states & (1 << 1)) ? INDEX_OPEN_POS : INDEX_CLOSE_POS);
  middleServo.write((states & (1 << 2)) ? MIDDLE_OPEN_POS : MIDDLE_CLOSE_POS);
  ringServo.write((states & (1 << 3)) ? RING_OPEN_POS : RING_CLOSE_POS);
  pinkyServo.write((states & (1 << 4)) ? PINKY_OPEN_POS : PINKY_CLOSE_POS);

  delay(15);
}
