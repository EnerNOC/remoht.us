/* Arduino controller code for Remoht.us
 * Author: Thom Nichols
 */
 
// uncomment if your ardunino is 3V3 TTL:
//#define TTL_3V3 1
#define HEARTBEAT 1

#ifdef TTL_3V3
#define TTL_V 3.3
#else
#define TTL_V 5.0
#endif

#define PIN_HEARTBEAT 13 // digital out
#define NUM_RELAYS 2
#define PIN_RELAY_1 2 // ditigal out
#define PIN_RELAY_2 3 // digital out
#define RELAY_DEFAULT LOW

// Note: the PIR is 'active' low so an internal pull-up is used on this pin.
#define PIN_PIR 4  // digital in 
#define PIN_LDR 0  // analog in
#define PIN_TEMP 1 // analog in

#define ANALOG_HIGH 1024

#define ALPHA 0.15 // for low-pass filter

int heartbeat = LOW;
int relayPins[] = {PIN_RELAY_1, PIN_RELAY_2};
int LEVELS[] = {LOW, HIGH};
int relayStates[] = {0 ,0};

float tempC = 40.0;
float lightPct = 1.0;
int pir = 0;

#define CMD_TERMINATOR '\n'
#define BUF_LEN 20
char cmdBuf[BUF_LEN];

void setup() {
#ifdef TTL_3V3
//  analogReference(EXTERNAL);
#endif
  pinMode(PIN_RELAY_1, OUTPUT);
  pinMode(PIN_RELAY_2, OUTPUT);
  pinMode(PIN_PIR, INPUT_PULLUP);

  resetRelays();
  Serial.begin(9600);
  while (!Serial) {}
}

// the loop routine runs over and over again forever:
void loop() {
  
  if (Serial.available() <= 1) {
    delay(100);
    readTemp(); // continuously sample
    readPIR();
    readLDR();
    heartbeat = ( heartbeat == HIGH ? LOW : HIGH );
    digitalWrite(PIN_HEARTBEAT, heartbeat);
    return;
  }
  
  digitalWrite(PIN_HEARTBEAT,HIGH);
  int bytesRead = Serial.readBytesUntil(CMD_TERMINATOR, cmdBuf, BUF_LEN);
  char cmd = cmdBuf[0];
//  Serial.write((uint8_t*)cmdBuf,bytesRead);
  
  switch ( cmd ) {
    case 'd':
      printReadings();
      break;
      
    case 'r':
      if ( bytesRead == 5 ) { // toggle relay, format is "r 1 0"
        int relayID = cmdBuf[2]-'0';
        int val = cmdBuf[4]-'0';
        setRelay(relayID, val);
      } 
      // any command that starts w/ r should show current relay states
      printRelays();
      break;
      
    default:
      Serial.print("x");
  }
  Serial.write(CMD_TERMINATOR);
  digitalWrite(PIN_HEARTBEAT,LOW);
}

void printRelays() {
  Serial.print("r ");
  for ( int i=0; i< NUM_RELAYS; i++ ) {
    Serial.print( relayStates[i] );
    if ( i+1 != NUM_RELAYS )
      Serial.print(" ");
  }
}

void printReadings() {
  Serial.print("d ");
  Serial.print( tempC );
  Serial.print(" ");
  Serial.print( lightPct );
  Serial.print(" ");
  Serial.print( pir );
}

float readTemp() {
  // see: http://learn.adafruit.com/tmp36-temperature-sensor
  float newReading = analogRead(PIN_TEMP);
  float vout = newReading * TTL_V / ANALOG_HIGH;
  float newTempC = (vout - 0.5) * 100;
//  float newTempC = newReading;
  tempC = lowPass( newTempC, tempC );
  return tempC;
}

float readLDR() {
  float ldrRaw = analogRead(PIN_LDR);
  // map to a floating point value between 0.0 and 1.0
  
  float ldrNew = float(ldrRaw) / ANALOG_HIGH;
  lightPct = lowPass(ldrNew, lightPct);
  return lightPct;
}

int readPIR() {
  pir = digitalRead(PIN_PIR);
  pir = ( pir == LOW ? 1 : 0 ); // 0 means motion detected
  // This is already smoothed by capacitors
  return pir;
}

/* Low pass filter to smooth sensor readings */
float lowPass(float newReading, float lastReading) {
  return lastReading + ALPHA * (newReading - lastReading);
}

void resetRelays() {
  for ( int i=0; i < NUM_RELAYS; i++ )
    setRelay(i, RELAY_DEFAULT);
}

void setRelay(int index, int val) {
  relayStates[index] = val;
  digitalWrite(relayPins[index], LEVELS[val]);
}


