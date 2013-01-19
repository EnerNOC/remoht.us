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

#define SAMPLE_DELAY 100 // milliseconds between readings
#define REPORT_THRESHOLD 2000 // don't report more frequently than every N milliseconds
#define ANALOG_CHANGE_THRESHOLD .05 // requre 5% change to report

// Note: the PIR is 'active' low so an internal pull-up is used on this pin.
#define PIN_PIR 4  // digital in 
#define PIN_LDR 0  // analog in
#define PIN_TEMP 1 // analog in

#define ANALOG_HIGH 1024

#define ALPHA 0.15 // for low-pass filter

short heartbeat = LOW;
short relayPins[] = {PIN_RELAY_1, PIN_RELAY_2};
short relayStates[] = {0,0};

#define CMD_TERMINATOR '\n'
#define BUF_LEN 20
char cmdBuf[BUF_LEN];

struct Readings {
	float tempC;
	float lightPct;
	short pir;
};

unsigned long lastReport = 0;
Readings lastVals = { 40.0, 1.0, 0 };
Readings newVals = { 40.0, 1.0, 0 };

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
    readTemp(); // continuously sample
    readPIR();
    readLDR();
    
    unsigned long now = millis();
    if ( changedVals(now) ) {
    	printReadings();
    	lastReport = now;
    	lastVals = newVals; // save last reported vals
    	newVals = (Readings){ lastVals.tempC, // initialize a 'new' set of new vals.
    		                    lastVals.lightPct,
    		                    lastVals.pir };
		}

		#if HEARTBEAT == 1
    heartbeat = ( heartbeat == HIGH ? LOW : HIGH );
    digitalWrite(PIN_HEARTBEAT, heartbeat);
		#endif
    delay( SAMPLE_DELAY );
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
      Serial.print("x"); // unknown value
  }
  digitalWrite(PIN_HEARTBEAT,LOW);
}

void printRelays() {
  Serial.print("r ");
  for ( int i=0; i< NUM_RELAYS; i++ ) {
    Serial.print( relayStates[i] );
    if ( i+1 != NUM_RELAYS )
      Serial.print(" ");
  }
  Serial.write(CMD_TERMINATOR);
}

bool changedVals(unsigned long now) {
	if ( now - lastReport < REPORT_THRESHOLD ) return false;
	bool changed = false;

	if ( newVals.pir != lastVals.pir ) return true;

	float diff = abs(newVals.lightPct - lastVals.lightPct);
	// this is already a percent
	if ( diff > ANALOG_CHANGE_THRESHOLD ) return true;

	diff = abs(newVals.tempC - lastVals.tempC);
	if ( diff / lastVals.tempC > ANALOG_CHANGE_THRESHOLD ) return true;

	return false;
}

void printReadings() {
  Serial.print("d ");
  Serial.print( newVals.tempC );
  Serial.print(" ");
  Serial.print( newVals.lightPct );
  Serial.print(" ");
  Serial.print( newVals.pir );
  Serial.write(CMD_TERMINATOR);
}

float readTemp() {
  // see: http://learn.adafruit.com/tmp36-temperature-sensor
  float newReading = analogRead(PIN_TEMP);
  float vout = newReading * TTL_V / ANALOG_HIGH;
  float newTempC = (vout - 0.5) * 100;
//  float newTempC = newReading;
  newTempC = lowPass( newTempC, newVals.tempC );
  if ( newTempC != newVals.tempC )
		newVals.tempC = newTempC;
  return newTempC;
}

float readLDR() {
  float ldrRaw = analogRead(PIN_LDR);
  // map to a floating point value between 0.0 and 1.0
  
  float ldrNew = float(ldrRaw) / ANALOG_HIGH;
  ldrNew = lowPass(ldrNew, newVals.lightPct);
  if ( ldrNew != newVals.lightPct )
		newVals.lightPct = ldrNew;
  return ldrNew;
}

int readPIR() {
  int newPir = digitalRead(PIN_PIR);
  newPir = ( newPir == LOW ? 1 : 0 ); // 0 means motion detected
	if ( newPir != newVals.pir )
		newVals.pir = newPir;
  // This is already smoothed by capacitors
  return newPir;
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
  digitalWrite(relayPins[index], val == 0 ? LOW : HIGH);
}


