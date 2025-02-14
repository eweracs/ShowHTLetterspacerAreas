# encoding: utf-8

from __future__ import division, print_function, unicode_literals
import objc
from GlyphsApp import Glyphs, Message
from GlyphsApp.plugins import ReporterPlugin
import math
from AppKit import NSAffineTransform, NSBezierPath, NSColor

import_success = False
try:
	from HTLSLibrary import HTLSEngine
	import_success = True
except:
	Message(
		title="HTLS Manager required",
		message="Please install HTLS Manager from the plugin manager and restart Glyphs."
	)


class ShowHTLSAreas(ReporterPlugin):

	@objc.python_method
	def start(self):
		self.master_params = {}
		self.glyphs_last_change = {}
		self.gave_warning = False

	@objc.python_method
	def settings(self):
		self.menuName = Glyphs.localize({
			"en": "HT Letterspacer Areas",
			"de": "Flächen für HT Letterspacer",
			"fr": "Aires HT Letterspacer",
		})

	@objc.python_method
	def slant_layer(self, layer):
		x_height = Glyphs.font.selectedFontMaster.xHeight
		transform = NSAffineTransform.new()
		slant = math.tan(Glyphs.font.selectedFontMaster.italicAngle * math.pi / 180.0)
		transform.shearXBy_atCenter_(slant, x_height / 2)

		for path in layer.paths:
			for node in path.nodes:
				node.position = transform.transformPoint_(node.position)

		return layer

	@objc.python_method
	def create_polygons(self, layer):
		if not import_success:
			return
		if not layer.shapes:
			return
		if not self.gave_warning:
			if not Glyphs.font.selectedFontMaster.customParameters["paramArea"] \
				or not Glyphs.font.selectedFontMaster.customParameters["paramDepth"]:
				Message(
					title="Missing configuration",
					message="Please set up parameters in HTLS Manager. Using default values."
				)
				self.gave_warning = True
		if layer.master.id not in self.master_params:
			self.master_params[layer.master.id] = {
				"paramArea": layer.master.customParameters["paramArea"],
				"paramDepth": layer.master.customParameters["paramDepth"],
				"paramOver": layer.master.customParameters["paramOver"],
			}
		params_changed = False
		for param in ["paramArea", "paramDepth", "paramOver"]:
			if self.master_params[layer.master.id][param] != layer.master.customParameters[param]:
				params_changed = True
				self.master_params[layer.master.id] = {
					"paramArea": layer.master.customParameters["paramArea"],
					"paramDepth": layer.master.customParameters["paramDepth"],
					"paramOver": layer.master.customParameters["paramOver"],
				}

		if self.glyphs_last_change[layer.parent] != layer.parent.lastChange or not layer.tempData["polygons"] or \
			params_changed:

			htls_polygons = HTLSEngine(layer).calculate_polygons()
			if not htls_polygons:
				return

			bezierPath = NSBezierPath.new()

			for polygon in htls_polygons:
				bezierPath.moveTo_(polygon[-1])
				for node in polygon:
					bezierPath.lineTo_(node)
				bezierPath.closePath()

			NSColor.greenColor().colorWithAlphaComponent_(0.4).set()
			bezierPath.fill()
			layer.tempData["polygons"] = bezierPath
		else:
			bezierPath = layer.tempData["polygons"]

		if bezierPath:
			NSColor.greenColor().colorWithAlphaComponent_(0.4).set()
			bezierPath.fill()

	@objc.python_method
	def foreground(self, layer):
		if layer.parent not in self.glyphs_last_change:
			self.glyphs_last_change[layer.parent] = layer.parent.lastChange
		self.create_polygons(layer)

	@objc.python_method
	def inactiveLayerForeground(self, layer):
		if layer.parent not in self.glyphs_last_change:
			self.glyphs_last_change[layer.parent] = layer.parent.lastChange
		self.create_polygons(layer)

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
