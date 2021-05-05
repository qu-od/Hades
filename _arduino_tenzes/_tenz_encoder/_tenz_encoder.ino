#include "HX711.h"
#define sck 6 //пин для синхроимпульса
#define dt 7 //пин для посылки данных

HX711 tenz;

char this_encoder_number;
int millis_for_delay = 500; 
//начальное значение задержки между итерациями (delay)
int times_to_measur = 5;
//начальное значение количества измерений для получения одного значения
int command_len_in_bytes = 6;
int response_len_in_bytes = 6;

struct Command{ //6 bytes
  char header; // to recognize a command header must be an encoder number 
  //header is kinda key to acsess 
  //(1 to 12 - workers, 13-20 - spare encoders, 42 - test encoder)
  char number; // uint8 command number
  //unsigned int data_field_size; // uint8 data field size
  float data_value; // data value (float - 4 bytes long)
  };

struct Response{
  char header; // (1 to 12 - workers, 13-20 - spare encoders, 42 - test encoder)
  char error_code; // 0 means "no error" (1 byte for char)
  float data_value; // 4 bytes for float
  };


void setup() {

  Serial.begin(19200);
  tenz.begin(dt,sck);

  /*Serial.print("Показания датчика с учетом веса тары: \t\t");
  Serial.println(tenz.get_value(10));

  Serial.print("Показания датчика с учетом веса тары и с учетом калибровочного коэффициента: \t\t");
  Serial.println(tenz.get_units(10));*/
  
}

void loop() {
  delay(1); //in millis. Deletion of this delay could raise power consumption!
  if (Serial.available() >= 6){
    char command_buffer[command_len_in_bytes];
    Command command;
    Response response;
    response.header = 42;
    response.error_code = 100; // clear with initial error_code 
    response.data_value = 0; // clear data
    int number_of_bytes_read = Serial.readBytes(command_buffer, Serial.available());
    if (number_of_bytes_read == command_len_in_bytes){
      memcpy(&command, command_buffer, number_of_bytes_read); //unpack from bytes
      if (command.header == 42){
        if (command.number == 0){           // tare()
          response.data_value = tenz.get_value(times_to_measur);
          //excessive output here. Не пропадать же месту в response.data_value
          tenz.tare(times_to_measur);
          response.error_code = 0;
          }
        else if (command.number == 1){      // get_value()
          float value = tenz.get_value(times_to_measur);
          response.data_value = value;
          response.error_code = 0;
          }
        else if (command.number == 2){      // set_scale()
          tenz.set_scale(command.data_value); 
          response.data_value = command.data_value; // echo for debug
          response.error_code = 0;
          }
        else if (command.number == 3){      // get_units()
          float units = tenz.get_units(times_to_measur);
          response.data_value = units;
          response.error_code = 0;
          }
        else if (command.number == 4){      // change delay
          millis_for_delay = command.data_value; //implicit float-to-int conversion
          response.data_value = command.data_value; //echo for debug
          response.error_code = 0;
          }
        else if (command.number == 5){      // change times_to_take_measurment
          times_to_measur = command.data_value; //implicit float-to-int conversion
          response.data_value = command.data_value; //echo for debug
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
    delay(millis_for_delay);
    //delete command
    //delete response
  }
  

}
