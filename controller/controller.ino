#include <WiFi.h>
#include <WiFiUdp.h>
#include <ESP32Servo.h>
#include <time.h>
#include <string.h>
#include <iostream>
#include <vector>
#include <sstream>
#include <regex>
#include <algorithm> 
#include <cctype> 
#include <thread> 
#include <chrono>
#include <typeinfo>

#define LED_PIN 2
 
std::vector<std::string> splitString(const std::string& str, char delimiter) {
    std::vector<std::string> tokens;
    std::stringstream ss(str);
    std::string token;

    while (std::getline(ss, token, delimiter)) {
        tokens.push_back(token);
    };

    return tokens;
}

void Update_LocalTime();
void replace_events(std::string replacement);
void send_events();
void check_if_now();
void activate_servo(int n);

struct event {
  std::string package;
  int year;
  int month;
  int day;
  int hour;
  int minute;
  int servo;
  std::string stringform;
};

std::vector<event> events;
event now;
const int eventCount = sizeof(events) / sizeof(events[0]);
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 0;
const int daylightOffset_sec = 3600;

const char* ssid = "HRP2.4G#";  
const char* password = "10lleTid!";  

WiFiUDP udp; 
unsigned int localPort = 8382; 

void send_message(std::string message){
      const char* msg = message.c_str();
      udp.beginPacket(udp.remoteIP(), udp.remotePort());  
      udp.write((const uint8_t*)msg, strlen(msg));
      udp.endPacket();
}

Servo servo1;
Servo servo2;

int servo_closed = 10;
int servo_opened = 180;

static std::vector<Servo*> servos = {&servo1, &servo2};

static const std::vector<int> servopins = {14, 12};
static const int servoAmount = servopins.size();

void setup() {

  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(115200);

  for(int i = 0; i<servoAmount; i++){
    servos[i]->attach(servopins[i]);
  };

  Serial.println("Hello!");
  WiFi.begin(ssid, password);  
  unsigned long startcount_rebootTime = millis();
  int val = 0x1;
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    unsigned long currentcount_rebootTime = millis();
    if (currentcount_rebootTime-startcount_rebootTime >= 6000){
      ESP.restart();
    }
    Serial.println(currentcount_rebootTime-startcount_rebootTime);
    Serial.println("Connecting to WiFi...");
    digitalWrite(LED_PIN, HIGH);

  Serial.println("Connected to WiFi\n");
  
  Serial.println("ip: ");
  Serial.println(WiFi.localIP());
  
  udp.begin(localPort);  
  if (val == 0x1){
    val = 0x0;
  }else{
    val = 0x1;
  }
  digitalWrite(LED_PIN, val);
}

digitalWrite(LED_PIN, HIGH);
}

void loop() {
  for (int i; i<servoAmount; i++){
    if(servos[i]->read() != servo_closed){
        servos[i]->write(servo_closed);
      };
  };

  Update_LocalTime();
  check_if_now();
  int packetSize = udp.parsePacket(); 
  if (packetSize) { 
    char incomingPacket[255]; 
    int len = udp.read(incomingPacket, 255); 
    if (len > 0) {
      incomingPacket[len] = 0; 
    }

    Serial.print("Received packet: ");
    Serial.println(incomingPacket); 

    char commandType = incomingPacket[0];
    const char* commandValue = incomingPacket + 1;  

    if (commandType == 'r') {
      Serial.print(commandValue);
      send_message("Events opdateret");
      replace_events(commandValue);
    } else if (commandType == 'g'){
      send_events();
    } else if (commandType=='i'){
      send_message("Ativerer");
      activate_servo(atoi(commandValue));
    } else {
      send_message("Unknown command");
    }
  }
}
std::string trim(const std::string& str) {

    size_t start = str.find_first_not_of(" \t");
    size_t end = str.find_last_not_of(" \t");


    if (start == std::string::npos || end == std::string::npos) {
        return "";
    }
    return str.substr(start, end - start + 1);
}

void interpret_event(std::string new_event_string) {

    Serial.print("Interpreting event: ");
    Serial.println(new_event_string.c_str());

    std::vector<std::string> event_list = splitString(new_event_string, ',');

    for (size_t i = 0; i < event_list.size(); i++) {
        Serial.print("event_list[");
        Serial.print(i);
        Serial.print("]: ");
        Serial.println(event_list[i].c_str());  
    }

    if (event_list.size() != 7) {
       for (int i = 0; i < event_list.size(); i++){
          Serial.print("Event[");
          Serial.print(std::to_string(i).c_str());
          Serial.print("]: ");
          Serial.println(event_list[i].c_str());
       };
       return;  
    }

    int year, month, day, hour, minute, servo;
    try {
        year = std::stoi(trim(event_list[1]));
        month = std::stoi(trim(event_list[2]));
        day = std::stoi(trim(event_list[3]));
        hour = std::stoi(trim(event_list[4]));
        minute = std::stoi(trim(event_list[5]));
        servo = std::stoi(trim(event_list[6]));
    } catch (const std::invalid_argument& e) {
        Serial.println("Error: Invalid number in event data.");
        return;  
    } catch (const std::out_of_range& e) {
        Serial.println("Error: Number out of range in event data.");
        return; 
    }

    event new_event = {
        event_list[0],  
        year,
        month,
        day,
        hour,
        minute,
        servo,
        new_event_string  
    };

    events.push_back(new_event);
    Serial.println("Event added successfully.");
}

void replace_events(std::string replacement) {
    events.clear();
    Serial.println("Replacing events...");
    std::vector<std::string> new_events = splitString(replacement, '|');
    for (int i = 0; i<new_events.size(); i++){
      if (new_events[i] == ""){
        new_events.erase(new_events.begin() + i);
      }
    }

    for (int i = 0; i<new_events.size(); i++){
      Serial.print("[");
      Serial.print(new_events[i].c_str());
      Serial.println(']');
    };

    Serial.print("Number of events: ");
    Serial.println(std::to_string(new_events.size()).c_str());

    for (int i = 0; i < new_events.size(); i++) {
        interpret_event(new_events[i]);
    };
}

void send_events(){
  int events_size = events.size();
  std::string message;
  for(int i=0; i<events_size ;i++){
    message += '|'+events[i].stringform+'|';
  }
  send_message(message+std::to_string(servoAmount));
}

void activate_servo(int n){
  Serial.println("activating servo");
  servos[n]->write(servo_opened);
  std::this_thread::sleep_for(std::chrono::seconds(3));
  servos[n]->write(servo_closed);
};

void check_if_now(){
    if (events.empty()){
      return;
    };
    for (auto it = events.begin(); it != events.end(); ) {
        event next_event = *it;

        if (now.year >= next_event.year && now.month >= next_event.month && now.day >= next_event.day && now.hour >= next_event.hour && now.minute > next_event.minute) {
            Serial.println(next_event.hour); 
            activate_servo(next_event.servo-1); 
            it = events.erase(it);  
        } else {
            ++it; 
        }
    }
}

void Update_LocalTime() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Failed to obtain time");
    return;
  }
  now.minute = timeinfo.tm_min;
  now.hour = timeinfo.tm_hour+1;
  now.day = timeinfo.tm_mday;
  now.month = timeinfo.tm_mon+1;
  now.year = timeinfo.tm_year + 1900;

  if(now.hour == 24){
    now.day += 1;
    now.hour = 0;
  }
}
