// motors.ino

const int STP1 = 5;
const int STP2 = 0;
const int DIR1 = 6;
const int DIR2 = 1;

extern float motorspeed_az;   // steps per sekund (+/-)
extern float motorspeed_alt;  // steps per sekund (+/-)

unsigned long last_step_time_az = 0;
unsigned long last_step_time_alt = 0;
unsigned long time_now = 0;
unsigned long interval_az = 0;
unsigned long interval_alt = 0;


void setupMotors() {
  pinMode(STP1, OUTPUT);
  pinMode(STP2, OUTPUT);
  pinMode(DIR1, OUTPUT);
  pinMode(DIR2, OUTPUT);
}


void updateMotorAZ() {

  if (motorspeed_az == 0) {
    return;
  }

  interval_az = 1000000 / fabs(motorspeed_az);
  time_now = micros();

  digitalWrite(DIR1, motorspeed_az > 0);

  if (time_now - last_step_time_az >= interval_az) {

    digitalWrite(STP1, HIGH);
    delayMicroseconds(5);
    digitalWrite(STP1, LOW);

    last_step_time_az = time_now;
  }

}


void updateMotorALT() {

  if (motorspeed_alt == 0) {
    return;
  }

  interval_alt = 1000000 / fabs(motorspeed_alt);
  time_now = micros();

  digitalWrite(DIR2, motorspeed_alt > 0);

  if (time_now - last_step_time_alt >= interval_alt) {

    digitalWrite(STP2, HIGH);
    delayMicroseconds(5);
    digitalWrite(STP2, LOW);

    last_step_time_alt = time_now;
  }

}


void motorsTask() {
  updateMotorAZ();
  updateMotorALT();
}