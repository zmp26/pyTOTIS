from gpiozero import LED, Button
import lcddriver
from time import *
import os

"""
pyTOTIS
python Tech Ops Toner Inventory System
"""

#declaring lcd objects
lcd = lcddriver.lcd()
#use lcd_display_string("string", num) where "string" is the string (up to 16 characters) and num is row 1 or row 2

#defining re-order thresholds for high importance (HI) and low importance (LI)
HI_THRESHOLD_QUANTITY = 2   #high importance toner re-order threshold
LI_THRESHOLD_QUANTITY = 1   #low importance toner re-order threshold

#gpio pin declarations
BLUE_LED_PIN = 17
DELIVER_BTN_PIN = 24
DEPLOY_BTN_PIN = 25

#button and led declarations
blue_led = LED(BLUE_LED_PIN)
deliver_btn = Button(DELIVER_BTN_PIN)
deploy_btn = Button(DEPLOY_BTN_PIN)

#pyTOTIS version
pyTOTIS_ver = "    ver  0.1    "

# Make a class to be able to define toner objects.
# Each toner type will have its own object from this
# class that will be responsible for holding the name,
# barcode, quantity, and whether or not it is HI or LI
class Toner:
    def __init__(self, tonername, barcode, quantity, threshold):
        self.tonername = tonername
        self.barcode = barcode
        self.quantity = quantity
        self.threshold = threshold

    def increase_quantity(self):
        self.quantity += 1

    def decrease_quantity(self):
        #returns -1 if quantity is already at 0
        #returns 1 otherwise
        if self.quantity == 0:
            return -1
        else:
            self.quantity -= 1
            return 1

    def set_threshold(self, threshold):
        #returns 1 if new threshold is allowed
        #returns -1 otherwise
        if threshold >= 0:
            self.threshold = threshold
            return 1
        else:
            return -1

    def get_threshold(self):
        #returns threshold value
        return self.threshold

    def set_barcode(self, barcode):
        self.barcode = barcode

    def get_barcode(self):
        return self.barcode

    def set_tonername(self, tonername):
        #returns 1 if successful update
        #returns -1 otherwise
        if tonername is not "":
            self.tonername = tonername
            return 1
        else:
            return -1

    def get_tonername(self):
        return self.tonername

    def get_quantity(self):
        return self.quantity

#create a list that will hold all toner objects
tonerlist = []

#loop through toners.txt and make toner objects for each line
toner_file = open("toners.txt", "r")
lines = toner_file.readlines()
toner_file.close()


for line in lines:
    new_line = line.split()
    print type(new_line[2])
    tonerlist.append(Toner(str(new_line[2]), str(new_line[0]), int(new_line[1]), HI_THRESHOLD_QUANTITY)) #defaulting all toners to HI

def pyTOTIS_startup():
    lcd.lcd_display_string("     pyTOTIS    ", 1)
    lcd.lcd_display_string(pyTOTIS_ver, 2)
    sleep(2)
    pyTOTIS_main_menu()

def pyTOTIS_main_menu():
    lcd.lcd_clear()
    lcd.lcd_display_string("     pyTOTIS    ", 1)
    lcd.lcd_display_string("Press When Ready", 2 )

def pyTOTIS_update_toners(filename, tl):
    #filename is name file to update
    #tl is tonerlist used in pyTOTIS
    os.remove("toners.txt")
    f = open(filename, "w")
    for t in tl: #iterate over all toner objects t in toner list tl
        if t == tl[-1]:
            fileline = str(t.get_barcode()) + " " + str(t.get_quantity()) + " " + str(t.get_tonername())
        else:
            fileline = str(t.get_barcode()) + " " + str(t.get_quantity()) + " " + str(t.get_tonername()) + "\n"

        f.write(fileline)
    f.close()

def pyTOTIS_toner_deliver(tl):
    temp = False
    lcd.lcd_clear()
    lcd.lcd_display_string("Scan barcode to", 1)
    lcd.lcd_display_string("add to inventory", 2)
    toner_barcode = raw_input("toner barcode: ")
    toner_barcode = toner_barcode.strip()
    lcd.lcd_clear()
    for line in tl:
        #check toner list for toner
        if line.get_barcode() == toner_barcode:
            line.increase_quantity()
            lcd.lcd_display_string("Current  Amount:", 1)
            lcd.lcd_display_string(str(line.get_quantity()), 2)
            sleep(2)
            temp = True

    if not temp:
        #tonername, barcode, quantity, threshold
        tl.append(Toner("no_name", toner_barcode, 1, HI_THRESHOLD_QUANTITY))
        lcd.lcd_display_string("no_name  created", 1)
        lcd.lcd_display_string("amend toners.txt", 2)
        sleep(2)

    #update toners.txt below
    pyTOTIS_update_toners("toners.txt", tl)

    pyTOTIS_main_menu()

def pyTOTIS_toner_deploy(tl):
    temp = False
    lcd.lcd_clear()
    lcd.lcd_display_string("Scan barcode to", 1)
    lcd.lcd_display_string("remove inventory", 2)
    toner_barcode = raw_input("toner barcode: ")
    toner_barcode = toner_barcode.strip()
    lcd.lcd_clear()
    for line in tl:
        #check toner list for toner
        if line.get_barcode() == toner_barcode:
            retval = line.decrease_quantity()
            if retval == 1: #this means that the toner was successfully found and decreased by 1
                lcd.lcd_display_string("Current  Amount:", 1)
                lcd.lcd_display_string(str(line.get_quantity()), 2)
                sleep(2)
                temp = True
    if not temp:
        #tonername, barcode, quantity, threshold
        tl.append(Toner("no_name", toner_barcode, 0, HI_THRESHOLD_QUANTITY))
        lcd.lcd_display_string("no_name  created", 1)
        lcd.lcd_display_string("amend toners.txt", 2)
        sleep(2)

    #update toners.txt below
    pyTOTIS_update_toners("toners.txt", tl)

    pyTOTIS_main_menu()


#main program control
pyTOTIS_startup()
while True:
    blue_led.on()

    if deliver_btn.is_pressed: #begin toner input process
        #next two lines for debugging purposes -> uncomment/comment as necessary
        #print("deliver button pressed")
        blue_led.off()
        pyTOTIS_toner_deliver(tonerlist)

    if deploy_btn.is_pressed: #begin toner deploy process
        #next two lines for debugging purposes -> uncomment/comment as necessary
        #print("deploy button pressed")
        blue_led.off()
        pyTOTIS_toner_deploy(tonerlist)
