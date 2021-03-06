from pyglet.gl import *
from pyglet.window import key, mouse
import cocos
import pymunk
import mapgen
import player
from math import *

class TerrainScroller(object):
    def __init__(self, director, clock):
        super(TerrainScroller, self).__init__()

        #Initialize variables.
        self.clock = clock

        self.focus_x = 5056/2 #The position x in map space that the scroller focuses on.
        self.focus_y = 5056/2 #The position x in map space that the scroller focuses on
        self.view_angle = 0 #Holds current view angle. Used for view rotation.

        self.physics_layer = PhysicsLayer(clock)
        self.terrain_layer = cocos.tiles.load('terrain.xml')['maptemplate']

        #Create some tile sprites from spritesheet.
        #Used when we need to individually create tiles
        #at run time.
        self.tiles_sprite_sheet = pyglet.resource.image('Content/Images/tiles.png')
        self.tile_image_grid = pyglet.image.ImageGrid(self.tiles_sprite_sheet, 4, 3)
        self.air_tile_texture = self.tile_image_grid[3]
        self.cave_tile_texture = self.tile_image_grid[9]

        #Run function that generates the pymunk segment colliders.
        mapgen.segment_gen(self.terrain_layer, self.physics_layer)

        #Begin Scrolling Manager.
        self.scroller = cocos.layer.ScrollingManager()
        self.scroller.transform_anchor_x = 1024/2
        self.scroller.transform_anchor_y = 1024/2
        self.scroller.add(self.terrain_layer, z=0)
        self.scroller.add(self.physics_layer, z=1)

        #Audio Code
        self.audio = cocos.audio.music.MusicControl()
        self.audio.load("Content/Audio/grassy_world.ogg")
        self.audio.play()

        #Begin Keyboard code.
        keyboard = key.KeyStateHandler()
        director.window.push_handlers(keyboard)
        director.window.push_handlers(self.on_key_press,
                                      self.on_key_release,
                                      self.on_mouse_press)

    def update(self, dt):
        self.physics_layer.update(dt)
        #self.scroller.set_focus(self.focus_x, self.focus_y)
        self.scroller.set_focus(*self.physics_layer.player.player_sprite.position)

    def cam_move(self, move):
        self.clock.schedule(move)

    def cam_stop(self, stop):
        self.clock.unschedule(stop)

    def cam_pan_up(self, dt):
        self.focus_y = self.focus_y + 2

    def cam_pan_left(self, dt):
        self.focus_x = self.focus_x - 2

    def cam_pan_down(self, dt):
        self.focus_y = self.focus_y - 2

    def cam_pan_right(self, dt):
        self.focus_x = self.focus_x + 2

    def cam_rotate_clockwise(self):
        self.physics_layer.player.player_sprite.do(cocos.actions.RotateBy(90, 1))
        self.scroller.do(cocos.actions.RotateBy(-90, 1))
        if self.view_angle != 270:
            self.view_angle += 90
        else:
            self.view_angle = 0

        self.set_gravity()

    def cam_rotate_counter_clockwise(self):
        self.physics_layer.player.player_sprite.do(cocos.actions.RotateBy(-90, 1))
        self.scroller.do(cocos.actions.RotateBy(90, 1))
        if self.view_angle != 0:
            self.view_angle -= 90
        else:
            self.view_angle = 270

        self.set_gravity()

    def set_gravity(self):
        """
        Changes the gravity direction based on the angle
        of the view.
        """
        if self.view_angle == 0:
            self.physics_layer.space.gravity = (0, -700)
        elif self.view_angle == 90:
            self.physics_layer.space.gravity = (-700, 0)
        elif self.view_angle == 180:
            self.physics_layer.space.gravity = (0, 700)
        elif self.view_angle == 270:
            self.physics_layer.space.gravity = (700, 0)

    def rotate2d(self, point, origin):
        """
        A rotation function that rotates a point around a point.
        To rotate around the origin use [0,0]
        Used when the view rotates and we need to rotate the
        mouse click position vector to be able to select objects
        at the correct location.
        """
        degrees = -self.view_angle
        x = point[0] - origin[0]
        y = point[1] - origin[1]
        newx = (x*cos(radians(degrees))) - (y*sin(radians(degrees)))
        newy = (x*sin(radians(degrees))) + (y*cos(radians(degrees)))
        newx += origin[0]
        newy += origin[1]
        new_origin = (int(newx), int(newy))
        return new_origin

    def destroy_tile(self, x, y):
        #Gets the cell's location from the scrolling manager world coordinates.
        self.cell_origin = self.scroller.pixel_from_screen(x, y)
        self.new_cell_origin = self.rotate2d(self.cell_origin, self.physics_layer.player.body.position)
        print self.new_cell_origin
        self.cell = self.terrain_layer.get_at_pixel(*self.new_cell_origin)


        #Gets the clicked cell's neighbors.
        self.neighbors = self.terrain_layer.get_neighbors(self.cell)
        top = self.neighbors[(0, 1)]
        bottom = self.neighbors[(0, -1)]
        right = self.neighbors[(1, 0)]
        left = self.neighbors[(-1, 0)]

        #Changes clicked tile to cave tile if the clicked tile is not an air tile.
        if self.cell.tile.id != "air":
            self.cell.tile = cocos.tiles.Tile(id= 'cave', properties= {'btype': 'cave', 'collider': False}, image= self.cave_tile_texture)
            #Redraws the map. Need to create function that redraws the tile only.
            self.terrain_layer.set_dirty()

        #Gets a list of pymunk objects within 16 pixels of tile center. Since tile size is 32 pixels, this will always find pymunk objects at the border of the tile, hence, the pymunk segments around it if any.
        self.near_shapes =  self.physics_layer.space.nearest_point_query((self.cell.position[0] + 16, self.cell.position[1] + 16), 16, -1, 0)

        #Check to see if pymunk object is the player, if True, ignore this object.
        for i in self.near_shapes:
            if i['shape'] == self.physics_layer.player.shape:
                pass
            else:
                #Deletes all pymunk objects from space, except the player object.
                self.physics_layer.space._remove_shape(i['shape'])

        #The following conditionals determine where to generate segments when a tile is changed to an air or cave tile.
        if top.tile.properties['collider'] != False:
                    self.physics_layer.create_segment(start=(self.cell.position[0], self.cell.position[1]+32), end=((self.cell.position[0]+32),self.cell.position[1]+32))

        if bottom.tile.properties['collider'] != False:
            self.physics_layer.create_segment(start=(self.cell.position[0], self.cell.position[1]), end=((self.cell.position[0]+32),self.cell.position[1]))

        if right.tile.properties['collider'] != False:
                    self.physics_layer.create_segment(start=(self.cell.position[0]+32, self.cell.position[1]), end=((self.cell.position[0]+32),self.cell.position[1]+32))

        if left.tile.properties['collider'] != False:
                    self.physics_layer.create_segment(start=(self.cell.position[0], self.cell.position[1]), end=((self.cell.position[0]),self.cell.position[1]+32))

    #Begin input code.
    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            self.physics_layer.player.jump(self.view_angle)

        if symbol == key.W:
            #self.cam_move(self.cam_pan_up)
            pass
        if symbol == key.A:
            #self.cam_move(self.cam_pan_left)
            self.physics_layer.player.shape.friction = 0.0
            self.physics_layer.player.walk_left(self.view_angle)
        if symbol == key.S:
            #self.cam_move(self.cam_pan_down)
            pass
        if symbol == key.D:
            #self.cam_move(self.cam_pan_right)
            self.physics_layer.player.shape.friction = 0.0
            self.physics_layer.player.walk_right(self.view_angle)
        if symbol == key.V:
            #Zooms out to view entire map layer.
            self.scroller.do(cocos.actions.ScaleTo(0.2, .1))
            #print self.terrain_layer.get_visible_cells()
        if symbol == key.E:
            self.cam_rotate_clockwise()
        if symbol == key.Q:
            self.cam_rotate_counter_clockwise()

    def on_key_release(self, symbol, modifiers):
        if symbol == key.SPACE:
            self.physics_layer.player.cancel_jump(self.view_angle)
        if symbol == key.W:
            #self.cam_stop(self.cam_pan_up)
            pass
        if symbol == key.A:
            #self.cam_stop(self.cam_pan_left)
            self.physics_layer.player.stop_left()
            self.physics_layer.player.shape.friction = 10
            self.physics_layer.player.body.velocity.x = 0
        if symbol == key.S:
            #self.cam_stop(self.cam_pan_down)
            pass
        if symbol == key.D:
            #self.cam_stop(self.cam_pan_right)
            self.physics_layer.player.stop_right()
            self.physics_layer.player.shape.friction = 10
            self.physics_layer.player.body.velocity.x = 0

    def on_mouse_press (self, x, y, buttons, modifiers):
        self.destroy_tile(x, y)

class PhysicsLayer(cocos.layer.ScrollableLayer):
    is_event_handler = True
    def __init__(self, clock):
        super( PhysicsLayer, self ).__init__()

        self.space = pymunk.Space()
        self.space.gravity = (0,-700)

        self.player = player.Player(position=(5056/2, 5056/2+200))

        self.add(self.player.player_sprite)

        self.space.add(self.player.body,
                       self.player.shape)

    def create_segment(self, start, end):
        """
        Used to generate segment colliders during mapgen or tile
        creation/destruction.
        """
        self.segment = pymunk.Segment(self.space.static_body, start, end, 1)
        self.segment.elasticity = 0.0
        self.space.add(self.segment)

    def update(self, dt):
        self.player.update()
        self.space.step(dt)