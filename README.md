# WorldMood
A simple social scraper connected to a colorful world map.

This project is divided by two pieces of code:
* Worldmood_computer.py: this python script scrapes data on Facebook, and computes the total amount of reactions on the latest post of several news pages. Reactions are gathered and organized by geographic area, and converted to a payload string. The payload is sent to the microcontroller through a serial connection.
* Worldmood_arduino.ino: this arduino script receives the payload string, analyzes it, and controls the addressable leds depending on the message content.

![Worldmood in action](https://scimaker.files.wordpress.com/2019/12/worldmood_1.jpg)
