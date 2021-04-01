#include "HX711.h"
#define dt 7
#define sck 6
HX711 tenz;
using namespace std;

void setup() {

  Serial.begin(19200);
  tenz.begin(dt,sck);
  
  Serial.println("Показания датчика ДО калибровки и тарирования");
  
  Serial.print("Показания датчика по 1-ому измерению: \t\t");
  Serial.println(tenz.read());

  Serial.print("Показания датчика по 10-ти измерениям: \t\t");
  Serial.println(tenz.read_average(10));

  Serial.print("Масса тары: \t\t");
  Serial.println(tenz.get_offset());

  Serial.print("Калибровочный коэффициент: \t\t");
  Serial.println(tenz.get_scale());

  Serial.println("Установите в течение 5 секунд тару на тензодатчик");
  delay(5000);
  tenz.tare(10);
  tenz.set_scale();

  Serial.println("Показания датчика ПОСЛЕ калибровки и тарирования");
  
  Serial.print("Показания датчика по 1-ому измерению: \t\t");
  Serial.println(tenz.read());

  Serial.print("Показания датчика по 10-ти измерениям: \t\t");
  Serial.println(tenz.read_average(10));

  Serial.print("Масса тары: \t\t");
  Serial.println(tenz.get_offset());

  Serial.print("Калибровочный коэффициент: \t\t");
  Serial.println(tenz.get_scale());

  Serial.print("Показания датчика с учетом веса тары: \t\t");
  Serial.println(tenz.get_value(10));

  Serial.print("Показания датчика с учетом веса тары и с учетом калибровочного коэффициента: \t\t");
  Serial.println(tenz.get_units(10));
  

}

void loop() {
  delay(1000);
  //определение и обнуление
  int command = '0';
  String response("");

  //обработка команды (если она пришла)
  if(Serial.available() > 0)
  {
      command = Serial.read(); // Reads the data from the serial port
      response += String("Command recieved!");

    if (command == '0') { // "make tare" command
      tenz.tare();
      response += String(" Tenz tared.");
    }

    if (command == '1') { // "get value" command supposed to 
      int value = tenz.get_value(5);
      response += (String(", ") + String(value));
    }

    if (command == '2') { // "set scale" command
      float test_scale = 32;
      tenz.set_scale(test_scale);
      response += (String(" New scale = ") + String(test_scale));
    }

    if (command == '3') { // "get units" command
      int units = tenz.get_units(5);
      response += (String(", ") + String(units));
    }

    if (command == '9') { // "send info" command
      int offset = tenz.get_offset();
      int scale = tenz.get_scale();
      response += (String(" Offset = ") + String(offset) + String(",  Scale = ") +  String(scale));
    } 

    //if (command > 2) {
    //  response = String('Wrong command');
    //}

    //Serial.println(command);
    Serial.println(response);
  }
}



