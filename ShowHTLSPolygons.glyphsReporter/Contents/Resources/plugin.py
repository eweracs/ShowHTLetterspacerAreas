# encoding: utf-8

from __future__ import division, print_function, unicode_literals
import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
import math
from AppKit import NSAffineTransform

import os
import imp
imp.load_source("HT_LetterSpacer_script", os.path.expanduser("~/Library/Application Support/Glyphs 3/Repositories/HT "
                                                             "Letterspacer/HT_LetterSpacer_script.py"))

from HT_LetterSpacer_script import *


class ShowHTLSPolygons(ReporterPlugin):

	@objc.python_method
	def settings(self):
		self.menuName = Glyphs.localize({
			"en": "HT Letterspacer Polygons",
			"de": "HT-Letterspacer-Polygone",
			"fr": "Polygons HT Letterspacer",
			})

	@objc.python_method
	def slant_layer(self, layer):
		xHeight = Glyphs.font.selectedFontMaster.xHeight
		transform = NSAffineTransform.new()
		slant = math.tan(Glyphs.font.selectedFontMaster.italicAngle * math.pi / 180.0)
		transform.shearXBy_atCenter_(slant, xHeight/2)
	
		for path in layer.paths:
			for node in path.nodes:
				node.position = transform.transformPoint_(node.position)
		
		return layer

	@objc.python_method
	def create_polygons(self, layer):
		engine = HTLetterspacerLib()
		engine.paramDepth = int(Glyphs.font.selectedFontMaster.customParameters["paramDepth"])
		engine.paramOver = int(Glyphs.font.selectedFontMaster.customParameters["paramOver"] or 0)
		engine.xHeight = Glyphs.font.selectedFontMaster.xHeight
		engine.factor = 1.0
		engine.angle = Glyphs.font.selectedFontMaster.italicAngle
		engine.upm = Glyphs.font.upm
		engine.LSB = True
		engine.RSB = True
		engine.newWidth = False
		engine.output = ""

		new_layer = GSLayer()

		decomposed_layer = layer.copyDecomposedLayer()
		decomposed_layer.parent = layer.parent

		for polygon in engine.set_space(decomposed_layer, layer):
			path = GSPath()
			for node in polygon:
				new_node = GSNode()
				new_node.type = GSLINE
				new_node.position = (node[0], node[1])
				path.nodes.append(new_node)
			path.closed = True
			new_layer.paths.append(path)

		new_layer = self.slant_layer(new_layer)
		new_layer.completeBezierPath.fill()

	@objc.python_method
	def foreground(self, layer):
		NSColor.greenColor().colorWithAlphaComponent_(0.4).set()
		self.create_polygons(layer)

	@objc.python_method
	def inactiveLayerForeground(self, layer):
		NSColor.greenColor().colorWithAlphaComponent_(0.4).set()
		self.create_polygons(layer)

	@objc.python_method
	def preview(self, layer):
		NSColor.blueColor().set()
		if layer.paths:
			layer.bezierPath.fill()
		if layer.components:
			for component in layer.components:
				component.bezierPath.fill()

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
