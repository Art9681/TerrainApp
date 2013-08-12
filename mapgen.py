import xml.etree.cElementTree as ET
import random
from noise import snoise2, pnoise1

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
        self.column_height_values = []

        self.create_xml_tilemap()
        self.horizon()
        self.caves()

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

    def horizon(self):
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
            self.column_height_values.append(y*3)
        ###End column height noise###

        #Open and parse the xml file to change cells according to noise#
        tree = ET.parse("map_template.xml")
        root = tree.getroot()

        #The counters that iterate for every column and cell.
        self.col_counter = 0
        self.cell_counter = 0

        for column in root.iter('column'):
            self.col_height = self.col_height + self.column_height_values[self.col_counter]
            self.col_counter += 1
            self.cell_counter = 0

            for cell in column:
                self.cell_counter += 1
                if self.cell_counter > self.col_height:
                    cell.set('tile', 'air')

        tree.write("terrain.xml")

    def caves(self):
        ##3D Terrain Noise##
        #This counter is incremented every time the terrain gen loops through inserting a cell into a row.
        #Used to keep track of the last item in nData we accessed.
        noise_counter = 0

        noise_data = []
        octaves = random.randint(3, 7)
        print "Cave Octaves: %s" %octaves
        frequency = random.uniform(3.0, 7.0) * octaves
        print "Cave Noise Frequency: %s" %frequency

        for y in range(self.columns):
            for x in range (self.rows):
                noise_data.append(int(snoise2(x / frequency, y / frequency, octaves) * 127.0 + 128.0 ))

        for i in noise_data:
            print i

        #Open and parse the xml file to change cells according to noise#
        tree = ET.parse("terrain.xml")
        root = tree.getroot()

        #The counters that iterate for every column and cell.
        col_counter = 0
        cell_counter = 0

        for column in root.iter('column'):
            self.col_height = self.col_height + self.column_height_values[col_counter]
            col_counter += 1
            cell_counter = 0

            for cell in column:
                cell_counter += 1
                if cell_counter < self.col_height-8:
                    cell.set('tile', 'rock' if noise_data[noise_counter] <= 128 else ('air'))

                noise_counter += 1

        tree.write("terrain.xml")







