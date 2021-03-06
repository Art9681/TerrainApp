import xml.etree.cElementTree as ET
import random
from noise import snoise2, pnoise1
import pyglet

class MapTemplate(object):
    def __init__(self):
        super(MapTemplate, self).__init__()
        '''Generates an XML file with the resources and tilesets
        for a cocos2d rect tilemap. First pass fills the entire map
        with one specified tile type. This block should be the default ground tile.'''

        #Initialize variables.
        self.map_pixel_size_x = 5056
        self.map_pixel_size_y = 5056
        self.cell_size = 32
        self.columns = self.map_pixel_size_x/self.cell_size
        self.rows = self.map_pixel_size_y/self.cell_size
        self.col_height = self.rows/2
        self.column_height_offset = []
        self.column_height_values = []

        self.create_xml_tilemap()

    #Generates map_template.xml
    def create_xml_tilemap(self):
        self.resource = ET.Element("resource")
        self.requires = ET.SubElement(self.resource, "requires")
        self.requires.set("file", "blocks.xml")
        self.rectmap = ET.SubElement(self.resource, "rectmap")
        self.rectmap.set("id", "maptemplate")
        self.rectmap.set("tile_size", "32x32")

        #First pass for map.
        for col in range(self.columns):
            self.column = ET.SubElement(self.rectmap, "column")

            for row in range(self.rows):
                self.cell = ET.SubElement(self.column, "cell")

                #First terrain pass. Fills entire map with specified tile.
                #This tile should be the default ground tile.
                self.cell.set("tile", "dirt")

        self.tree = ET.ElementTree(self.resource)
        self.tree.write("map_template.xml")
        print "xml_template created"
        self.horizon()

    def horizon(self):
        print "Parsing map_template for horizon gen"
        '''This method divides ground and sky. It opens and parses the xml
        file generated previously.'''

        ###Begin column height noise, generates hills and valleys at horizon###
        self.hpoints = 256
        self.hspan = 15.0
        self.hoctaves = 8 #Determines variation in peaks and valleys. Lower numbers produce better results.
        self.hbase = 0 #Not sure what this does but it still changes stuff.

        for i in xrange(self.columns):
            x = float(i) * self.hspan / self.hpoints - 0.5 * self.hspan
            y = pnoise1(x + self.hbase, self.hoctaves)
            self.column_height_offset.append(y*3)
        ###End column height noise###

        #Open and parse the xml file to change cells according to noise#
        tree = ET.parse("map_template.xml")
        root = tree.getroot()

        print "Finished root parsing"

        #The counters that iterate for every column and cell.
        self.col_counter = 0
        self.cell_counter = 0

        for column in root.iter('column'):
            self.col_height = self.col_height + self.column_height_offset[self.col_counter]
            self.column_height_values.append(self.col_height-1)
            self.col_counter += 1
            self.cell_counter = 0

            for cell in column:
                self.cell_counter += 1
                if self.cell_counter > self.col_height:
                    cell.set('tile', 'air')

        tree.write("terrain.xml")
        root.clear()
        self.ground_layers()

    def ground_layers(self):
        #Open and parse the xml file to change cells according to noise#
        tree = ET.parse("terrain.xml")
        root = tree.getroot()

        #The counters that iterate for every column and cell.
        col_counter = 0
        cell_counter = 0

        for column in root.iter('column'):
            self.col_height = self.col_height + self.column_height_offset[col_counter]
            col_counter += 1
            cell_counter = 0

            for cell in column:
                cell_counter += 1
                if cell_counter < self.col_height-10 + random.randrange(-5, 5):

                    cell.set('tile', 'rock')

                if cell_counter < self.col_height-60 + random.randrange(-5, 5):
                    cell.set('tile', 'sand')

        tree.write("terrain.xml")
        root.clear()
        self.ore_deposits()

    def ore_deposits(self):
        '''Generates the ore deposits in the map using 3D Simplex noise.'''
        ##3D Ore Noise##
        #This counter is incremented every time the terrain gen loops through inserting a cell into a row.
        #Used to keep track of the last item in nData we accessed.
        noise_counter = 0

        noise_data = []
        octaves = random.randint(3, 7)
        print "Ore Octaves: %s" %octaves
        frequency = random.uniform(3.0, 7.0) * octaves
        print "Ore Noise Frequency: %s" %frequency

        for y in range(self.columns):
            for x in range (self.rows):
                noise_data.append(int(snoise2(x / frequency, y / frequency, octaves) * 127.0 + 128.0 ))

        #Open and parse the xml file to change cells according to noise#
        tree = ET.parse("terrain.xml")
        root = tree.getroot()

        #The counters that iterate for every column and cell.
        col_counter = 0
        cell_counter = 0

        for column in root.iter('column'):
            self.col_height = self.col_height + self.column_height_offset[col_counter]
            col_counter += 1
            cell_counter = 0

            for cell in column:
                cell_counter += 1
                if cell_counter < self.col_height-10:
                    if noise_data[noise_counter] >= 200:
                        cell.set('tile', 'gold')
                    elif noise_data[noise_counter] <= 50:
                            cell.set('tile', 'iron')


                noise_counter += 1

        tree.write("terrain.xml")
        root.clear()
        self.caves()

    def caves(self):
        ##3D Terrain Noise##
        #This counter is incremented every time the terrain gen loops through inserting a cell into a row.
        #Used to keep track of the last item in nData we accessed.
        noise_counter = 0

        noise_data = []
        octaves = random.randint(10, 13)
        print "Cave Octaves: %s" %octaves
        frequency = random.uniform(3.0, 7.0) * octaves
        print "Cave Noise Frequency: %s" %frequency

        for y in range(self.columns):
            for x in range (self.rows):
                noise_data.append(int(snoise2(x / frequency, y / frequency, octaves) * 127.0 + 128.0 ))

        #Open and parse the xml file to change cells according to noise#
        tree = ET.parse("terrain.xml")
        root = tree.getroot()

        #The counters that iterate for every column and cell.
        col_counter = 0
        cell_counter = 0

        for column in root.iter('column'):
            self.col_height = self.col_height + self.column_height_offset[col_counter]
            col_counter += 1
            cell_counter = 0

            for cell in column:
                cell_counter += 1
                if cell_counter < self.col_height-30 + random.randrange(-5, 5):
                    if noise_data[noise_counter] >= 128:
                        cell.set('tile', 'cave')

                noise_counter += 1

        tree.write("terrain.xml")
        root.clear()
        self.vegetation()

    def vegetation(self):
        #Open and parse the xml file to change cells according to noise#
        tree = ET.parse("terrain.xml")
        root = tree.getroot()

        #The counters that iterate for every column and cell.
        col_counter = 0
        cell_counter = 0

        for column in root.iter('column'):
            cell_counter = 0
            for cell in column:
                if cell_counter > self.column_height_values[col_counter] and cell_counter < self.column_height_values[col_counter]+1:
                    if random.randint(1, 5) == 3:
                        cell.set('tile', 'shrub')


                cell_counter += 1

            col_counter += 1

        tree.write("terrain.xml")
        root.clear()

