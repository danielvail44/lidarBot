#include "Motor.h"
#include "Servo.h"
#include "SoftPWM.h"
#include "Thread.h"
#include "mbed.h"
#include "rtos.h"

RawSerial lidar(p13, p14);
short dist;   // actual distance measurements of LiDAR
int strength; // signal strength of LiDAR
int check;    // save check value
int i;
int uart[9];             // save data measured by LiDAR
const int HEADER = 0x59; // frame header of data package
int angle = 0;
int readings[180];
int readings2[180];
bool autoMode = false;

bool scanning = true;

int getDistance() {

  while (lidar.readable()) {
    lidar.getc();
  }
  while (1) { // check if serial port has data input
    while (lidar.getc() != HEADER) {
      //    printf("Waiting...\n");
    };

    if (lidar.getc() != HEADER) {
      continue;
    }
    uart[0] = HEADER;
    uart[1] = HEADER;
    for (i = 2; i < 9; i++) { // save data in array
      uart[i] = lidar.getc();
    }
    check = uart[0] + uart[1] + uart[2] + uart[3] + uart[4] + uart[5] +
            uart[6] + uart[7];
    if (uart[8] == (check & 0xff)) { // verify the received data as per protocol
      dist = uart[2] + uart[3] * 256;     // calculate distance value
      strength = uart[4] + uart[5] * 256; // calculate signal strength value
      dist += 1;
      return dist;
    }
  }
}

PwmOut servo(p26);
RawSerial pi(p28, p27);
Motor lMotor(p21, p23, p24); // pwm, fwd, rev
Motor rMotor(p22, p29, p30); // pwm, fwd, rev
Thread scanner;
Thread driveThread;
int centerDist = 0;
void turn(int degrees);
void drive(int distance);
int minDist(int degrees);
int getAngle();
void drive();
int minDistWide(int degrees);
void setServo(int deg) {
  // printf("%d\n", deg);
  float d = float(deg);
  float x = 1.8;
  d = ((d / 180.0) - .5) * 1000 * x;
  d += 1500;
  servo.pulsewidth_us(d);
}

void scan() {
  while (true) {
    if (scanning) {
      printf("Starting scan: \r\n\r\n");

      for (int j = 0; j < 180; j++) {
        setServo(j);
        // printf("%d degrees...\r\n", j);
        //  wait(.01);
        int distance = getDistance();
        readings[j] = distance;
        if (i == 90) {
          centerDist = distance;
        }
      }

      //    printf("\r\n\r\n\r\nAngle,Distance\n\r");
      for (int j = 0; j < 180; j++) {
        //      printf("%d, %d\n\r", j, readings[j]);
        pi.printf("%d\n", readings[j]);
        readings2[i] = readings[j];
      }

      for (int j = 179; j >= 0; j--) {
        setServo(j - 10);
        // printf("%d degrees...\r\n", j);
        // wait(.01);
        int distance = getDistance();
        readings[j] = distance;
        if (i == 90) {
          centerDist = distance;
        }
      }

      //    printf("\r\n\r\n\r\nAngle,Distance\n\r");
      for (int j = 0; j < 180; j++) {
        //      printf("%d, %d\n\r", j, readings[j]);
        pi.printf("%d\n", readings[j]);
        readings2[i] = readings[j];
      }
    }
  }
}

int main() {
  servo.period_ms(20);
  scanner.start(scan);
  lidar.baud(115200);
  pi.baud(115200);
  getAngle();
  wait(1.5);
  while (1) {
    char c = pi.getc();
    printf("Character: %c", c);

    if (c == 'S') {
      scanning = true;
      printf("Best angle: %d", getAngle());
    }
    if (c == 's') {
      scanning = false;
    }

    if (c == 'S') {
      scanning = true;
      printf("Best angle: %d", getAngle());
    }
    if (c == 's') {
      scanning = false;
    }
    if (c == 'a') {
      if (autoMode) {
        autoMode = false;
        driveThread.terminate();
      }
    }
    if (c == 'A') {
      if (!autoMode) {
        autoMode = true;
        driveThread.start(drive);
      }
    }

    if (!autoMode) {
      if (c == 'F') {
        lMotor.speed(.5);
        rMotor.speed(.5);
      }
      if (c == 'f') {
        lMotor.speed(0);
        rMotor.speed(0);
      }
      if (c == 'B') {
        lMotor.speed(-.5);
        rMotor.speed(-.5);
      }
      if (c == 'b') {
        lMotor.speed(0);
        rMotor.speed(0);
      }
      if (c == 'R') {
        lMotor.speed(.5);
        rMotor.speed(-.5);
      }
      if (c == 'r') {
        lMotor.speed(0);
        rMotor.speed(0);
      }
      if (c == 'L') {
        lMotor.speed(-.5);
        rMotor.speed(.5);
      }
      if (c == 'l') {
        lMotor.speed(0);
        rMotor.speed(0);
      }
    }
  }
}

void drive() {
  while (1) {
    turn(getAngle());
    drive(minDistWide(getAngle() + 90) / 2);
  }
}

void turn(int degrees) {
  float time = abs(degrees) / 140.0;
  if (degrees > 0) {
    lMotor.speed(.35);
    rMotor.speed(-.35);
  } else {
    lMotor.speed(-.35);
    rMotor.speed(.35);
  }
  wait(time);
  lMotor.speed(0);
  rMotor.speed(0);
}
void drive(int distance) {
  float time = distance / 15.0;
  if (time > 5){
      time = 5;
  }
  lMotor.speed(.3);
  rMotor.speed(.3);
  uint32_t timestart = us_ticker_read();
  while (minDist(90) > 10 and us_ticker_read() - timestart < time * 1000000) {
    printf("Waiting: %d\n", minDist(90));
  }
  lMotor.speed(0);
  rMotor.speed(0);
  if (minDistWide(90) <= 30) {
    wait(1.5);
  }
  printf("Wide: %d\n", minDistWide(90));
}
int minDist(int degrees) {
  int min = 2000;
  for (int i = degrees - 10; i < degrees + 10; i++) {
    if (readings[i] < min) {
      min = readings[i];
    }
  }
  return min;
}
int minDistWide(int degrees) {
  int min = 2000;
  for (int i = degrees - 20; i < degrees + 20; i++) {
    if (readings[i] < min) {
      min = readings[i];
    }
  }
  return min;
}
int getAngle() {
  int bestAngle = 0;
  int max = 0;
  int dist;
  for (int i = 10; i < 170; i++) {
    // printf("Angle: %d, distance: %d\r\n",i, dist);
    dist = minDistWide(i);
    if (dist > max) {
      max = dist;
      bestAngle = i;
    }
  }
  bestAngle -= 90;
  return bestAngle;
}