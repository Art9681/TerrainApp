import pyglet
from pyglet.window import key, mouse
import cocos
import mapgen

class TerrainScroller(object):
    def __init__(self, director, clock):
        super(TerrainScroller, self).__init__()

        self.clock = clock

        self.focus_x = 5056/2 #The position x in map space that the scroller focuses on.
        self.focus_y = 5056/2 #The position x in map space that the scroller focuses on.

        self.maptemplate = cocos.tiles.load('terrain.xml')['maptemplate']


        #Begin Scrolling Manager.
        self.scroller = cocos.layer.ScrollingManager()
        self.scroller.add(self.maptemplate)

        #Begin Keyboard code.
        keyboard = key.KeyStateHandler()
        director.window.push_handlers(keyboard)
        director.window.push_handlers(self.on_key_press, self.on_key_release)

    def update(self, dt):
        self.scroller.force_focus(self.focus_x, self.focus_y)

    def cam_move(self, move):
        self.clock.schedule(move)

    def cam_stop(self, stop):
        self.clock.unschedule(stop)

    def cam_pan_up(self, dt):
        self.focus_y = self.focus_y + 1

    def cam_pan_left(self, dt):
        self.focus_x = self.focus_x - 1

    def cam_pan_down(self, dt):
        self.focus_y = self.focus_y - 1

    def cam_pan_right(self, dt):
        self.focus_x = self.focus_x + 1

    #Begin input code.
    def on_key_press(self, symbol, modifiers):
        if symbol == key.W:
            self.cam_move(self.cam_pan_up)
        if symbol == key.A:
            self.cam_move(self.cam_pan_left)
        if symbol == key.S:
            self.cam_move(self.cam_pan_down)
        if symbol == key.D:
            self.cam_move(self.cam_pan_right)
        if symbol == key.V:
            #Zooms out to view entire map layer.
            self.scroller.do(cocos.actions.ScaleTo(0.2, .1))

    def on_key_release(self, symbol, modifiers):
        if symbol == key.W:
            self.cam_stop(self.cam_pan_up)
        if symbol == key.A:
            self.cam_stop(self.cam_pan_left)
        if symbol == key.S:
            self.cam_stop(self.cam_pan_down)
        if symbol == key.D:
            self.cam_stop(self.cam_pan_right)

