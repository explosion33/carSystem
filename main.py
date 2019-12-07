import sys, pygame, os
from pygame.locals import *
from random import randint
from pygame import gfxdraw
import subprocess
import ast
from multiprocessing import Process

cvInstalled = False
try:
    import cv2
    cvInstalled = True
except:
    print("cv2 not found Camera will not be initialized")
import numpy as np


class button (object):
    """
    button(pos,size,color,text): a button class, pretty self explanatory\n
    pos      : (x,y)\n
    size     : (w,h)\n
    color    : (normal, click, disabled(optional)) can be (r,g,b) or a path to an image\n
    text     : (content, color, size, font)\n
    function : def (no paranthesis when passing it through)
    args     : arguments for function, functions arguments must be list, dict, or single arg
    """
    def __init__(self, pos, size, color, text, function=None, args=None):
        self.pos = pos
        self.size = size
        self.text = text
        self.color = color
        self.function = function
        self.args = args
        self.useColor = 0
        self.state = [1,0] #current state, last state
        self.enabled = True
        self.mode = "color"

        if type(self.color[0]) == str:
            self.mode = "image"


        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)
        self.draw()

    def AAfilledRoundedRect(self, surface,rect,color,radius=0.4):

        """
        AAfilledRoundedRect(surface,rect,color,radius=0.4): draws a rounded, antialiased, rectangle\n

        surface : destination\n
        rect    : rectangle\n
        color   : rgb or rgba\n
        radius  : 0 <= radius <= 1
        """

        rect         = pygame.Rect(rect)
        color        = pygame.Color(*color)
        alpha        = color.a
        color.a      = 0
        pos          = rect.topleft
        rect.topleft = 0,0
        rectangle    = pygame.Surface(rect.size,pygame.SRCALPHA)

        circle       = pygame.Surface([min(rect.size)*3]*2,pygame.SRCALPHA)
        pygame.draw.ellipse(circle,(0,0,0),circle.get_rect(),0)
        circle       = pygame.transform.smoothscale(circle,[int(min(rect.size)*radius)]*2)

        radius              = rectangle.blit(circle,(0,0))
        radius.bottomright  = rect.bottomright
        rectangle.blit(circle,radius)
        radius.topright     = rect.topright
        rectangle.blit(circle,radius)
        radius.bottomleft   = rect.bottomleft
        rectangle.blit(circle,radius)

        rectangle.fill((0,0,0),rect.inflate(-radius.w,0))
        rectangle.fill((0,0,0),rect.inflate(0,-radius.h))

        rectangle.fill(color,special_flags=pygame.BLEND_RGBA_MAX)
        rectangle.fill((255,255,255,alpha),special_flags=pygame.BLEND_RGBA_MIN)
        
        return surface.blit(rectangle,pos)

    def renderText(self, surface, content, color, size, font):
        """
        text(surface,content,color,size,font): renders the text for the button\n
            content : text to be displayed\n
            color   : color of text\n
            size    : font size\n
            font    : font type (empty is default font)\n
        """
        font = pygame.font.SysFont(font, size)
        text = font.render(content, True, color)
        
        r1 = self.surface.get_rect()
        r2 = text.get_rect()

        r2.center = r1.center
        self.surface.blit(text, r2)

    def draw(self):
        """
        draw(): draws button background and text onto self.surface
        """
        self.surface = self.surface.convert_alpha()
        self.surface.convert_alpha()
        if self.mode == "color":
            rect = pygame.Rect((0,0), self.size,)
            self.AAfilledRoundedRect(self.surface, rect, self.color[self.useColor])
        elif self.mode == "image":
            self.surface.fill((0,0,0,0))
            
            p = self.useColor
            if not self.enabled:
                if len(self.color) == 3:
                    p = 2
                elif len(self.color) == 4:
                    if self.state == False:
                        p=3
                    else:
                        p=2

            img = pygame.image.load(self.color[p])
            img = pygame.transform.smoothscale(img, (int(self.size[0]), int(self.size[1])))

            self.surface.blit(img, (0,0))
        
        self.renderText(self.surface, self.text[0], self.text[1], self.text[2], self.text[3])

    def interact(self, click):
        """
        interact(click): handles texture changes and function calling for the button\n
        click : boolean denoting weather or not the mousebutton is currently down
        """
        mouse = pygame.Rect(0, 0, 2, 2)
        xm, ym = pygame.mouse.get_pos()
        mouse.center = (xm,ym)

        rect = self.surface.get_rect(topleft=self.pos)
        if rect.colliderect(mouse) and click:
            if self.state[0] != 1:
                self.state[1] = self.state[0]
                self.state[0] = 1

                self.useColor = 1
                self.draw()
                
                print(self.function, self.args)
                if self.function:
                    if self.args is not None:
                        self.function(self.args)
                    else:
                        self.function()

        else:
            if self.state[0] != 0:
                self.state[1] = self.state[0]
                self.state[0] = 0

                self.useColor = 0
                self.draw()
    
    def loop(self, click):
        """
        loop(self, click): should be called once per loop\n
        click : boolean containing info on weather or not mousedown is true\n
        returns : (self.surface, self.pos)
        """
        if self.enabled:
            self.interact(click)
        return (self.surface, self.pos)

    def enable(self, en=True):
        """
        enable(en=True): sets whether or not the button can be interacted with\n
        If a third image or color is provided it will be used for the disabled state\n
        en : whether or not the button is enabled (True = enabled, False = Disabled)
        """
        if en:
            if not self.enabled:
                self.enabled = True
                self.useColor = 0
                print("drew",self.text[0], str(self.function), "button")
                self.draw()
        else:
            if self.enabled:
                self.enabled = False

                if len(self.color) >=3:
                    self.useColor = 2

                print("drew, not enabled", self.text[0], str(self.function), "button")
                self.draw()
        

