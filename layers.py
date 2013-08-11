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
        director.window.push_handlers(self.on_mouse_scroll)

    def update(self, dt):
        pass

    _desired_scale = 1
    def on_mouse_scroll(self, x, y, dx, dy):
        #Zooms the map.
        if dy < 0:
            if self._desired_scale < .2: return True
            self._desired_scale -= .1
        elif dy > 0:
            if self._desired_scale > 2: return True
            self._desired_scale = 0
        if dy:
            self.scroller.do(cocos.actions.ScaleTo(self._desired_scale, .1))
            return True