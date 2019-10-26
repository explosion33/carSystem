import sys, pygame, os
import pygame.camera
from pygame.locals import *
from random import randint
from pygame import gfxdraw
import subprocess
import ast



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
            img = pygame.transform.smoothscale(img, self.size)

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
                    if self.args:
                        self.function(self.args)
                    else:
                        self.function()

        else:
            if self.state[0] != 0:
                self.state[1] = self.state[0]
                self.state[0] = 0

                self.useColor = 0
                self.draw()
    
    def loop(self, click,):
        if self.enabled:
            self.interact(click)
        return (self.surface, self.pos)

    def enable(self, enabled=True):
        """
        enabled(enabled=True): sets whether or not the button can be interacted with\n
        If a third image or color is provided it will be used for the disabled state\n
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
        

class toggleButton(button):
    def __init__(self, pos, size, color, text, function=None):
        button.__init__(self, pos, size, color, text, function=None, args=None)
        self.state = True
        self.oneCLick = True
        self.rect = self.surface.get_rect(topleft=self.pos)
        self.function = function

    def interact(self, click):
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
        

def getCenterPos(dimensions, screenSize):
    """
    getCenterPos(dimensions, screenSize): gets the (x,y) position in order to center an object on its screen\n
    dimensions : the (width, height) of the object\n
    screenSize : the (width, height) of the screen\n
    """
    center = (screenSize[0]/2-dimensions[0]/2,screenSize[1]/2-dimensions[1]/2)
    return center

def initSwipe():
    """
    initialize the swiping process
    """
    global swipe1Data
    swipe1Data = [swipe1Data[0] ,True, mouse.centerx]

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
        print()

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
    """
    getInfo(path): get bluetooth device info from a txt file\n
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
    info = open(path,"w").close()
    os.system("bash bin/deviceInfo.sh")
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

def disconnect():
    """
    disconenct(): disconnects the current bluetooth device
    """
    os.system("bash bin/disconnect.sh")

def readSettings():
    """
    readSettings(): reads settings.txt and returns a dictioanry
    """

    f = open("settings.txt", "r")
    p = f.read()
    out = ast.literal_eval(p)
    print(out)
    return out

#initialize pygame
pygame.init()
size = (800,480)
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)                   #visible display
display = pygame.Surface(size)                                              #working display (gets added to bisible display) (can be useful for scaling entire display)
pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))    #makes cursor invisible whilst still allowing for its functionality

#initialize pygames camera library
pygame.camera.init()
camera = pygame.camera.Camera('/dev/video0', size)
#camera.set_controls(hflip=True)
camera.start()

#create vaious variables
settings = readSettings()

mouse = pygame.Rect(0, 0, 2, 2)         #mouse rectangle for collison
click = False                           #stores state of mouse click
mode = 'menu'                           #current mode
subMenu = "main"                        #current submenu of menu mode
debug = ""                              #content to be displayed at topleft of screen
debugFont = pygame.font.SysFont("", 20) #font object for the debug text

#swipe detection variables
changex = 0
swipeThreshhold = 4.44
changing = False

#system variables
volume = 50
lastVolume = 50
deviceInfo = getInfo("bin/info.txt")            #bluetooth device info
lastDevices = getLastDevices("bin/devices.txt") #get previously connected devices
print(lastDevices)

#initialize clock
clock = pygame.time.Clock()
timers = {}
dt = 0

#definition of UI componetns
#MAINMENU
if settings["mode"] == "dark":
    location = "images/buttons/dark/"
    txtColor = (238,238,238)
    bckg = (24,30,39)
    accent = (33,62,69)
else:
    location = "images/buttons/light/"
    txtColor = (35,35,35)
    bckg = (255,255,255)
    accent = (113,113,113)


UIDevices = button((20,10), (150,60), (location + "UIBtn.png",location + "UIBtnPressed.png"),("Devices", txtColor,30,""), changeMenu, "devices")
UICamera = button((20,90), (150,60), (location + "UIBtn.png",location + "UIBtnPressed.png"),("Camera", txtColor,30,""))
UISettings = button((20,170), (150,60), (location + "UIBtn.png",location + "UIBtnPressed.png"),("Settings", txtColor,30,""))
UIBlank = button((20,250), (150,60), (location + "UIBtn.png",location + "UIBtnPressed.png"),("", txtColor,30,""))
UIBlank2 = button((20,330), (150,60), (location + "UIBtn.png",location + "UIBtnPressed.png"),("", txtColor,30,""))
UIBlank3 = button((20,410), (150,60), (location + "UIBtn.png",location + "UIBtnPressed.png"),("", txtColor,30,""))
UIButtons = [UIDevices, UICamera, UISettings, UIBlank, UIBlank2, UIBlank3]

#aduio info
audioBorder = pygame.Surface((400,460), pygame.SRCALPHA)
audioBorder.fill((0,0,0,0))
AAfilledRoundedRect(audioBorder,audioBorder.get_rect(), accent,0.05)

audioMute = toggleButton((230,420), (40,40), (location + "volumeOn.png", location + "volumeMute.png"), ("", txtColor,30,""), mute)
audioPause = toggleButton((320,140),(200,200), (location + "play.png", location + "pause.png", location + "playDisabled.png", location + "pauseDisabled.png"), ("", txtColor,30,""), play)
volumeSlider = slider((280, 420), (320, 30), (238,238,238),(location + "slide.png", location + "slidePressed.png"), [0,100], 50, chagneVolume)
AudioControls = [audioMute, audioPause, volumeSlider]

