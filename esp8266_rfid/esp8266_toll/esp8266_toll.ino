#include <ESP8266WiFi.h>

const char* g_ssid      = "radio";
const char* g_password  = "radio@123";
const char* g_host      = "pubsub.pubnub.com";
const char* g_pubKey    = "pub-c-913ab39c-d613-44b3-8622-2e56b8f5ea6d";
const char* g_subKey    = "sub-c-8ad89b4e-a95e-11e5-a65d-02ee2ddab7fe";
const char* g_channel   = "carIdentificanDevice-resp";

unsigned long g_startMillis;
unsigned long g_switchTimeMillis;
boolean       g_heaterInHighPhase;

/*********************************************************************************
Function Name     : setup
Description       : Initialize the Serial Communication with baud 115200, connect 
                    to the Router with SSID and PASSWORD 
Parameters        : void
Return            : void
*********************************************************************************/

void setup(void){
  Serial.begin(115200);
  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(g_ssid);
  
  WiFi.begin(g_ssid, g_password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");  
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.begin(9600);
}

/*********************************************************************************
Function Name     : loop
Description       : Publish the data to the hello_world channel using the 
                    GET Request 
Parameters        : void
Return            : void
*********************************************************************************/
void loop(void){

  WiFiClient client;
  const int l_httpPort = 80;
  if (!client.connect(g_host, l_httpPort)) {
    Serial.println("Pubnub Connection Failed");
    return;
  }
  String resp = "";
  char a[13];
  if(Serial.available()>0){
    for(int i =0; i<12;i++){
      a[i] = Serial.read(); 
      delay(10); 
      resp+=a[i];
    }
    a[12] = '\0';
  }
  char *len = a;
//DATA FORMAT : http://pubsub.pubnub.com /publish/pub-key/sub-key/signature/channel/callback/message
  if(strlen(len)==12){
    String url = "/publish/";
    url += g_pubKey;
    url += "/";
    url += g_subKey;
    url += "/0/";
    url += g_channel;
    url += "/0/";
    url += "{\"carRFIDnum\":\"";
    url += len;
    url += "\"}";
    Serial.println(url);
    
    client.print(String("GET ") + url + " HTTP/1.1\r\n" +
               "Host: " + g_host + "\r\n" + 
               "Connection: close\r\n\r\n");
    delay(10);
    
    while(client.available()){
      String line = client.readStringUntil('\r');
      Serial.print(line);
    }    
  }
  memset(a, 0, sizeof a);  
  Serial.println();
  Serial.println("Pubnub Connection Closed");
  delay(1000);
}

//End of the Program
