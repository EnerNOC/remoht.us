/* Arduino controller code for Remoht.us
 * 
 */

#define NUM_RELAYS 2
#define PIN_RELAY_1 2
#define PIN_RELAY_2 4
#define RELAY_DEFAULT LOW
int relayPins[] = {PIN_RELAY_1,PIN_RELAY_2};
int LEVELS[] = {LOW,HIGH};
int relayStates[] = {0,0};

#define CMD_TERMINATOR '\n'
#define BUF_LEN 20
char cmdBuf[BUF_LEN];

void setup() {                
  // initialize the digital pin as an output.
  pinMode(PIN_RELAY_1, OUTPUT);     
  pinMode(PIN_RELAY_2, OUTPUT);     

  resetRelays();
  Serial.begin(9600);
  while (!Serial) {}
}

// the loop routine runs over and over again forever:
void loop() {
  
  if (Serial.available() <= 1) {
    delay(100);
    return;
  }
  
  int bytesRead = Serial.readBytesUntil(CMD_TERMINATOR, cmdBuf, BUF_LEN);
  char cmd = cmdBuf[0];
//  Serial.write((uint8_t*)cmdBuf,bytesRead);
  
  switch ( cmd ) {
    case 'd': // TODO dummy
      Serial.print("d 1 2 3 4");
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
}

void printRelays() {
  Serial.print("r ");
  for ( int i=0; i< NUM_RELAYS; i++ ) {
    Serial.print( relayStates[i] );
    if ( i+1 != NUM_RELAYS )
      Serial.print(" ");
  }
}

void resetRelays() {
  for ( int i=0; i < NUM_RELAYS; i++ )
    setRelay(i, RELAY_DEFAULT);
}

void setRelay(int index, int val) {
  relayStates[index] = val;
  digitalWrite(relayPins[index], LEVELS[val]);
}