def segment_gen(maptemplate, physics_layer):
    #Begin physics segment collider generation. (This is crazy!)
        empty_cells = []
        #Get each air cell in the map and append to cell list.
        for cell in maptemplate.find_cells(collider=False):
            empty_cells.append(cell)

        #Get the neighbor for each air cell. For each neighbor, determine its block type.
        for cell in empty_cells:
            cell_neighbors = maptemplate.get_neighbors(cell)

            top = cell_neighbors[(0, 1)]
            if top:
                if top.tile.properties['collider'] != False:
                    physics_layer.create_segment(start=(cell.position[0], cell.position[1]+32), end=((cell.position[0]+32),cell.position[1]+32))

            bottom = cell_neighbors[(0, -1)]
            if bottom:
                if bottom.tile.properties['collider'] != False:
                    physics_layer.create_segment(start=(cell.position[0], cell.position[1]), end=((cell.position[0]+32),cell.position[1]))

            right = cell_neighbors[(1, 0)]
            if right:
                if right.tile.properties['collider'] != False:
                    physics_layer.create_segment(start=(cell.position[0]+32, cell.position[1]), end=((cell.position[0]+32),cell.position[1]+32))


            left = cell_neighbors[(-1, 0)]
            if left:
                if left.tile.properties['collider'] != False:
                    physics_layer.create_segment(start=(cell.position[0], cell.position[1]), end=((cell.position[0]),cell.position[1]+32))

