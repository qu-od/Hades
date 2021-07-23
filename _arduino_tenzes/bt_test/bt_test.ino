#define ledPin LED_BUILTIN
//int state = 0;
char echo = 'n';
void setup() {
    pinMode(ledPin, OUTPUT);
    digitalWrite(ledPin, LOW);
    Serial.begin(19200); //might try 9600 but why?
    //baudrate=19200 to match arduino pro mini w 168 baudrate
}
void loop() {
 delay(50);
 digitalWrite(LED_BUILTIN, LOW);  
 delay(50);                     
 digitalWrite(LED_BUILTIN, HIGH);
  
 //byte Btearray[] = {0x00, 0xff, 0x88};
 //Serial.println((char*)Btearray);
 if(Serial.available() > 0){ // Checks whether data is comming from the serial port
     echo = Serial.read(); // Reads the data from the serial port
     Serial.println(echo);
 }
 Serial.println("---Посылка значит так от мелкой ардуины, прошитой по воздуху!---");
 
 if (echo == '1') {
     digitalWrite(ledPin, HIGH); // Turn LED OFF
     Serial.println("LED: ON"); // Send back, to the phone, the String "LED: ON"
     echo = 'n';
 }
 else if (echo == '0') {
     digitalWrite(ledPin, LOW);
     Serial.println("LED: OFF");
     echo = 'n';
 } 
}
