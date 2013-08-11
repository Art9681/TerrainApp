import pyglet
from cocos.director import director
import scenes
import mapgen

# Disable error checking for increased performance
pyglet.options['debug_gl'] = False

def main():
    director.init(width=1024, height=1024, do_not_scale=True, caption = "TerrainApp", vsync = False, resizable = False)
    director.show_FPS = True
    my_scene = scenes.GameScene(director)

    # run the scene
    director.run(my_scene)

if __name__ == '__main__':
    mapgen.MapTemplate()
    main()