#get apropriate name to display as streaming device
deviceFont = pygame.font.SysFont("", 45)
deviceText = "No Device"
if deviceInfo["MAC"]:
    deviceText = ""
    if deviceInfo["Alias"]:
        deviceText += deviceInfo["Alias"]
    else:
        deviceText += deviceInfo["Name"]


#DEVICES
DEVBack = button((20,410), (150,60), (location + "UIBtn.png",location + "UIBtnPressed.png"),("Back", txtColor,30,""), changeMenu, "main")
DEVDisconnect = button((20,280), (150,60), (location + "UIBtn.png",location + "UIBtnPressed.png"),("Disconnect", txtColor,30,""), disconnect)
DeviceButtons = [DEVBack]


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

    disp.fill(bckg)

    #default menu display
    if subMenu == "main":
        #try to connect to devices
        if settings["autoConnect"] == "on":
            if not deviceInfo["MAC"]:
                for MAC in lastDevices:
                    cmd = "bash bin/autoConnect.sh " + MAC
                    print(cmd)
                    os.system(cmd)

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

        if not deviceInfo["MAC"]:
            for cont in AudioControls:
                cont.enable(False)
        else:
            for cont in AudioControls:
                cont.enable()

    elif subMenu == "devices":
        for btn in DeviceButtons:
            a,b = btn.loop(click)
            disp.blit(a,b)

        font = pygame.font.SysFont("", 30)

        k = pygame.font.SysFont("", 35).render("DEVICE INFO", True, txtColor)
        disp.blit(k, (10, 10))
        k = pygame.font.SysFont("", 20).render("This is the Info of the currently connected Device", True, txtColor)
        disp.blit(k, (12, 40))

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

        k = pygame.font.SysFont("", 35).render("Saved Devices", True, txtColor)
        disp.blit(k, (size[0]/2, 10))
        k = pygame.font.SysFont("", 20).render("These devices will be automaticaly conected when in range", True, txtColor)
        disp.blit(k, (size[0]/2 + 2, 40))

        a = 80
        for MAC, name in lastDevices.items():
            k = font.render(name, True, txtColor)
            disp.blit(k, (size[0]/2 + 20, a))
            a += 30


    #changing to rear-view camera
    global swipe1Data
    global changing
    global changex
    global mode

    a,b = swipe1Data[0].loop(click)
    w,h = swipe1Data[0].size
    
    if mode == "menu":
        if not changing:
            swiping, lastPos, swipeBtn1, x, moving = swipe(swipe1Data[0], swipe1Data[1], swipe1Data[2], mouse)
            swipe1Data = [swipeBtn1, swiping, lastPos]

            if x < size[0]-(size[0]/swipeThreshhold) and not click and not changing:
                changex = x
                changing = True

        if changing:
            moving = True
            changex -= 60
            x = changex
            if x < 0:
                print("Switching to cam")
                mode = "cam"
                subMenu = "main"
                b = swipe1Data[0]
                b.pos = (size[0]-swipe1Data[0].size[0], 0)
                swipe1Data = [b, False, 0]
                changing = False

        if moving:
            disp2 = cam(pygame.Surface(size))
            disp3 = pygame.Surface(size)
            disp3.blit(disp2,(0,0))

            x = -(size[0]-(x+w))
            if x > 0: x = 0

            disp3.blit(disp, (x,0))
            disp = disp3

            volumeSlider.enable(False)
            audioMute.enable(False)
            audioPause.enable(False)
            for button in UIButtons:
                button.enable(False)
        else:
            for button in UIButtons:
                button.enable()


        #disp.blit(a,b)
    else:
        for cont in AudioControls:
            cont.enable(False)

    #return final display
    return disp

def cam(disp):
    #get camera image
    disp.fill(bckg)
    disp = camera.get_image()
    cameraSize = camera.get_size()

    #if camera does not fit on the display resize it
    if cameraSize != size:
        if cameraSize[0] != size[0]:
            x = size[0]/cameraSize[0]
            y = cameraSize[1] * x
            x = size[0]
        else:
            y = size[1]/cameraSize[1]
            x = size[0] * y
            y = size[1]
        x = int(x)
        y = int(y)
        
        #rescale surface and add it to display to avoid mismatch in surface sizes
        s = pygame.Surface((x,y))
        s = pygame.transform.scale(disp,(x,y))
        disp = pygame.Surface(size)
        disp.blit(s, (0,0))
    disp = pygame.transform.flip(disp, True, False)

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

    if click:
        mouse.center = pygame.mouse.get_pos()

    if audioMute.state:
        if volume != lastVolume:
            subprocess.call(["amixer", "-D", "pulse", "sset", "Master", str(volume) + "%"])
            lastVolume = volume

    #main menu screen
    if mode == 'menu':
        display = menu(pygame.Surface(size))

        k = countTimers(dt)
    
        if "Refresh" not in list(timers.keys()):
            addTimer("Refresh", 1000)
        if "Refresh" in k:
            deviceInfo = getInfo("bin/info.txt")
            print("GOT INFO")
            deviceText = "No Device"
            if deviceInfo["MAC"]:
                deviceText = ""
                if deviceInfo["Alias"]:
                    deviceText += deviceInfo["Alias"]
                else:
                    deviceText += deviceInfo["Name"]


    #camera screen
    elif mode == "cam":
        display = cam(pygame.Surface(size))


    addDebug(dt, int(fps), timers, DEVBack.state)

    text = debugFont.render(debug, True, (0,255,0))
    display.blit(text, (0,0))
    debug = ""

    #pygame.draw.rect(display, (255,0,0,125), volumeSlider.rect)

    screen.blit(display, (0,0))
    pygame.display.flip() 