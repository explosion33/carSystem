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


def cam():
    """
    changes the mode of the program to camera
    """
    global mode
    mode = 'cam'

def getCenterPos(dimensions, screenSize):
    """
    getCenterPos(dimensions, screenSize): gets the (x,y) position in order to center an object on its screen\n
    dimensions : the (width, height) of the object\n
    screenSize : the (width, height) of the screen\n
    """
    center = (screenSize[0]/2-dimensions[0]/2,screenSize[1]/2-dimensions[1]/2)
    return center


#initialize pygame
pygame.init()
size = (800,480)
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)                   #visible display
display = pygame.Surface(size)                                              #working display (gets added to bisible display) (can be useful for scaling entire display)
pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))    #makes cursor invisible whilst still allowing for its functionality

#initialize pygames camera library
pygame.camera.init()
camera = pygame.camera.Camera('/dev/video0', size)
camera.start()

#create vaious variables
mouse = pygame.Rect(0, 0, 2, 2)
click = False
bckg = (255,255,255)
mode = 'menu'

#definition of UI componetns 
btn2 = button(getCenterPos((300,100), size), (300,100), ("images/buttons/redN.png","images/buttons/redP.png","images/buttons/redP.png"),("TOUCH", (255,255,255),50,""), cam)

def menu(disp):
    a,b = btn2.loop(click)
    disp.blit(a,b)
    return disp

def cam(disp):
    #get camera image
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
        return disp

#main loop
while True:
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
            mouse.center = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            click = False

    #main menu screen
    if mode == 'menu':
        display = menu(display)
    
    #camera screen
    elif mode == "cam":
        display = cam(display)


    screen.blit(display, (0,0))
    pygame.display.flip()
    display.fill(bckg)