class toggleButton(button):
    def __init__(self, pos, size, color, text, function=None):
        """
        toggleButton(pos,size,color,text): a toggle button class, pretty self explanatory\n
        pos      : (x,y)\n
        size     : (w,h)\n
        color    : (normal, click, disabled(optional)) can be (r,g,b) or a path to an image\n
        text     : (content, color, size, font)\n
        function : def (no paranthesis when passing it through)
        """

        button.__init__(self, pos, size, color, text, function=None, args=None)
        self.state = True
        self.oneCLick = True
        self.rect = self.surface.get_rect(topleft=self.pos)
        self.function = function

    def interact(self, click):
        """
        interact(click): handles texture changes and function calling for the button\n
        click : boolean denoting weather or not the mousebutton is currently down
        """
        mouse = pygame.Rect(0, 0, 2, 2)
        xm, ym = pygame.mouse.get_pos()
        mouse.center = (xm,ym)

        #rect = self.surface.get_rect(topleft=self.pos)

        if mouse.colliderect(self.rect) and click:
            if self.oneClick:
                self.oneClick = False
                if self.state:
                    self.state = False
                    self.useColor = 1
                else:
                    self.state = True
                    self.useColor = 0
                self.draw()
                
                if self.function:
                    self.function(self.state)
        if not click:
            self.oneClick = True
    
    def enable(self, enabled=True):
        """
        enabled(enabled=True): sets whether or not the button can be interacted with\n
        If a third or fourth image or color is provided it will be used for the disabled state\n
        enabled : whether or not the button is enabled (True = enabled, False = Disabled)
        """
        if enabled:
            if not self.enabled:
                self.enabled = True
                self.draw()
        else:
            if self.enabled:
                self.enabled = False
                self.draw()


class slider(object):
    """
        slider(pos, size, barColor, ballImage, maxMin, start function): creates a slider input and calls a function on slider update with the value as an argument\n
        pos       : position on screen (x,y)\n
        size      : (w,h)\n
        barColor  : color of bar where the ball will slide (r,g,b) or (r,g,b,a)\n
        ballImage : directory of picture of the slider (normal, pressed)\n
        maxMin    : maximum and minum values of the slider [min, max] (is inclusive)\n
        start     : the starting value of the slider, int between min and max\n
        function  : function to be called when the slider is updated\n
        """
    def __init__(self, pos, size, barColor, ballImage, maxMin, start=0, function=None):
        self.pos = pos
        self.size = size
        self.ballImage = ballImage
        self.use = 0
        self.min = maxMin[0]
        self.max = maxMin[1]
        self.function = function
        self.enabled = True
        self.firstTouch = None
        self.value = self.min
        self.percent = 0
        
        print(start)
        if start <= self.max and start >= self.min:
            k = start - self.min
            k = float(k)/(self.max-self.min)
            k = k * (self.size[0]-self.size[1])
            self.xoffset = k
        else:
            self.xoffset = 0

        self.bar = pygame.Surface((self.size[0]-10, self.size[1]/2))
        self.AAfilledRoundedRect(self.bar,self.bar.get_rect(),barColor, radius=0.05)

        self.surface = pygame.Surface(self.size)
        self.draw()

        img = pygame.image.load(self.ballImage[self.use])
        img = pygame.transform.smoothscale(img, (self.size[1], self.size[1]))
        self.rect = img.get_rect()

    def AAfilledRoundedRect(self,surface,rect,color,radius=0.4):

        """
        AAfilledRoundedRect(surface,rect,color,radius=0.4): draws a rounded, antialiased, rectangle\n

        surface : destination\n
        rect    : rectangle\n
        color   : rgb or rgba\n
        radius  : 0 <= radius <= 1
        """

        rect         = pygame.Rect(rect)
        color        = pygame.Color(*color)
        alpha        = color.a
        color.a      = 0
        pos          = rect.topleft
        rect.topleft = 0,0
        rectangle    = pygame.Surface(rect.size,pygame.SRCALPHA)

        circle       = pygame.Surface([min(rect.size)*3]*2,pygame.SRCALPHA)
        pygame.draw.ellipse(circle,(0,0,0),circle.get_rect(),0)
        circle       = pygame.transform.smoothscale(circle,[int(min(rect.size)*radius)]*2)

        radius              = rectangle.blit(circle,(0,0))
        radius.bottomright  = rect.bottomright
        rectangle.blit(circle,radius)
        radius.topright     = rect.topright
        rectangle.blit(circle,radius)
        radius.bottomleft   = rect.bottomleft
        rectangle.blit(circle,radius)

        rectangle.fill((0,0,0),rect.inflate(-radius.w,0))
        rectangle.fill((0,0,0),rect.inflate(0,-radius.h))

        rectangle.fill(color,special_flags=pygame.BLEND_RGBA_MAX)
        rectangle.fill((255,255,255,alpha),special_flags=pygame.BLEND_RGBA_MIN)
        
        return surface.blit(rectangle,pos)

    def draw(self):
        """
        draw(): draws button background and text onto self.surface
        """
        self.surface = self.surface.convert_alpha()
        self.surface.convert_alpha()

        self.surface.fill((0,0,0,0))
        img = pygame.image.load(self.ballImage[self.use])
        img = pygame.transform.smoothscale(img, (self.size[1], self.size[1]))

        self.surface.blit(self.bar, (5, self.size[1]/4))
        self.surface.blit(img, (self.xoffset,0))

    def interact(self, click):
        """
        interact(click): handles texture changes and function calling for the button\n
        click : boolean denoting weather or not the mousebutton is currently down
        """
        mouse = pygame.Rect(0, 0, 2, 2)
        xm, ym = pygame.mouse.get_pos()
        mouse.center = (xm,ym)

        self.rect.topleft = (self.pos[0] + self.xoffset, self.pos[1])

        if self.rect.colliderect(mouse) and click:
            self.use = 1
            if self.firstTouch == None:
                self.firstTouch = (xm - self.pos[0]) - self.xoffset
            
        if not click:
            self.use = 0
            self.firstTouch = None

        
        if self.firstTouch:
            self.xoffset = xm - self.pos[0] - self.firstTouch
            if self.xoffset < 0:
                self.xoffset = 0
            elif self.xoffset > self.size[0]-self.size[1]:
                self.xoffset = self.size[0]-self.size[1]
            self.draw()

            p = float(self.xoffset)/(self.size[0]-self.size[1])
            self.value = p * (self.max-self.min)
            self.value += self.min
            self.value = int(self.value)
            self.percent = int(p*100)
            
            self.function(self.value)  
    
    def loop(self, click):
        """
        loop(self, click): should be called once per loop\n
        click : boolean containing info on weather or not mousedown is true\n
        returns : (self.surface, self.pos)
        """
        if self.enabled:
            self.interact(click)

        return (self.surface, self.pos)

    def enable(self, enabled=True):
        """
        enabled(enabled=True): sets weather or not the slider can be interacted with\n
        If a third image or color is provided it will be used for the disabled state\n
        enabled : whether or not the slider is enabled (True = enabled, False = Disabled)
        """
        if enabled:
            if not self.enabled:
                self.enabled = True
                self.draw()
        else:
            if self.enabled:
                self.enabled = False
                self.draw()
        

