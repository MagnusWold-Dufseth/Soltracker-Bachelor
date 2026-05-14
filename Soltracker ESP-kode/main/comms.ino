// comms.ino

float dev_az = 0.0;
float dev_alt = 0.0;
bool current_state = false;


void setupComms() {
  Serial.setTimeout(2);
}


void receiveFromPi() {
  if (!Serial.available()) {
    return;
  }

  String line;

  while (Serial.available()) {
    line = Serial.readStringUntil('\n');
  }

  line.trim();

  int tIndex = line.indexOf("track:");
  int azIndex = line.indexOf("az:");
  int altIndex = line.indexOf("alt:");

  if (tIndex == -1 || azIndex == -1 || altIndex == -1) {
    return;
  }

  current_state = line.substring(tIndex + 6, line.indexOf(',', tIndex)).toInt();
  dev_az = line.substring(azIndex + 3, line.indexOf(',', azIndex)).toFloat();
  dev_alt = line.substring(altIndex + 4).toFloat();
}

