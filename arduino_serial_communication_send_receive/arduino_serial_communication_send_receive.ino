/**
* 
* This sketch reads multiple analog and digital sensors as well as the IMU, and sends the values on the serial port.
* This sketch also receives meessages from the serial port in the format [string,number], and then
* associates to this messages a certain behavior (e.g, triggering a vibration motor pattern)
* 
* The analog sensors values are filtered with a butterworth lowpass filter.
* The filtering is achieved by means of the library https://github.com/tttapa/Filters
* The coefficients for the filter are calculated using the tools: http://www.exstrom.com/journal/sigproc/
* 
* 
* Author: Luca Turchet
* Date: 30/05/2019
* 
* 
* 
* 
**/

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <EEPROM.h>
#include <IIRFilter.h>
#include <string.h>

  

#define BAUD_RATE 115200 //NOTE: on the Teensy this is meaningless as the Teensy always transmits data at the full USB speed


/* Variables for incoming messages *************************************************************/

const byte MAX_LENGTH_MESSAGE = 64;
char received_message[MAX_LENGTH_MESSAGE];

char START_MARKER = '[';
char END_MARKER = ']';

    
boolean new_message_received = false;


/* Digital outputs *************************************************************/

const uint16_t motor_up_pin = 7; 
const uint16_t motor_down_pin = 8; 
const uint16_t motor_left_pin = 9; 
const uint16_t motor_right_pin = 10;

unsigned long motor_up_last_debounce_time = 0;  
unsigned long motor_down_last_debounce_time = 0;  
unsigned long motor_left_last_debounce_time = 0; 
unsigned long motor_right_last_debounce_time = 0;  

unsigned long debounce_delay = 50;    // the debounce time; increase if the output flickers


/* Analog inputs ******************************************************************************************/

#define ANALOG_BIT_RESOLUTION 12 // Only for Teensy

//static const unsigned long ANALOG_PERIOD_MILLISECS = 1; // E.g. 4 milliseconds per sample for 250 Hz
//static const unsigned long ANALOG_ANALOG_PERIOD_MICROSECS = 1000 * PERIOD_MILLISECS;
//static const float ANALOG_SAMPLING_FREQUENCY = 1.0e3f / PERIOD_MILLISECS;
#define ANALOG_PERIOD_MICROSECS 1000
static uint32_t analog_last_read = 0;


uint16_t analog_input0_pin = 2;
uint16_t analog_input0 = 0;
uint16_t analog_input0_lp_filtered = 0;
uint16_t previous_analog_input0_lp_filtered = 0;


// 50 Hz Butterworth low-pass
double a_lp_50Hz[] = {1.000000000000, -3.180638548875, 3.861194348994, -2.112155355111, 0.438265142262};
double b_lp_50Hz[] = {0.000416599204407, 0.001666396817626, 0.002499595226440, 0.001666396817626, 0.000416599204407};
IIRFilter lp_analog_input0(b_lp_50Hz, a_lp_50Hz);


//Thresholds for each sensor
uint16_t analog_input0_threshold = 5;



/** Functions for handling received messages ***********************************************************************/

void receive_message() {
  
    static boolean reception_in_progress = false;
    static byte ndx = 0;
    char rcv_char;

    while (Serial.available() > 0 && new_message_received == false) {
        rcv_char = Serial.read();
        Serial.println(rcv_char);

        if (reception_in_progress == true) {
            if (rcv_char!= END_MARKER) {
                received_message[ndx] = rcv_char;
                ndx++;
                if (ndx >= MAX_LENGTH_MESSAGE) {
                    ndx = MAX_LENGTH_MESSAGE - 1;
                }
            }
            else {
                received_message[ndx] = '\0'; // terminate the string
                reception_in_progress = false;
                ndx = 0;
                new_message_received = true;
            }
        }
        else if (rcv_char == START_MARKER) {
            reception_in_progress = true;
        }
    }

    if (new_message_received) {
      handle_received_message(received_message);
      new_message_received = false;
    }
}