def initSwipe():
    """
    initialize the swiping process
    """
    global swipe1Data
    swipe1Data = [swipe1Data[0] ,True, mouse.centerx]
    print(swipe1Data)

def initSwipe2():
    """
    initialize the swiping process for the second swiping button
    """
    global swipe2Data
    swipe2Data = [swipe2Data[0] ,True, mouse.centerx]

def AAfilledRoundedRect(surface,rect,color,radius=0.4):

        """
        AAfilledRoundedRect(surface,rect,color,radius=0.4): draws a rounded, antialiased, rectangle\n

        surface : destination\n
        rect    : rectangle\n
        color   : rgb or rgba\n
        radius  : 0 <= radius <= 1
        """

        rect         = pygame.Rect(rect)
        color        = pygame.Color(*color)
        alpha        = color.a
        color.a      = 0
        pos          = rect.topleft
        rect.topleft = 0,0
        rectangle    = pygame.Surface(rect.size,pygame.SRCALPHA)

        circle       = pygame.Surface([min(rect.size)*3]*2,pygame.SRCALPHA)
        pygame.draw.ellipse(circle,(0,0,0),circle.get_rect(),0)
        circle       = pygame.transform.smoothscale(circle,[int(min(rect.size)*radius)]*2)

        radius              = rectangle.blit(circle,(0,0))
        radius.bottomright  = rect.bottomright
        rectangle.blit(circle,radius)
        radius.topright     = rect.topright
        rectangle.blit(circle,radius)
        radius.bottomleft   = rect.bottomleft
        rectangle.blit(circle,radius)

        rectangle.fill((0,0,0),rect.inflate(-radius.w,0))
        rectangle.fill((0,0,0),rect.inflate(0,-radius.h))

        rectangle.fill(color,special_flags=pygame.BLEND_RGBA_MAX)
        rectangle.fill((255,255,255,alpha),special_flags=pygame.BLEND_RGBA_MIN)
        
        return surface.blit(rectangle,pos)

def swipe(btn, swiping, lastPos, mouse, direction="left"):
    """
    swipe(btn,swiping,lastPos,mouse): handles logic for draging a screen\n
    btn       : The button object (class Button) that will be tracked throughout the swipe\n
    swiping   : A variable to determine whether. Kept track of between frames. Needs to be updated dynamicaly\n
    lastPos   : the dynamic variable to keep track of distance moved between frames\n
    mouse     : the mouse Rect where the mouse is\n
    returns   : swiping, lastPos, btn, x (x value of btn), moving (whether or not the screen is in a transition state)
    direction : determines the direction the swipe will be moving
    """
    moving = False

    x,y = btn.pos
    w,h = btn.size
    if direction == "left":
        if swiping:
            print("swiping")
            moving = True
            tx = mouse.center[0]

            btn.pos = (x + tx-lastPos, 0)
            lastPos = tx

            if x + w > size[0]:
                btn.pos = (size[0]- w, 0)

            if not click:
                swiping = False
                lastPos = 0

        elif x + w != size[0]:
            moving = True
            amntFromZ = -(x + w - size[0])
            chng = amntFromZ/5
            if chng < 1: chng = 1
            btn.pos = (x+chng, 0)

            if amntFromZ < 1:
                btn.pos = (size[0] - w, 0)

    elif direction == "right":
        if swiping:
            moving = True
            tx = mouse.center[0]

            btn.pos = (x + tx-lastPos, 0)
            lastPos = tx

            if x < 0:
                btn.pos = (0, 0)

            if not click:
                swiping = False
                lastPos = 0

        elif x != 0:
            moving = True
            amntFromZ = x
            chng = amntFromZ/5
            if chng < 1: chng = 1
            btn.pos = (x-chng, 0)

            if amntFromZ < 1:
                btn.pos = (0, 0)


    return swiping, lastPos, btn, x, moving

