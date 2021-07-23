void execute_at_command(String at_cmd_text){
  Serial.println(at_cmd_text);
  if(Serial.available() > 0){Serial.readString();} 
  //ошибка: ответ не выводится в монитор порта
  delay(500);
  }

void setup() {
  Serial.begin(38400); //BAUDRATE FOR AT MODE (ALWAYS)
  delay(500);
  execute_at_command("AT");
  execute_at_command("AT+NAME=T-13");
  execute_at_command("AT+UART=19200,0,0"); 
  //"AT+UART=19200,0,0" means baudrate=19200, one stop bit, parity check disabled
  // baudrate=19200 to program Arduino Pro Mini (those 168 ones at least). 
  //(WORKED with STATE_to_RES manual keying)
  // baudrate=115200 to program Arduino Uno. 
  //(WORKED with 1uf 50v capacitor and STATE_to_RES)
  execute_at_command("AT+POLAR=1,0");
}

void loop() {
}