void handle_received_message(char *received_message) {

  //Serial.print("received_message: ");
  //Serial.println(received_message);

  
  char *all_tokens[2]; //NOTE: the message is composed by 2 tokens: command and value
  const char delimiters[5] = {START_MARKER, ',', ' ', END_MARKER,'\0'};
  int i = 0;

  all_tokens[i] = strtok(received_message, delimiters);
  
  while (i < 2 && all_tokens[i] != NULL) {
    all_tokens[++i] = strtok(NULL, delimiters);
  }

  char *command = all_tokens[0]; 
  char *value_str = all_tokens[1];
  
  int value = 0;
  sscanf(value_str, "%d", &value);

  if (strcmp(command,"motor_up_pattern") == 0) {

    /*
    Serial.print("activating message 1: ");
    Serial.print(command);
    Serial.print(" ");
    Serial.print(value);
    Serial.println(" ");
    */
    
    analogWrite(motor_up_pin, value);
    
  }
  if (strcmp(command,"motor_down_pattern") == 0) {    
    analogWrite(motor_down_pin, value);
    
  }
  if (strcmp(command,"motor_left_pattern") == 0) {    
    analogWrite(motor_left_pin, value);
    
  }
  if (strcmp(command,"motor_right_pattern") == 0) {    
    analogWrite(motor_right_pin, value);
    
  }
}




/**************************************************************************************************************/

void setup() {
  Serial.begin(BAUD_RATE);
  while(!Serial);

  /* Setup of the digital sensors ******************************************************************************/
  pinMode(motor_up_pin, OUTPUT);
  pinMode(motor_down_pin, OUTPUT);
  pinMode(motor_left_pin, OUTPUT);
  pinMode(motor_right_pin, OUTPUT);

  digitalWrite(motor_up_pin, LOW);
  digitalWrite(motor_down_pin, LOW);
  digitalWrite(motor_left_pin, LOW);
  digitalWrite(motor_right_pin, LOW);

  /* Setup of the analog sensors ******************************************************************************/
 
  analogReadResolution(ANALOG_BIT_RESOLUTION); // Only for Teensy
  
}




/****************************************************************************************************/

void loop() {


  receive_message();

  
  /* Loop for the analog and digital sensors ******************************************************************************/
  
  if (micros() - analog_last_read >= ANALOG_PERIOD_MICROSECS) {
    analog_last_read += ANALOG_PERIOD_MICROSECS;

    
    /* Loop for the analog sensors ******************************************************************************/

    analog_input0 = analogRead(analog_input0_pin);
    analog_input0_lp_filtered =  (uint16_t)lp_analog_input0.filter((double)analog_input0);    

    // Apply thresholds to the filtered signal
    analog_input0_lp_filtered = (analog_input0_lp_filtered < analog_input0_threshold) ? 0 : analog_input0_lp_filtered;

    //Plot on the Serial Plotter the unfiltered sensors values 
    /*
    Serial.print(analog_input0);
    Serial.print(" ");
    Serial.print(analog_input1);
    Serial.print(" ");
    Serial.print(analog_input2);
    Serial.print(" ");
    Serial.println(analog_input3);
    */


    //Plot on the Serial Plotter the filtered sensors values 
    /*
    Serial.print(analog_input0_lp_filtered);
    Serial.print(" ");
    Serial.print(analog_input1_lp_filtered);
    Serial.print(" ");
    Serial.print(analog_input2_lp_filtered);
    Serial.print(" ");
    Serial.println(analog_input3_lp_filtered);
    */



    // Send the sensor value to the serial port only if it has changed
    
    if(analog_input0_lp_filtered != previous_analog_input0_lp_filtered){
      Serial.print("a0, ");
      Serial.println(analog_input0_lp_filtered);
      //Serial.print(analog_input0);
      //Serial.print(" ");
      //Serial.println(analog_input0_lp_filtered);
      previous_analog_input0_lp_filtered = analog_input0_lp_filtered;
    }

    /*if (analog_input0_lp_filtered > 50) {
      //Serial.println("Motor ON");
      analogWrite(motor_up_pin, analog_input0_lp_filtered);
      analogWrite(motor_down_pin, analog_input0_lp_filtered);
      analogWrite(motor_left_pin, analog_input0_lp_filtered);
      analogWrite(motor_right_pin, analog_input0_lp_filtered);
    }
    else {
      //Serial.println("Motor OFF");
      analogWrite(motor_up_pin, 0);
      analogWrite(motor_down_pin, 0);
      analogWrite(motor_left_pin, 0);
      analogWrite(motor_right_pin, 0);
    }*/
        
  } // End of the section processing the analog sensors with the set sample rate for them
  
}
