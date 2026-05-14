// regulation.ino

const float Kp_az = 100.0;
const float Kp_alt = 100.0;

const float minSpeed = -1000.0;       // steps/s
const float maxSpeed = 1000.0;        // steps/s
const float deadband = 0.0;           // grader
const float maxAccel = 1000.0;        // steps/s^2

float motorspeed_az = 0;
float motorspeed_alt = 0;

extern float dev_az;
extern float dev_alt;
extern bool current_state;
extern float angle;

const int DIAG1 = 4;
const int DIAG2 = 7;

static unsigned long lastDIAG1Print = 0;
static unsigned long lastDIAG2Print = 0;



float approach(float current, float target, float maxStep) {
  if (target > current + maxStep) return current + maxStep;
  if (target < current - maxStep) return current - maxStep;
  return target;
}


void setupRegulation() {
  pinMode(DIAG1, INPUT_PULLUP);
  pinMode(DIAG2, INPUT_PULLUP);
}


void regulationTask() {

  if (digitalRead(DIAG1) == HIGH || digitalRead(DIAG2) == HIGH) {

    motorspeed_az = 0.0;
    motorspeed_alt = 0.0;

    if (digitalRead(DIAG1) == HIGH && millis() - lastDIAG1Print >= 2000) {

      lastDIAG1Print = millis();

      Serial.println("Feil fra stepperdriver 1! Motorer er stoppet");
    }

    if (digitalRead(DIAG2) == HIGH && millis() - lastDIAG2Print >= 2000) {

      lastDIAG2Print = millis();

      Serial.println("Feil fra stepperdriver 2! Motorer er stoppet");
    }

    return;
  }

  float target_az = 0.0;
  float target_alt = 0.0;

  if (fabs(dev_az) >= deadband) {
    target_az = constrain(Kp_az * dev_az, minSpeed, maxSpeed);
  }
  if (fabs(dev_alt) >= deadband) {
    target_alt = constrain(Kp_alt * dev_alt, minSpeed, maxSpeed);
  }

  static unsigned long lastRegTime = micros();
  unsigned long now = micros();

  float dt = (now - lastRegTime) / 1000000.0;
  lastRegTime = now;

  float maxDelta = maxAccel * dt;

  motorspeed_az = approach(motorspeed_az,  target_az,  maxDelta);
  motorspeed_alt = approach(motorspeed_alt, target_alt, maxDelta);


  if (angle < 1.0) {
    motorspeed_alt = max(motorspeed_alt, 0.0f);
  }

  if (angle > 89.0) {
    motorspeed_alt = min(motorspeed_alt, 0.0f);
  }


}