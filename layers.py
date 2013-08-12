import pyglet
from pyglet.window import key, mouse
import cocos
import mapgen

class TerrainScroller(object):
    def __init__(self, director):
        super(TerrainScroller, self).__init__()

        self.maptemplate = cocos.tiles.load('terrain.xml')['maptemplate']


        #Begin Scrolling Manager.
        self.scroller = cocos.layer.ScrollingManager()
        self.scroller.add(self.maptemplate)

        #Begin Keyboard code.
        keyboard = key.KeyStateHandler()
        director.window.push_handlers(keyboard)
        director.window.push_handlers(self.on_key_press)

    def update(self, dt):
        pass

    #Begin input code.
    def on_key_press(self, symbol, modifiers):
        if symbol == key.V:
            #Zooms out to view entire map layer.
            self.scroller.do(cocos.actions.ScaleTo(0.2, .1))

