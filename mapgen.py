import xml.etree.cElementTree as ET
import random
from noise import snoise2, pnoise1

class MapTemplate(object):
    def __init__(self):
        super(MapTemplate, self).__init__()

        #Initialize variables.
        self.map_pixel_size_x = 1024
        self.map_pixel_size_y = 1024
        self.cell_size = 32
        self.columns = self.map_pixel_size_x/self.cell_size
        self.rows = self.map_pixel_size_y/self.cell_size
        self.col_height = self.rows/2
        self.column_height_values = []


        self.create_xml_tilemap()
        self.first_pass()



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

                #First terrain pass. Creates divide between ground and sky. Horizon.
                self.cell.set("tile", "dirt")

        self.tree = ET.ElementTree(self.resource)
        self.tree.write("map_template.xml")

    def first_pass(self):
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
        col_counter = 0
        cell_counter = 0

        print len(self.column_height_values)

        for column in root.iter('column'):

            self.col_height = self.col_height + self.column_height_values[col_counter]
            print self.column_height_values[col_counter]
            print self.col_height
            col_counter += 1
            cell_counter = 0

            for cell in column:
                cell_counter += 1
                if cell_counter > self.col_height:
                    cell.set('tile', 'air')


        '''for i in self.column_height_values:
            print i

        print len(self.column_height_values)'''
        tree.write("terrain.xml")