def mute(cond):
    """
    mute(cond)\n
    cond : True or False (True is not mute and False is Mute)
    """
    global volume
    s = str(volume) + "%"
    if cond:
        subprocess.call(["amixer", "-D", "pulse", "sset", "Master", s])
    else:
        subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "0%"])

def chagneVolume(value):
    """
    changeVolume(value)\n
    value : integer between 0 and 100
    """
    global volume
    volume = value

def play(state):
    """
    play(state)\n
    state : True or False (True is Play and False is Pause)
    """
    global deviceInfo
    device = deviceInfo["MAC"]
    if state: #pause
        os.system("dbus-send --system --print-reply --dest=org.bluez /org/bluez/hci0/dev_" + device +  " org.bluez.MediaControl1.Pause")
    else:
        os.system("dbus-send --system --print-reply --dest=org.bluez /org/bluez/hci0/dev_" + device + " org.bluez.MediaControl1.Play")

def addDebug(*args):
    """
    addDebug(*args): create a string of debug information\n
    *args : a string or strings\n
    returns a comma seperated string
    """
    global debug
    for i in args:
        debug += str(i)
        debug += ", "

def getInfo(path):
	os.system("bluetoothctl << EOF >" + path)
	os.system("info")
	os.system("exit")
	os.system("EOF")

def readInfo(path):
    """
    readInfo(path): get bluetooth device info from a txt file\n
    path : a path to a text file\n
    returns dictionary with ["MAC", "Name", "Alias", "Icon", "Paired", "Trusted"]
    """
    out = {
        "MAC": None,
        "Name": None,
        "Alias": None,
        "Icon": None,
        "Paired": None,
        "Trusted": None,
    }
    keys = list(out.keys())

    info = open(path, "r")
    for line in info:
        if "Device" in line:
            x = line[7:24]
            x = x.replace(":", "_")
            out["MAC"] = x

        else:
            for key in keys:
                if key in line:
                    l = len(key) + 3
                    c = 0
                    for i in line:
                        if i == "\\":
                           break
                        c += 1
                    c -= 1
                    out[key] = line[l:c] 
                    
    info.close()
    return out

def getLastDevices(path):
    """
    getLastDevices(path): reads and parses previously paired devices from txt file\n
    path : str, path to the .txt file containing the info\n
    returns dict {MAC_ADRESS: Name}
    """
    out = {}
    info = open(path,"w").close()
    os.system("bash bin/lastDevices.sh")
    info = open(path, "r")

    for line in info:
        if "Device" in line:
            key = line[7:24]
            p = 0
            for i in line:
                if i == "\\":
                    break
                p += 1
            name = line[25:p-1]
            out[key] = name
    return out

def addTimer(name, ms):
    """
    addTimer(name,ms): adds a timer to be tracked\n
    name : str, name of timer. Using an already existing name will update the timer with a new time\n
    ms   : int, the number of milliseconds the timer will be active for (1000ms = 1s)
    """
    global timers
    timers[name] = ms

def countTimers(dt):
    """
    countTimers(dt): counts down all timers\n
    dt : the time in millseconds between tick
    returns a list of any finished timers
    """
    global timers
    endTimers = []
    for key, value in timers.items():
        timers[key] = value - dt
        if timers[key] <= 0:
            endTimers.append(key)
    for key in endTimers:
        del timers[key]
    return endTimers

def changeMenu(submenu):
    """"
    changeMenu(submenu): changes the submenu\n
    submenu : string
    """
    global subMenu
    subMenu = submenu
    print("changing", submenu)

def disconenctDevice():
    """
    disconenctDevice(): disconnects the current bluetooth device
    """
    os.system("bluetoothctl << EOF")
    os.system("disconnect")
    os.system("exit")
    os.system("EOF")

def disconnect():
	"""
	disconnect(): function to create a sub process to remove the device \n
	calls disconnectDevice()
	"""
	
	p = Process(target=disconenctDevice)
	p.start()

def readSettings():
    """
    readSettings(): reads settings.txt and returns a dictioanry
    """

    f = open("settings.txt", "r")
    p = f.read()
    out = ast.literal_eval(p)
    print(out)
    return out

def applySettings():
    """
    applySettings(): writes the states of the buttons on the settings menu to settings.txt
    """
    global settChecks
    global settings

    titles = ["autoConnect", "darkMode", "debug", "record", "full", "flip"]
    states = []
    for i in settChecks:
        states.append(i.state)

    out = {}
    for i in range(len(titles)):
        out[titles[i]] = states[i] 

    f = open("settings.txt", "w")
    f.write(str(out))
    settings = out
    

def beginPair():
    """
    begin the pairing process
    """

    global pairing
    global pairStatus
    global prePairDevices
    if not pairing:
        pairing = True
        pairStatus = """Now Discoverable, Look for "Car Speakers" on your device """
        prePairDevices = getLastDevices("bin/devices.txt")
        os.system("sudo hciconfig hci0 piscan")
    else:
        pairing = False
        pairStatus = ""
        os.system("sudo hciconfig hci0 noscan")

def removeDevice(MAC):
    """
    removeDevice(MAC): un-pairs a bluetooth device
    MAC : bluetooth mac adress of device ("XX:XX:XX:XX:XX:XX")
    """

    global lastDevices
    global removeButtons

    os.system("sudo bash bin/removeDevice.sh " + MAC)
    lastDevices = getLastDevices("bin/devices.txt")
    removeButtons = makeRemoveButtons()

