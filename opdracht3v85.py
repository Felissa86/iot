# IoT programming 
# Modulecode: 31365
# Inzendcode: 31365A3
# Felissa Marlisa-Becks
# Datum: 18 augustus 2023

import socket
import ephem
import RPi.GPIO as GPIO
import time
from time import sleep
import requests
import ScanUtility
import bluetooth._bluetooth as bluez

# GPIO naamgeving
GPIO.setmode(GPIO.BCM)

# Zet GPIO waarschuwingen uit
GPIO.setwarnings(False)

# Gebruikte GPIO pin nummers - Buzzer en button zitten op dezelfde GPIO!
pinpir = 17  # input
buzzer = 12  # output
button = 12  # input
pinled = 18  # output

# GPIO pin als output
GPIO.setup(pinled, GPIO.OUT)
GPIO.setup(buzzer, GPIO.OUT)

# GPIO pin als input
GPIO.setup(pinpir, GPIO.IN)

# GPIO pin als input, er wordt gebruikt gemaakt van een pull up weerstand
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

run = True

def internet():
    "Controleert of internet aanwezig is"

    try:
        res = socket.getaddrinfo('google.nl',80)
        print ("\033[1;1;1m,\033c")
        print ("\033[1;33mInternet check\033[1;m")
        print ("Internet is aanwezig!\n")
        time.sleep(1)

        beacon()

        return True
    except:
        print ("Internet is niet aanwezig!")
        print ("Controleer de verbinding en probeer opnieuw!")
        print ("Het programma is gestopt!")
        return False

# Stel bluetooth apparaat in. Het bluetooth apparaat van de Raspberry Pi is standaard 0.
dev_id = 0

def beacon():
    "Gebruikt een beacon om te detecteren of ik thuis ben"

    x=0

    try:
            sock = bluez.hci_open_dev(dev_id)
            print ("\033[1;33mZoeken naar beacon\033[1;m")
    except:
            print ("STORING - Geen toegang tot bluetooth")

    ScanUtility.hci_enable_le_scan(sock)

    while True:
        item ["uuid"] = "e7afe3c9-63c6-4882-bd98-4cc4ca6dec76"    #Eigen beacon - Thuis
        returnedList = ScanUtility.parse_events(sock, 10)
        for item in returnedList:
            # Als aan de waarde voldaan wordt
            if item ["uuid"] == "":
                print ("\033[1;37mEr is geen beaconsignaal\033[1;33m")
                time.sleep(2)

            if item ["uuid"] == "e7afe3c9-63c6-4882-bd98-4cc4ca6dec76":
                print ("\033[1;37mIk ben thuis\033[1;33m")
                time.sleep(2)

                deurbel1()
            
            # NOT EQUAL - Als niet aan de waarde voldaan wordt
            if item ["uuid"] != "e7afe3c9-63c6-4882-bd98-4cc4ca6dec76":
                print ("\033[1;37mIk ben NIET thuis (NOT EQUAL)\n\033[1;33m")
                time.sleep(2)

                deurbel2()

            #Problemen met wachttijd beacon zoeken, tweede UUID gemaakt voor niet thuis functie
            #else:
                #item ["uuid"] == "b423f91d-bf83-4cc7-87b0-e8c0d43f7a19"
                #print ("\033[1;37mIk ben niet thuis - Vigilance mode AAN\033[1;33m")
                #print ("\033[1;37mDruk op de deurbel om verder te gaan\033[1;33m")
                #time.sleep (2)

                #deurbel2()

def deurbel1():
    "Monitort deurbel"

    print ("\033[1;1;1m,\033c")
    print ("\nDruk op deurbel 1 (button)")

    while True:
        input_state = GPIO.input(button)
        if input_state == True:
            print ("\n\033[1;33mDeurbel 1\033[1;m")
            print ("De deurbel 1 (button) is ingedrukt")
            time.sleep(0.2)

def deurbel2():    # deze functie wordt in vigilance mode gestart 
    "Monitort deurbel"

    while True:
        input_state = GPIO.input(button)
        if input_state == True:
            print ("\n\033[1;31mDeurbel 2\033[1;m")
            print ("De deurbel 2 (button) is ingedrukt")
            time.sleep(0.2)

            ifttt()

def ifttt():
    "Verstuurt een bericht naar IFTTT"

    print ("\n\033[1;33mIFTTT bericht versturen\033[1;m")
    print ("Er wordt een bericht verstuurd naar IFTTT")

    # Zorgt middels HTML post commando, dat HTML regel verstuurd wordt met unieke code naar IFTTT server
    r = requests.post('https://maker.ifttt.com/trigger/doorbell_detected1/with/key/ldCXqfeQaeJmV6ylPrGeb9myFA3gtk15zfGvLqWYP_6', params={"value1":"none","value2":"none","value3":"none"})

    print("Wacht 5 seconden om het event af te laten ronden en het volgende event kan starten")
    time.sleep(5)

    pir()

