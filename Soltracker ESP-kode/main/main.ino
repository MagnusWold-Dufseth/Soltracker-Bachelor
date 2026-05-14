// main.ino

void setup() {
  Serial.begin(115200);
  setupComms();
  setupRegulation();
  setupMotors();
  setupSensor();
}

void loop() {
  receiveFromPi();
  sensorTask();
  regulationTask();
  motorsTask();
}
