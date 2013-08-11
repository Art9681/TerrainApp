import pyglet
import cocos
import layers

class GameScene(cocos.scene.Scene):
    def __init__(self, director):
        super(GameScene, self).__init__()

        #Create the clock and delta time variables.
        #The clock ticks 60 times a second.
        self.clock = pyglet.clock
        self.dt = 1/60

        #The layers this scene has.
        self.scroller = layers.TerrainScroller(director)

        self.add(self.scroller.scroller, z=0)

        #Begin clock tick.
        self.clock.schedule(self.scroller.update)

