void setup() {
  Serial.begin(38400); //BAUDRATE FOR AT MODE (ALWAYS)
  delay(500);
  Serial.println("AT+NAME=T-0b");
  delay(500);
  Serial.println("AT+UART=57600,0,0");  
  //uno.upload.speed=115200

  //pro.menu.cpu.8MHzatmega168.upload.speed=19200
  //pro.menu.cpu.16MHzatmega168.upload.speed=19200
  //pro.menu.cpu.8MHzatmega328.upload.speed=57600
  //pro.menu.cpu.16MHzatmega328.upload.speed=57600
  delay(500);
  Serial.println("AT+POLAR=1,0");
  delay(500);
}

void loop() {
}