def pir():    
        "Bij beweging volgt melding op smartphone, het alarm gaat aan en lamp wordt bij nacht ingeschakeld"

        # Variabelen
        currentstate = 0
        previousstate = 0

        print ("\n\033[1;33mWacht tot de PIR klaar is...\033[1;m")

        # Loop totdat PIR output op 0 is
        while GPIO.input(pinpir) == 1:

                currentstate = 0

        print("PIR wacht op beweging")

        # Loop totdat gebruiker stopt met CTRL-C
        while True:

            # Leest PIR state
            currentstate = GPIO.input(pinpir)

            # Als de PIR is getriggered
            if currentstate == 1 and previousstate == 0:

                print(" \033[1;35mBeweging gedetecteerd!")
                print("    - Melding wordt naar smartphone verstuurd!")
                print("    - Alarm gaat af!")
                print("    - Lamp gaat aan als het nacht is en blijft uit als het dag is!\033[1;m")

                # Zorgt middels HTML post commando, dat HTML regel verstuurd wordt met unieke code naar IFTTT server
                r = requests.post('https://maker.ifttt.com/trigger/motion_detected2/with/key/ldCXqfeQaeJmV6ylPrGeb9myFA3gtk15zfGvLqWYP_6', params={"value1":"none","value2":"none","value3":"none"})
                print ("\nIFTTT  melding is verstuurd! Kijk op je telefoon of je de melding ontvangen hebt")

                # Slaat vorige status op
                previousstate = 1

                alarm()

                # Wacht 10 seconden totdat volgende loop begint
                print("Wacht 10 seconds voordat volgende event kan starten")
                time.sleep(10)

            # Als de PIR ready status heeft terug gekregen
            elif currentstate == 0 and previousstate == 1:

                print("Ready")
                previousstate = 0

            # Wacht voor 10 milliseconds
            time.sleep(0.01)

def alarm():
    "Laat buzzer 3x3 horen"

    print ("\n\033[1;33m3x3 Alarm\033[1;m")

    GPIO.setup(buzzer,GPIO.OUT)

    a=0
    b=0
    p1 = 0.1 # tijd tussen korte piepjes
    p2 = 0.5 # tijd tussen reeks piepjes

    while True:
        a=a+1
        GPIO.output(buzzer,GPIO.HIGH)
        print ("Beep")
        sleep(p1) # tijd tussen piepjes
        GPIO.output(buzzer,GPIO.LOW)
        sleep(p1)
        if a==3:
            a=0
            b=b+1
            sleep(p2)
            print ("")
            if b==3:
                b=0
                sleep(p2)

                dagnacht()

def dagnacht():
    "Bepaald dag of nacht"

    home     = ephem.Observer()
    home.lat = '51.441642' # Latitude Eindhoven
    home.lon = '5.4697225'  # Longitude Eindhoven

    next_sunrise = home.next_rising(ephem.Sun()).datetime()
    next_sunset  = home.next_setting(ephem.Sun()).datetime()

    if next_sunset < next_sunrise:
        print ("\033[1;33mDag-/nachtcheck (Ephem) : Het is dag!\033[1;m")
        print ('De lamp gaat niet aan bij alarm')
        status = ('dag')
        #status = ('nacht')   # dummy om de nacht optie te testen

        lamp(status)

    else:
        print ("\033[1;33mDag-/Nachtcheck (Ephem) : Het is nacht!\033[1;m")
        print ('De lamp gaat aan bij alarm')
        status = ('nacht')

        lamp(status)

    time.sleep(1)

def lamp(status):
   "Lamp gaat bij alarm aan als het nacht is"

   print ("\n\033[1;33mLamp\033[1;m")
   if status == ('nacht'):
       print ('Alarm! Het is nacht. Niemand thuis. Lamp is AAN\n')
       print ('\033[1;34m--------------------------------------------------------Program restart\033[1;m\n')
       GPIO.output(pinled,GPIO.HIGH)  # lamp gaat aan
       time.sleep(3)                  
       GPIO.output(pinled,GPIO.LOW)   # Hier gaat de lamp weer uit omdat je de lus 'schoon' wil starten

       internet()

   else:
       print ('Alarm! Het is dag. Niemand thuis. Lamp is UIT\n')
       print ('\033[1;34m--------------------------------------------------------Program restart\033[1;m\n')
       GPIO.output(pinled,GPIO.LOW)
       time.sleep(10)

       internet()


# ==== Hoofdprogramma ====

print ("\033[1;1;1m,\033c")

print ("LOI - IoT programming Security")
print ("==========================================")
print ("Prototype - Smart Deurbel")
print ("\nModulecode: 31365")
print ("Inzendcode: 31365A3\n")

time.sleep(5) #pauze van 5 seconden


internet()    # de functie 'internet' wordt gestart


