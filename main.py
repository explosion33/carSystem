import sys, pygame, os
import pygame.camera
from pygame.locals import *
from random import randint
from pygame import gfxdraw
import subprocess



class button (object):
    """
    button(pos,size,color,text): a button class, pretty self explanatory\n
    pos      : (x,y)\n
    size     : (w,h)\n
    color    : (normal, hover, click) can be (r,g,b) or a path to an image\n
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
        self.state = [0,0] #current state, last state
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
            img = pygame.image.load(self.color[self.useColor])
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
                
                if self.function:
                    if self.args:
                        self.function(args)
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

        
        

def getCenterPos(dimensions, screenSize):
    """
    getCenterPos(dimensions, screenSize): gets the (x,y) position in order to center an object on its screen\n
    dimensions : the (width, height) of the object\n
    screenSize : the (width, height) of the screen\n
    """
    center = (screenSize[0]/2-dimensions[0]/2,screenSize[1]/2-dimensions[1]/2)
    return center

def initSwipe():
    global swipe1Data
    swipe1Data = [swipe1Data[0] ,True, mouse.centerx]

def initSwipe2():
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
    global volume
    s = str(volume) + "%"
    if cond:
        call(["amixer", "-D", "pulse", "sset", "Master", s])
    else:
        call(["amixer", "-D", "pulse", "sset", "Master", "0%"])

def chagneVolume(value):
    global volume
    volume = value

def play(state):
    global deviceInfo
    device = deviceInfo["MAC"]
    if state: #play
        os.system("dbus-send --system --print-reply --dest=org.bluez /org/bluez/hci0/dev_" + device +  " org.bluez.MediaControl1.Play")
    else:
        os.system("dbus-send --system --print-reply --dest=org.bluez /org/bluez/hci0/dev_" + device + " org.bluez.MediaControl1.Pause")
        print()

def addDebug(*args):
    global debug
    for i in args:
        debug += i
        debug += ", "

def getInfo(path):
    out = {
        "MAC": None,
        "Name": None,
        "Alias": None,
        "Icon": None,
        "Paired": None,
        "Trusted": None,
    }
    keys = list(out.keys())
    info = open(path,"rw")
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
mouse = pygame.Rect(0, 0, 2, 2)
click = False
dblClick = False
bckg = (24,30,39)
mode = 'menu'
subMenu = "main"
changex = 0
swipeThreshhold = 4.44
changing = False
debug = ""
volume = 50
lastVolume = 50
deviceInfo = getInfo("bin/info.txt")

#initialize clock
clock = pygame.time.Clock()
timer = 0
dt = 0



#definition of UI componetns
font = pygame.font.SysFont("", 20)

#buttons
txtColor = (238,238,238)
UIDevices = button((20,10), (150,60), ("images/buttons/UIBtn.png","images/buttons/UIBtnPressed.png"),("Devices", txtColor,30,""))
UICamera = button((20,90), (150,60), ("images/buttons/UIBtn.png","images/buttons/UIBtnPressed.png"),("Camera", txtColor,30,""))
UISettings = button((20,170), (150,60), ("images/buttons/UIBtn.png","images/buttons/UIBtnPressed.png"),("Settings", txtColor,30,""))
UIBlank = button((20,250), (150,60), ("images/buttons/UIBtn.png","images/buttons/UIBtnPressed.png"),("", txtColor,30,""))
UIBlank2 = button((20,330), (150,60), ("images/buttons/UIBtn.png","images/buttons/UIBtnPressed.png"),("", txtColor,30,""))
UIBlank3 = button((20,410), (150,60), ("images/buttons/UIBtn.png","images/buttons/UIBtnPressed.png"),("", txtColor,30,""))
UIButtons = [UIDevices, UICamera, UISettings, UIBlank, UIBlank2, UIBlank3]

#aduio info
audioBorder = pygame.Surface((400,460), pygame.SRCALPHA)
audioBorder.fill((0,0,0,0))
AAfilledRoundedRect(audioBorder,audioBorder.get_rect(),(33,62,69),0.05)

audioMute = toggleButton((230,420), (40,40), ("images/buttons/volumeOn.png", "images/buttons/volumeMute.png"), ("", txtColor,30,""), mute)
audioPause = toggleButton((320,140),(200,200), ("images/buttons/play.png", "images/buttons/pause.png"), ("", txtColor,30,""), play)
volumeSlider = slider((280, 420), (320, 30), (238,238,238),("images/buttons/slide.png", "images/buttons/slidePressed.png"), [0,100], 50, chagneVolume)

playerInfo = 

#swipeBtns
swipeBtn1 = button((size[0]-80,0), (80,size[1]), ((255,255,0),(255,255,0),(255,128,0)), ("",(0,0,0,0), 1, ""), initSwipe)
swipe1Data = [swipeBtn1, False, 0]

swipeBtn2 = button((0,0), (80,size[1]), ((255,255,0),(255,255,0),(255,128,0)), ("",(0,0,0,0), 1, ""), initSwipe2)
swipe2Data = [swipeBtn2, False, 0]


def menu(disp):
    global UIButtons
    global audioBorder
    global audioMute
    global volumeSlider
    global audioPause
    
    #default menu display
    disp.fill(bckg)

    disp.blit(audioBorder, (220,10))

    a,b = audioMute.loop(click)
    disp.blit(a,b)

    a,b = volumeSlider.loop(click)
    disp.blit(a,b)

    a,b = audioPause.loop(click)
    disp.blit(a,b)
    
    for btn in UIButtons:
        a,b = btn.loop(click)
        disp.blit(a,b)

    

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


        #disp.blit(a,b)


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
    dt = 0.1#clock.tick() / 1000
    if timer != 0:
        timer += dt
        if timer >= 0.7:
            timer = 0
            dblClick = False

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

            if timer == 0:
                timer = 0.001
            elif timer < 0.7:
                dblClick = True

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

    #camera screen
    elif mode == "cam":
        display = cam(pygame.Surface(size))

        font = pygame.font.SysFont("", 20)
        text = font.render(str(dblClick) + ', ' + str(click) + ', ' + str(timer), True, (255,255,255))
        display.blit(text, (0,0))


    addDebug(str(volume), str(volumeSlider.xoffset), str(volumeSlider.value) + str(audioPause.state))

    text = font.render(debug, True, (0,255,0))
    display.blit(text, (0,0))
    debug = ""

    #pygame.draw.rect(display, (255,0,0,125), volumeSlider.rect)

    screen.blit(display, (0,0))
    pygame.display.flip() 