def makeRemoveButtons(devices=None):
    """
    makeRemoveButtons(devices=None): creates a list of buttons that remove the device for each device\n
    devices : optional list that replaces the global lastDevices\n
    returns: list of buttons
    """
    if not devices:
        global lastDevices
        devices = lastDevices
    out = []
    a = 80
    k = pygame.font.SysFont("", 40).render("name", True, (0,0,0))
    w,h = k.get_size()

    for MAC, name in devices.items():

        remBtn = button((size[0]-5-h,a), (h,h), ("images/buttons/dark/delete.png", "images/buttons/dark/deletePressed.png"), ("", (0,0,0,0), 1, ""), removeDevice, MAC)
        out.append(remBtn)

        a += 50
    return out

def skip(cond):
    """
    skip(cond): skips or backtracks audio\n
    cond : True or False (True = skip)
    """

    global deviceInfo
    device = deviceInfo["MAC"]

    if cond: #skip
        os.system("dbus-send --system --print-reply --dest=org.bluez /org/bluez/hci0/dev_" + device +  " org.bluez.MediaControl1.Next")
    else:
        os.system("dbus-send --system --print-reply --dest=org.bluez /org/bluez/hci0/dev_" + device + " org.bluez.MediaControl1.Previous")

def reboot():
    """
    reboot(): reboots the system
    """
    os.system("sudo reboot")

def connect(MAC):
	"""
	conenct(MAC): connects via bluetooth to the specified MAC address
	MAC : A MAC address (AA:BB:CC:DD:EE:FF)
	"""
	
	os.system("bluetoothctl << EOF")
	os.system("connect " + MAC)
	os.system("exit")
	os.system(EOF)
	print("process done, attempted to conenct to: " + MAC)

#Update camera driver
os.system("sudo rmmod uvcvideo")
os.system("sudo modprobe uvcvideo nodrop=1 timout=6000 quirks=640")


settings = readSettings()               #seetings dictionary

#initialize pygame
pygame.init()
size = (800,480)
if settings["full"]:
	screen = pygame.display.set_mode(size, pygame.FULLSCREEN)                 #visible display
else:
	screen = pygame.display.set_mode(size)                 										#visible display
	
display = pygame.Surface(size)                                              #working display (gets added to visible display) (can be useful for scaling entire display)
pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))    #makes cursor invisible whilst still allowing for its functionality

#initialize opencv camera
if cvInstalled:
    cap = cv2.VideoCapture(0)

    if (cap.isOpened() == False):
	    print("unable to read camera feed")
	


#create vaious variables

mouse = pygame.Rect(0, 0, 2, 2)         #mouse rectangle for collison
click = False                           #stores state of mouse click
mode = 'menu'                           #current mode
subMenu = "main"                        #current submenu of menu mode
debug = ""                              #content to be displayed at topleft of screen
debugFont = pygame.font.SysFont("", 20) #font object for the debug text
recordedImgs = []

addDebug(size)

#Pairing variables
pairing = False
pairStatus = ""
prePairDevices = getLastDevices("bin/devices.txt")

#swipe detection variables
changex = 0
swipeThreshhold = 4.44
changing = False

#system variables
volume = 50
lastVolume = 50                                 #used to determine if the volume needs to be updated
deviceInfo = readInfo("bin/info.txt")            #bluetooth device info
lastDevices = getLastDevices("bin/devices.txt") #get previously paired devices

#initialize clock
clock = pygame.time.Clock()
timers = {}
dt = 0                          #time between loop

print("creating UI components")

#definition of UI componetns
if settings["darkMode"]:  #determine what images to use (light/dark)
    location = "images/buttons/dark/"
    txtColor = (238,238,238)
    bckg = (24,30,39)
    accent = (33,62,69)
else:
    location = "images/buttons/light/"
    txtColor = (35,35,35)
    bckg = (255,255,255)
    accent = (113,113,113)


backBtn = button((20,410), (150,60), (location + "UIBtn.png",location + "UIBtnPressed.png", location + "UIBtnDisabled.png"),("Back", txtColor,30,""), changeMenu, "main") #Universal back button from sub menu

#MAINMENU
UIDevices = button((20,10), (150,60), (location + "UIBtn.png",location + "UIBtnPressed.png", location + "UIBtnDisabled.png"),("Devices", txtColor,30,""), changeMenu, "devices")
UIPair = button((20,90), (150,60), (location + "UIBtn.png",location + "UIBtnPressed.png", location + "UIBtnDisabled.png"),("Pair", txtColor,30,""), changeMenu, "pair")
UICamera = button((20,170), (150,60), (location + "UIBtn.png",location + "UIBtnPressed.png", location + "UIBtnDisabled.png"),("Camera", txtColor,30,""))
UISettings = button((20,250), (150,60), (location + "UIBtn.png",location + "UIBtnPressed.png", location + "UIBtnDisabled.png"),("Settings", txtColor,30,""), changeMenu, "settings")
UIBlank2 = button((20,330), (150,60), (location + "UIBtn.png",location + "UIBtnPressed.png", location + "UIBtnDisabled.png"),("", txtColor,30,""))
UIBlank3 = button((20,410), (150,60), (location + "UIBtn.png",location + "UIBtnPressed.png", location + "UIBtnDisabled.png"),("", txtColor,30,""))
UIButtons = [UIDevices, UICamera, UISettings, UIPair, UIBlank2, UIBlank3]

#aduio info
audioBorder = pygame.Surface((400,460), pygame.SRCALPHA)
audioBorder.fill((0,0,0,0))
AAfilledRoundedRect(audioBorder,audioBorder.get_rect(), accent,0.05)

