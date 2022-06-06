# ACEcar
Saxion university of applied sciences Project system 2022 ACEcar repo. 

# Team members
- Miguel Pérez Hernández: 524262
- Karolis Juozapaitis: 517546
- Jurijs Zuravlovs: 440882
- Dmytro Taras: 516824
- Tarik Mandic: 523830

# Goal
To make an autonomous car that follows a line and avoids obstacles using a camera (Plan B is to use an ultrasonic sensor and light sensor array).

# What is what
- ACEcar - Main folder where main code is
- Altium files - Schematics, PCB, Gerber and other files
- Arduino test files - Files for testing different functions whre an arduino is required.
- Component sktetches - Component 3d models and sketches
- Documents - Files such as Reports and project plans and so on
- PC test files - Files for testing different functions for pc side
- Pictures - Project pictures and so on
- Raspberry pi setup - Text files that contain commands + config strings to prepare  the raspberry pi to funtion correctly for the desired requirements
- Raspberry pi test files - Files for testing different functions for pi side.

# Raspberry Pi pin configuration
- Monster Moto Driver
  - INA- 5
  - INB- 6
  - Drive (PWM1)- 12
  - Steer (SPWM)- 13

- UART
  - UART TX- 14
  - UART RX- 15

- 8x IR Line Tracking Module
  - IR- 16
  - D1-D8 -> ADC

- ADC0,1
   - SPI: 7, 8, 9, 10, 11
   - GPIO 7- CS1
   - GPIO 8- CS0

- Ultrasonic
  - Trig- 20
  - Echo- 21

# Sources
  OpenCV- https://github.com/opencv/opencv
  
  
