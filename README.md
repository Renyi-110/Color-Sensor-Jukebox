<div align="center">

# Color Sensor Jukebox

### A music composer/player using colors.

List of Materials

| Product \# | Name | Qty | Dimension | Function | Interaction with other parts | Website |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 1 | Raspberry Pi 4 | 1 | 85.6 mm × 56.5 mm × 17 mm | Main microcontroller/computer | controls all electronics, interfaces with sensors, actuators, displays | raspberrypi.com |
| 2 | Raspberry Pi screen | 1 | 155 mm × 86 mm × 20 mm | display output, touchscreen input | connects to Pi via DSI or HDMI, displays GUI and data | raspberrypi.com |
| 3 | Raspberry Pi Cobbler | 1 | 73 mm (L) × 20 mm (W) × 11 mm (H) | Breaks out Pi GPIO to breadboard | Connects Pi GPIO header to breadboard for prototyping | adafruit.com |
| 4 | Micro HDMI | 1 | 5.83 mm × 2.20 mm × 7 mm | Video output cable | Connects Pi to HDMI display | raspberrypi.com |
| 5 | Standard HDMI | 1 | 13.9 mm × 4.45 mm × 21 mm | Video output cable | Connects Pi or other devices to HDMI display | raspberrypi.com |
| 6 | USB-C Power Cable | 1 | 8.4 mm × 2.6 mm × 6 mm | Power supply | powers Raspberry Pi | raspberrypi.com |
| 7 | Breadboard | 1 | 1.77" (L) × 1.36" (W) × 0.37" (H) | Prototyping circuit connections | hosts components and jumpers for circuit assembly | adafruit.com |
| 8 | Servo Motor | 2 | 22.2 mm (L) × 11.8 mm (W) × 31 mm (H | actuator for movement | controlled by pi GPIO, moves drawer/pointer via PWM | adafruit.com |
| 9 | Passive Buzzer | 1 | 12 mm × 12 mm × 8.5 mm | sound output | driven by PI GPIO for notes | adafruit.com |
| 10 | 3d printed Rack | 1 | 2" (L) × 0.25" (W) × 0.25" (H) | mechanical movement part | interfaces with servo and pinion for moving drawer | Mcmaster Carr |
| 11 | 3d printed Pinion | 1 | 0.58" (OD) × 0.5" (Overall Width) × 0.25" (Face Width) | mechanical movement part | interfaces with rack and servo motor | Mcmaster Carr |
| 12 | Different color LED’s | 5 | 5mm (D) × 8.6mm (L, body) × \~25mm (total height with leads), with 2.54mm lead spacing | visual indicators | controlled by Pi GPIO, shows status/colors | adafruit.com |
| 13 | Jumper wires | 30 | 2-3 inches long | Circuit connections | Connect PI, breadboard, and components | adafruit.com |
| 14 | TCS3200 Color Sensor | 1 | 32 mm (L) × 24.7 mm (W) × \~19 mm (H) | detects color of objects | sends color data to pi via GPIO, interacts with servo, leds, and buzzer  | robotshop.com |
| 15 | ¼ watt Resistor | 5 | \~6.3 mm (L) × 2.3 mm (D)  | limits current to LEDs and buzzer | Placed in series with LEDs/buzzer to protect components |  |
| 16 | Different color chips  | 5 | 1.5 inch diameter x height 0.5 inch | test/sample objects for color sensor | place in front of sensor, sorted by system | adafruit.com |
| 17 | Roll of clear tape | 1 | na | assembly | holds wires or parts in place | staples.com |
| 18 | Elmers clear glue |  | na | assembly | glues cardboard | staples.com |
| 19 | Roll of Electrical Tape | 1 | na | assembly | insulates and secures electrical connections | Home |
| 20 | Cardboard Jukebox | 1 | 1ft x 2inch x | housing | houses all components, provides structure | staples.com |
| 21 | Cardboard drawer | 1 | 2" (Length) × 2" (Width) × 1" (Height) | holds sorted chips | moved by servos and interacts with rack and pinion | Home |