audioMute = toggleButton((230,420), (40,40), (location + "volumeOn.png", location + "volumeMute.png"), ("", txtColor,30,""), mute)
audioPause = toggleButton((335,155),(170,170), (location + "play.png", location + "pause.png", location + "playDisabled.png", location + "pauseDisabled.png"), ("", txtColor,30,""), play)
audioForward = button((520,203), (75,75), (location + "forward.png",location + "forwardPressed.png"),("", txtColor,30,""), skip, True)
audioBackward = button((245,203), (75,75), (location + "back.png",location + "backPressed.png"),("", txtColor,30,""), skip, False)
volumeSlider = slider((280, 420), (320, 30), (238,238,238),(location + "slide.png", location + "slidePressed.png"), [0,100], 50, chagneVolume)
AudioControls = [audioMute, audioPause, volumeSlider, audioForward, audioBackward]

#get apropriate name to display as streaming device
deviceFont = pygame.font.SysFont("", 45)
deviceText = "No Device"
if deviceInfo["MAC"]:
    deviceText = ""
    if deviceInfo["Alias"]:
        deviceText += deviceInfo["Alias"]
    else:
        deviceText += deviceInfo["Name"]


#DEVICES menu

DEVDisconnect = button((20,280), (150,60), (location + "UIBtn.png",location + "UIBtnPressed.png"),("Disconnect", txtColor,30,""), disconnect)
removeButtons = makeRemoveButtons()
DeviceButtons = [backBtn]

#PAIR menu
PAIRStart = button((size[0]/2 - size[0]/4,size[1]/2 - size[1]/4), (size[0]/2,size[1]/2), (bckg,bckg),("START PAIR", txtColor,70,""),beginPair)
PairButtons = [backBtn, PAIRStart]

#Settings menu
switchSettings = True

SETTAutoConnect = toggleButton((485,30), (35,35), (location + "check.png", location + "uncheck.png"),("", txtColor, 7, ""))
SETTDarkMode = toggleButton((485,80), (35,35), (location + "check.png", location + "uncheck.png"),("", txtColor, 7, ""))
SETTDebug = toggleButton((485,130), (35,35), (location + "check.png", location + "uncheck.png"),("", txtColor, 7, ""))
SETTRecord = toggleButton((485,180), (35,35), (location + "check.png", location + "uncheck.png"),("", txtColor, 7, ""))
SETTFull = toggleButton((485,230), (35,35), (location + "check.png", location + "uncheck.png"),("", txtColor, 7, ""))
SETTFlip = toggleButton((485,280), (35,35), (location + "check.png", location + "uncheck.png"),("", txtColor, 7, ""))

SETTApply = button((20,330), (150,60), (location + "UIBtn.png",location + "UIBtnPressed.png", location + "UIBtnDisabled.png"),("Apply", txtColor,30,""), applySettings)
SETTReboot = button((190, 410), (150,60), (location + "UIBtnRed.png",location + "UIBtnRedPressed.png", location + "UIBtnDisabled.png"),("Reboot", txtColor,30,""), reboot)
settButtons = [backBtn, SETTApply, SETTReboot]
settChecks = [SETTAutoConnect, SETTDarkMode, SETTDebug, SETTRecord, SETTFull, SETTFlip]


#swipeBtns
swipeBtn1 = button((size[0]-80,0), (80,size[1]), ((255,255,0),(255,255,0),(255,128,0)), ("",(0,0,0,0), 1, ""), initSwipe)
swipe1Data = [swipeBtn1, False, 0]

swipeBtn2 = button((0,0), (80,size[1]), ((255,255,0),(255,255,0),(255,128,0)), ("",(0,0,0,0), 1, ""), initSwipe2)
swipe2Data = [swipeBtn2, False, 0]

