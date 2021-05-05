/*
  ReadAnalogVoltage

  Reads an analog input on pin 0, converts it to voltage, and prints the result to the Serial Monitor.
  Graphical representation is available using Serial Plotter (Tools > Serial Plotter menu).
  Attach the center pin of a potentiometer to pin A0, and the outside pins to +5V and ground.

  This example code is in the public domain.

  http://www.arduino.cc/en/Tutorial/ReadAnalogVoltage
*/

const int out_pin = 7;
// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
  pinMode(out_pin, OUTPUT);
  digitalWrite(out_pin, LOW);
}

// the loop routine runs over and over again forever:
void loop() {
  // read the input on analog pin 0:
  int sensorValue = analogRead(A0);
  // Convert the analog reading (which goes from 0 - 1023) to a voltage (0 - 5V):
  float voltage = sensorValue * (5.0 / 1023.0);
  // print out the value you read:
  Serial.println(voltage);


  if (voltage < 1.0) {
<<<<<<< HEAD
    digitalWrite(out_pin, HIGH);
=======
    digitalWrite(out_pin, 64);
>>>>>>> 0031ee2c38d3d66e4bd6300a4095b862a8a0a790
  }
  if (voltage > 3.0) {
    digitalWrite(out_pin, LOW);
  }

<<<<<<< HEAD
  delay(1000);
=======
  //delay(5);
>>>>>>> 0031ee2c38d3d66e4bd6300a4095b862a8a0a790
}