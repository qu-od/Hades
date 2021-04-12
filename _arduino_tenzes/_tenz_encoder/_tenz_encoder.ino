#include "HX711.h"
#define sck 6
#define dt 7
HX711 tenz;
using namespace std;

void setup() {

  Serial.begin(19200);
  tenz.begin(dt,sck);

  /*Serial.print("Показания датчика с учетом веса тары: \t\t");
  Serial.println(tenz.get_value(10));

  Serial.print("Показания датчика с учетом веса тары и с учетом калибровочного коэффициента: \t\t");
  Serial.println(tenz.get_units(10));*/
  
}

void loop() {
  delay(1000);
  
  int command_len_in_bytes = 6;
  char command_buffer[command_len_in_bytes];
  struct Command{ //6 bytes
    char header; // to recognize a command header must be 42
    //header is kinda key to acsess 
    char number; // uint8 command number
    //unsigned int data_field_size; // uint8 data field size
    float data_value; // data value (float - 4 bytes long)
    };
  int response_len_in_bytes = 6;
  struct Response{
    char header; // to recognize a response header must be 42
    char error_code; // 0 means "no error" (1 byte for char)
    float data_value; // 4 bytes for float
    };

  if (Serial.available() > 0){ 
    Command command;
    Response response;
    response.header = 42;
    int number_of_bytes_read = Serial.readBytes(command_buffer, Serial.available());
    if (number_of_bytes_read == command_len_in_bytes){
      response.error_code = 100; // clear with initial error_code 
      response.data_value = 0; // clear data
      memcpy(&command, command_buffer, number_of_bytes_read); //unpack from bytes
      if (command.header == 42){
        if (command.number == 0){           // tare()
          tenz.tare(1);
          response.error_code = 0;
          }
        else if (command.number == 1){      // get_value()
          float value = tenz.get_value(1);
          response.data_value = value;
          response.error_code = 0;
          }
        else if (command.number == 2){      // set_scale()
          tenz.set_scale(command.data_value); // NEED TESTING!
          response.error_code = 0;
          }
        else if (command.number == 3){      // get_units()
          float units = tenz.get_units(1);
          response.data_value = units;
          response.error_code = 0;
          }
        else {
          response.error_code = 3; // Wrong command number
          }
        }
      else {response.error_code = 2;} // Wrong command header
      }
    else {response.error_code = 1;} // Wrong command size
    char bytes_response[sizeof(response)];
    memcpy(bytes_response, &response, sizeof(response)); //pack to bytes
    Serial.write(bytes_response, response_len_in_bytes);
  }
  

}
