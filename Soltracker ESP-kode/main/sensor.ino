// sensor.ino

#include <Wire.h>
#include "SparkFun_BMI270_Arduino_Library.h"

BMI270 imu;

uint8_t i2cAddress = BMI2_I2C_PRIM_ADDR;

const int sdaPin = 23;
const int sclPin = 22;

float accX = 0;
float accY = 0;
float accZ = 0;
float angle = 0;

void setupSensor() {

    Wire.setPins(sdaPin, sclPin);
    Wire.begin();
    Wire.setClock(400000);

    while (imu.beginI2C(i2cAddress) != BMI2_OK)
    {
        Serial.println("Error: BMI270 feilet oppkobling, sjekk tilkobling!");
        delay(1000);
    }

    Serial.println("BMI270 tilkoblet!");

    bmi2_sens_config accelConfig;
    accelConfig.type = BMI2_ACCEL;

    accelConfig.cfg.acc.odr = BMI2_ACC_ODR_100HZ;
    accelConfig.cfg.acc.bwp = BMI2_ACC_OSR2_AVG2;
    accelConfig.cfg.acc.filter_perf = BMI2_PERF_OPT_MODE;
    accelConfig.cfg.acc.range = BMI2_ACC_RANGE_2G;

    int8_t err = imu.setConfig(accelConfig);

    if (err != BMI2_OK)
    {
        Serial.println("Akselerometer-konfigurasjon feilet!");
        return;
    }

    Serial.println("Akselerometer satt opp!");
}

void sensorTask() {

    imu.getSensorData();

    accX = imu.data.accelX;
    accY = imu.data.accelY;
    accZ = imu.data.accelZ;

    angle = atan2(sqrt(accX * accX + accY * accY), abs(accZ)) * 180.0 / PI;
}