def menu(disp):
    """
    menu(disp): creates a surface with the display for the menu, handles touch detection for menu
    disp : empty pygame display
    returns pygame display
    """

    global deviceInfo
    
    #Main Menu Vars
    global UIButtons
    global audioBorder
    global AudioControls
    global deviceFont
    global deviceText
    global subMenu
    global lastDevices
    global textColor
    global settings

    #Devices vars
    global DeviceButtons
    global DEVDisconnect
    global removeButtons

    #Pair vars
    global UIPair
    global PairButtons
    global pairing
    global pairStatus
    global prePairDevices

    #settings Vars
    global settButtons
    global settChecks
    global switchSettings
    

    disp.fill(bckg)

    #default menu display
    if subMenu == "main":
        switchSettings = True

        #audio options box
        disp.blit(audioBorder, (220,10))

        #audio controls
        for cont in AudioControls:
            a,b = cont.loop(click)
            disp.blit(a,b)

        #misc. Left buttons (primaraly to change between submenus)
        for btn in UIButtons:
            a,b = btn.loop(click)
            disp.blit(a,b)

        #Name of the current connected device
        playerInfo = deviceFont.render(deviceText, True, txtColor)
        s = playerInfo.get_size()[0]

        #if width of text is bigger than aduio panel remove a letters and add ...
        while s > 380:
            c = 1
            if "..." in deviceText: c = 4
            deviceText = deviceText[0:len(deviceText)-c]
            deviceText += "..."
            s = playerInfo.get_size()[0]
        x = 420 - (s/2)
        disp.blit(playerInfo, (x,20))

        #disable audio controls if there is no conencted device
        if not deviceInfo["MAC"]:
            for cont in AudioControls:
                if cont.enabled:
                    cont.enable(False)
            if not UIPair.enabled:
                print("enabling pair")
                UIPair.enable()

        else:
            for cont in AudioControls:
                if not cont.enabled:
                    cont.enable()
            if UIPair.enabled:
                print("disabling pair")
                UIPair.enable(False)

    #devices menu display
    elif subMenu == "devices":
        #display all buttons
        for btn in DeviceButtons:
            a,b = btn.loop(click)
            disp.blit(a,b)

        #main font
        font = pygame.font.SysFont("", 30)

        # Title + subtitle for device info
        k = pygame.font.SysFont("", 35).render("DEVICE INFO", True, txtColor)
        disp.blit(k, (10, 10))
        k = pygame.font.SysFont("", 20).render("This is the Info of the currently connected Device", True, txtColor)
        disp.blit(k, (12, 40))

        # if there is a device list info
        if deviceInfo["MAC"]:
            a,b = DEVDisconnect.loop(click)
            disp.blit(a,b)

            data = deviceInfo

            a = 0
            wmax=0
            for key in list(data.keys()):
                k = font.render(key, True, txtColor)
                disp.blit(k, (20, 80+a))
                a += 30
                w,h = k.get_size()
                if w > wmax: wmax = w
            wmax += 30
            a=0
            for key in list(data.keys()):
                k = font.render(": " + str(data[key]), True, txtColor)
                disp.blit(k, (wmax+10, 80+a))
                a += 30

        else:
            data = "No Connected Devices"
            k = font.render(data, True, txtColor)
            disp.blit(k, (20,80))

        #Title + subTitle for previously paired devices 
        k = pygame.font.SysFont("", 35).render("Paired Devices", True, txtColor)
        disp.blit(k, (size[0]/2, 10))
        k = pygame.font.SysFont("", 20).render("These devices will be automaticaly conected when in range", True, txtColor)
        disp.blit(k, (size[0]/2 + 2, 40))

        #list all previously paired devices
        a = 80
        for MAC, name in lastDevices.items():
            k = pygame.font.SysFont("", 40).render(name, True, txtColor)
            disp.blit(k, (size[0]/2 + 20, a))

            a += 50

        #display buttons to remove each device
        for btn in removeButtons:
            a,b = btn.loop(click)
            disp.blit(a,b)

    #pair menu display
    elif subMenu == "pair":
        #display pairing menu buttons
        for btn in PairButtons:
            a,b = btn.loop(click)
            disp.blit(a,b)

        #if pairing mode is activated (clicked start pair button)
        addDebug(PAIRStart.text, pairing)

        if pairing:
            if PAIRStart.text[0] == "START PAIR":
                PAIRStart.text = ("STOP PAIR", PAIRStart.text[1], PAIRStart.text[2], PAIRStart.text[3],)
                PAIRStart.draw()
            #start displaying pairing status text
            k = pygame.font.SysFont("", 35).render(pairStatus, True, txtColor)
            w,h = k.get_size()
            disp.blit(k, (size[0]/2 - w/2, 50))

            #get currnet devices and compare it to old devices to see if a new device was added
            lst = getLastDevices("bin/devices.txt")
            for device in lst:
                if device not in prePairDevices:
                    pairStatus = "pairing to " + lst[device]
                    os.system("sudo bash bin/trustDevice.sh " + str(device))    #trust the new device
                    p = Process(target=connect, args=(str(device),))
                    p.start()
                    os.system("sudo hciconfig hci0 noscan")                     #disable discoverable mode

                    lastDevices = lst                                           #re register device list
                    removeButtons = makeRemoveButtons()                         #re register remove device buttons

                    subMenu = "main"
        else:
            if PAIRStart.text[0] == "STOP PAIR":
                PAIRStart.text = ("START PAIR", PAIRStart.text[1], PAIRStart.text[2], PAIRStart.text[3],)
                PAIRStart.draw()

    #settings menu display
    elif subMenu == "settings":
        if switchSettings:
            switchSettings = False
            states = []
            for key, item in settings.items():
                states.append(item)
            print("states", states)
            for i in range(len(settChecks)):
                settChecks[i].state = states[i]
                if states[i]:
                    settChecks[i].useColor = 0
                else:
                    settChecks[i].useColor = 1

                settChecks[i].draw()

        for btn in settButtons:
            a,b = btn.loop(click)
            disp.blit(a,b)

        for btn in settChecks:
            a,b = btn.loop(click)
            disp.blit(a,b)

        font = pygame.font.SysFont("", 30)

        descriptions = [
            "Auto connect to paired devices when in range:",
            "Enable Dark Mode:",
            "Enable Debug Status Text:",
            "Enable Recording from the webcam:",
            "Enable Full Screen Mode (Recommended):",
            "Flip Camera Images horizantaly:",
                        ]

        a = 30
        for i in descriptions:
            k = font.render(i, True, txtColor)
            disp.blit(k, (30, a))
            a += 50
            
        k = pygame.font.SysFont("", 20).render("V1.0, Made by Ethan Armstrong", True, txtColor)
        w,h = k.get_size()
        w += 10
        h += 10
        disp.blit(k, (size[0]-w, size[1]-h))
        

    #if not in the pairing menu disable pair mode and pair status text
    if subMenu != "pair":
        if pairing:
            pairing = False
            pairStatus = "" 
            os.system("sudo hciconfig hci0 noscan")

    #changing to rear-view camera
    global swipe1Data
    global changing
    global changex
    global mode

    a,b = swipe1Data[0].loop(click)
    w,h = swipe1Data[0].size
    
    if mode == "menu":
        #if not undergoing the auto slide process to switch to camera
        if not changing:
            swiping, lastPos, swipeBtn1, x, moving = swipe(swipe1Data[0], swipe1Data[1], swipe1Data[2], mouse)
            swipe1Data = [swipeBtn1, swiping, lastPos]

            #if swiped past threshold begin auto swipe
            if x < size[0]-(size[0]/swipeThreshhold) and not click and not changing:
                changex = x
                changing = True

        #auto swiping
        if changing:
            moving = True
            changex -= 60
            x = changex

            #if menu is compleyely off screen switch to camera mode and reset vars
            if x < 0:
                print("Switching to cam")
                mode = "cam"
                subMenu = "main"
                b = swipe1Data[0]
                b.pos = (size[0]-swipe1Data[0].size[0], 0)
                swipe1Data = [b, False, 0]
                changing = False

        #if the user is swiping add one screen onto the other
        if moving:
            print("moving")
            disp2 = cam(pygame.Surface(size))
            print("got cam")
            disp3 = pygame.Surface(size)
            disp3.blit(disp2,(0,0))

            x = -(size[0]-(x+w))
            if x > 0: x = 0

            disp3.blit(disp, (x,0))
            disp = disp3


            for btn in UIButtons:
                if btn.enabled:
                    btn.enable(False)
            for cont in AudioControls:
                if cont.enabled:
                    cont.enable(False)
            print("enabled buttons")
        else:
            for btn in UIButtons:
                if not btn.enabled:
                    if btn.text[0] != "Pair":            
                        btn.enable()

    else: #if the mode is not menu disable the audio controls so they dont accidently get pressed
        for cont in AudioControls:
            if cont.enabled:
                cont.enable(False)
        for btn in UIButtons:
            if btn.enabled:
                    btn.enable(False)


    #return final display
    return disp

