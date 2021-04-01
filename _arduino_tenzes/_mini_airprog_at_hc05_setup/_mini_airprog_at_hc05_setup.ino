void setup() {
  Serial.begin(38400); //BAUDRATE FOR AT MODE (ALWAYS)
  delay(500);
  Serial.println("AT+NAME=Mini_airprog_19200");
  delay(500);
  Serial.println("AT+UART=19200,0,0");    
  // baudrate=19200 to program Arduino Uno. (WORKED with STATE_to_RES manual keying)
  // baudrate=115200 to program Arduino Uno. (WORKED with 1uf 50v capacitor and STATE_to_RES)
  delay(500);
  Serial.println("AT+POLAR=1,0");
  delay(500);
}

void loop() {
}
