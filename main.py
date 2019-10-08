import sys, pygame
import pygame.camera
from pygame.locals import *
from random import randint
from pygame import gfxdraw


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
            img = pygame.transform.scale(img, self.size)

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
            if self.state[0] != 2:
                self.state[1] = self.state[0]
                self.state[0] = 2

                self.useColor = 2
                self.draw()
                
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

def swipe(btn, swiping, lastPos, mouse):
    """
    swipe(btn,swiping,lastPos,mouse): handles logic for draging a screen\n
    btn     : The button object (class Button) that will be tracked throughout the swipe\n
    swiping : A variable to determine whether. Kept track of between frames. Needs to be updated dynamicaly\n
    lastPos : the dynamic variable to keep track of distance moved between frames\n
    mouse   : the mouse Rect where the mouse is\n
    returns: swiping, lastPos, btn, x (x value of btn), moving (whether or not the screen is in a transition state)
    """
    moving = False

    x,y = btn.pos
    w,h = btn.size

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

    return swiping, lastPos, btn, x, moving

    

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
bckg = (255,255,255)
mode = 'menu'
changex = 0
swipeThreshhold = 4.44
changing = False
debug = ""

#initialize clock
clock = pygame.time.Clock()
timer = 0
dt = 0

#definition of UI componetns
#buttons
btn1 = button(getCenterPos((300,100), size), (300,100), ("images/buttons/redN.png","images/buttons/redP.png","images/buttons/redP.png"),("TOUCH", (255,255,255),50,""))\
#swipeBtns
swipeBtn1 = button((size[0]-80,0), (80,size[1]), ((255,255,0),(255,255,0),(255,128,0)), ("",(0,0,0,0), 1, ""), initSwipe)
swipe1Data = [swipeBtn1, False, 0]

font = pygame.font.SysFont("", 20)

def menu(disp):

    

    disp.fill(bckg)

    global swipeBtn1
    global swipe1Data
    global debug
    global changing
    global changex
    global mode

    a,b = swipe1Data[0].loop(click)
    w,h = swipe1Data[0].size
    
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

        debug += str(x)

        disp3.blit(disp, (x,0))
        disp = disp3


    #disp.blit(a,b)

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

    #main menu screen
    if mode == 'menu':
        display = menu(pygame.Surface(size))

    #camera screen
    elif mode == "cam":
        display = cam(pygame.Surface(size))

        font = pygame.font.SysFont("", 20)
        text = font.render(str(dblClick) + ', ' + str(click) + ', ' + str(timer), True, (255,255,255))
        display.blit(text, (0,0))

        if dblClick:
            mode = 'menu'

    debug += str(mode) + str(swipe1Data[1]) + str(swipeBtn1.pos) + str(changing) + str(size[0]/swipeThreshhold)

    text = font.render(debug, True, (0,0,0))
    display.blit(text, (0,0))
    debug = ""

    screen.blit(display, (0,0))
    pygame.display.flip() 