def cam(disp):
    #get camera image
    if cvInstalled:
        ret, frame = cap.read()
        
        if ret == True:  	
            disp = pygame.image.frombuffer(frame.tostring(), frame.shape[1::-1], "RGB")
        
        
        if settings["flip"]:
            disp = pygame.transform.flip(disp, True, False)
        
    #SWIPE HANDLING SAME AS MENU
    global swipe2Data
    global changing
    global changex
    global mode

    a,b = swipe2Data[0].loop(click)
    w,h = swipe2Data[0].size
    
    if mode == "cam":
        if not changing:
            swiping, lastPos, swipeBtn1, x, moving = swipe(swipe2Data[0], swipe2Data[1], swipe2Data[2], mouse, "right")
            swipe2Data = [swipeBtn1, swiping, lastPos]

            if x > (size[0]/swipeThreshhold) and not click and not changing:
                changex = x
                changing = True

        if changing:
            moving = True
            changex += 60
            x = changex
            if x > size[0]-w:
                print("Switching to menu")
                mode = "menu"
                b = swipe2Data[0]
                b.pos = (0, 0)
                swipe2Data = [b, False, 0]
                b = (0,0)
                changing = False

        if moving:
            disp2 = menu(pygame.Surface(size))
            disp3 = pygame.Surface(size)
            disp3.blit(disp,(0,0))

            if x < 0: x = 0

            disp3.blit(disp2, (x-size[0],0))
            disp = disp3

        
        #disp.blit(a,b)

    return disp

#main loop

print("beginning")
while True:
    dt = clock.tick()
    fps = clock.get_fps()

    #gets game events
    for event in pygame.event.get():
        #exit handlers
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            sys.exit()
        #detect mouse press (pygame.mouse.get_pressed does not work with touch screen devices)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            click = True

        elif event.type == pygame.MOUSEBUTTONUP:
            click = False

    #if there is a click update the mouse rectangle (simulates touch)
    if click:
        mouse.center = pygame.mouse.get_pos()

    #if volume doesnt ewual last volume change it
    if audioMute.state:
        if volume != lastVolume:
            subprocess.call(["amixer", "-D", "pulse", "sset", "Master", str(volume) + "%"])
            lastVolume = volume

    #main menu screen
    if mode == 'menu':

        display = menu(pygame.Surface(size))

        k = countTimers(dt)
    
        #if refresh timer has finished refresh device variables
        if "Refresh" not in list(timers.keys()):
            addTimer("Refresh", 2500)
        if "Refresh" in k:
            deviceInfo = readInfo("bin/info.txt")

            print("GOT INFO")
            deviceText = "No Device"
            if deviceInfo["MAC"]:
                deviceText = ""
                if deviceInfo["Alias"]:
                    deviceText += str(deviceInfo["Alias"])
                else:
                    deviceText += str(deviceInfo["Name"])
        if "getDevices" not in list(timers.keys()):
        	addTimer("getDevices", 500)
        if "getDevices" in k:
        	p = Process(target=getInfo, args=("bin/info.txt",))
        	p.start()

        #try to connect to devices (auto connect)
        if settings["autoConnect"]:
            if not deviceInfo["MAC"]:
                #if refresh timer has finished refresh device variables
                if "connect" not in list(timers.keys()):
                    addTimer("connect", 1000)
                if "connect" in k:
                    for MAC in lastDevices:
                        p = Process(target=connect, args=(MAC,))
                        p.start()


    #camera screen
    elif mode == "cam":
        display= cam(pygame.Surface(size))

    #render debug text
    addDebug(dt, int(fps), timers, mode)

    if settings["debug"]:
        text = debugFont.render(debug, True, (0,255,0))
        display.blit(text, (0,0))
    debug = ""

    #pygame.draw.rect(display, (255,0,0,125), volumeSlider.rect)

    screen.blit(display, (0,0))
    pygame.display.flip() 
