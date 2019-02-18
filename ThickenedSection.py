import FreeCAD as App
import FreeCADGui
import FreeCAD
import Part
import logging,sys
import array
from FreeCAD import Base
from FreeCAD import Gui
import traceback

def isWireSingleArcOrCircle(wx):
	isCircle = False
	if len(wx.Edges) == 1:
		ex = wx.Edges[0]
		isCircle = issubclass(type(ex.Curve),Part.Circle)
	return isCircle


def offsetClosedWire(wx,dist,sym):
	"""Offsets a closed wire returning a face"""
	if sym:
		logging.debug('closed wire sym:')
		#work around OCC bug with single wire which is an arc
		if isWireSingleArcOrCircle(wx):
			ex = wx.Edges[0]
			c1 = Part.Circle()
			c1.Center = ex.centerOfCurvatureAt(0.0)
			c1.Axis = ex.Curve.Axis
			c1.Radius = ex.Curve.Radius - dist.Value/2
			logging.debug('c1.Radius = ' + str(c1.Radius))
			off1 = Part.Wire([c1.toShape()])
			c2 = Part.Circle()
			c2.Center = ex.centerOfCurvatureAt(0.0)
			c2.Axis = ex.Curve.Axis
			c2.Radius = ex.Curve.Radius + dist.Value/2
			logging.debug('c2.Radius = ' + str(c2.Radius))
			off2 = Part.Wire([c2.toShape()])
		else:
			off1 = wx.makeOffset2D(-dist/2,fill=False,openResult=False,intersection=True,join=2)
			off2=  wx.makeOffset2D(dist/2,fill=False,openResult=False,intersection=True,join=2)
		resultFace = Part.makeFace(Part.makeCompound([off1,off2]),'Part::FaceMakerCheese')
	else:
		logging.debug('closed wire non-sym:')
		if isWireSingleArcOrCircle(wx):
			ex = wx.Edges[0]
			c1 = Part.Circle()
			c1.Center = ex.centerOfCurvatureAt(0.0)
			c1.Axis = ex.Curve.Axis
			c1.Radius = ex.Curve.Radius 
			logging.debug('c1.Radius = ' + str(c1.Radius))
			off1 = Part.Wire([c1.toShape()])
			c2 = Part.Circle()
			c2.Center = ex.centerOfCurvatureAt(0.0)
			c2.Axis = ex.Curve.Axis
			c2.Radius = ex.Curve.Radius + dist.Value
			logging.debug('c2.Radius = ' + str(c2.Radius))
			off2 = Part.Wire([c2.toShape()])
			resultFace = Part.makeFace(Part.makeCompound([off1,off2]),'Part::FaceMakerCheese')
		else:
			resultFace = wx.makeOffset2D(dist,fill=True,openResult=False,intersection=True,join=2)
	return resultFace



def offsetOpenWire(wx,dist,sym,normal):
	"""Offsets an open wire returning a face"""
	resultFace = None
	try:
		if sym:
			logging.debug('open wire sym...')
			if isWireSingleArcOrCircle(wx):
				logging.debug('...Wire is a single arc')
				ex = wx.Edges[0]
				#construct outside offset of arc as an edge, and list of edges
				c1 = Part.Circle()
				c1.Center = ex.centerOfCurvatureAt(ex.FirstParameter)
				c1.Axis = ex.Curve.Axis
				c1.Radius = ex.Curve.Radius + dist.Value/2
				ax1 = Part.Arc(c1,ex.FirstParameter, ex.LastParameter)
				baseEdge = ax1.toShape()
				base = Part.Wire([baseEdge])
				#construct inside offset of arc
				c2 = Part.Circle()
				c2.Center = ex.centerOfCurvatureAt(ex.FirstParameter)
				c2.Axis = ex.Curve.Axis
				c2.Radius = ex.Curve.Radius - dist.Value/2
				ax2 = Part.Arc(c2,ex.FirstParameter, ex.LastParameter)
				offEdge = ax2.toShape()
				offset = Part.Wire([offEdge])
				#get the connector points
				p1 = baseEdge.firstVertex().Point
				p2 = baseEdge.lastVertex().Point
				p3 = offEdge.lastVertex().Point
				p4 = offEdge.firstVertex().Point
			else:
				base = wx.makeOffset2D(-dist/2,fill=False,openResult=True,intersection=True,join=2)
				offset = wx.makeOffset2D(dist/2,fill=False,openResult=True,intersection=True,join=2)
			logging.debug('getting sorting baseEdges...')
			baseEdges = Part.__sortEdges__(base.Edges)
			logging.debug('getting sorting offset edges...')
			offEdges = Part.__sortEdges__(offset.Edges)
			p1 = baseEdges[0].Vertexes[0].Point
			p2 = baseEdges[len(baseEdges)-1].Vertexes[1].Point
			p3 = offEdges[len(offEdges)-1].Vertexes[1].Point	
			p4 = offEdges[0].Vertexes[0].Point
		else:	
			logging.debug('...open wire non-sym')
			if isWireSingleArcOrCircle(wx):
				logging.debug('...Wire is a single arc')
				ex = wx.Edges[0]
				base = wx
				c2 = Part.Circle()
				c2.Center = ex.centerOfCurvatureAt(0.0)
				c2.Axis = ex.Curve.Axis
				c2.Radius = ex.Curve.Radius + dist.Value
				ax = Part.Arc(c2,ex.FirstParameter, ex.LastParameter)
				offEdge = ax.toShape()
				offset = Part.Wire([offEdge])
				p1 = ex.firstVertex().Point
				p2 = ex.lastVertex().Point
				p3 = offEdge.lastVertex().Point
				p4 = offEdge.firstVertex().Point

			else:
				resultFace = wx.makeOffset2D(dist,fill=True,openResult=True,intersection=True,join=2)
			
#in the case of a straight line wire, makeOffset2D will fail. In that case construct the shape
	except:
		traceback.print_exc()
		logging.debug('-->exception caught')
		wireEdges = Part.__sortEdges__(wx.Edges)
		p1 = wireEdges[0].Vertexes[0].Point
		p2 = wireEdges[len(wireEdges)-1].Vertexes[1].Point
		vWire = p2 - p1
		vWire.normalize()
		offdir = normal.cross(vWire)
		offdir.multiply(dist)
		if sym:
			p1 = p1 - offdir * 0.5
			p2 = p2 - offdir * 0.5
		p4 = p1 + offdir
		p3 = p2 + offdir
		base = Part.makeLine(p1,p2)
		offset = Part.makeLine(p3,p4)
	if resultFace is None:
		logging.debug('building face...')
		end1 = Part.makeLine(p2,p3)	
		end2 = Part.makeLine(p4,p1)	
		bndyEdges = base.Edges + [end1] + offset.Edges + [end2]
		bndyEdges = Part.__sortEdges__(bndyEdges)
		faceWire = Part.Wire(bndyEdges)
		resultFace = Part.Face(faceWire)
	return resultFace



def updateThickenedSection(obj,theSketch,thickness,sides) :
	"""Create a cross section surface from a sketch"""
#get the normal to the sketch
	logging.debug('-->updateThickenedSection()')
	mx = theSketch.Placement.toMatrix()
	normal = FreeCAD.Vector(mx.A31,mx.A32,mx.A33)
	normal.normalize()


#construct faces and put them in a list
	faces = []

	sideIdx = 0
	lastSide = 0

#loop through the wires
	logging.debug('number of wires = '+ str(len(theSketch.Shape.Wires)))
	for wx in theSketch.Shape.Wires :
		logging.debug('wire ' + str(sideIdx) + " length = " + str(wx.Length) + " closed = " + str(wx.isClosed()))
#determine symmetry and offset distance from arguments
		sym = False
		dist = thickness

#determine the side by reading the argument in the list of side specifications
#if there is a list supplied use it wire by wire. If we run out of values, keep using the last one
		if sideIdx >= len(sides):
			side = sides[lastSide]
		else:
			side = sides[sideIdx]
			lastSide = side
	
		sideIdx += 1

		if side < 0:
			dist = -dist
		elif side == 0:
			sym = True
#if  treat open and closed same
		resultFace = None
		base = None
		offset = None
		if wx.isClosed():
			resultFace = offsetClosedWire(wx,dist,sym)
		else:
			resultFace = offsetOpenWire(wx,dist,sym,normal)


		logging.debug('appending face  area = ' + str(resultFace.Area))
		faces.append(resultFace)

	sx = Part.makeShell(faces)
	obj.Shape = sx
	
	
	
	#	sktch = FreeCAD.ActiveDocument.getObjectsByLabel('Sketch')[0]
	#	try:
	#		test = FreeCAD.ActiveDocument.getObjectsByLabel('Test_2')[0]
	#	except:
	#		test =  FreeCAD.ActiveDocument.addObject("Part::Feature","Test_2")			
	#	
	#	updateThickenedSection(test,sktch,4.0,[1,1,-1,0])
	
	
			
class ThickenedSection:

	
	def __init__(self , obj , sketch):
		logging.basicConfig(stream=sys.stderr, level= logging.DEBUG)
		obj.addProperty("App::PropertyLink","Sketch","ThickenedSection","Section Sketch").Sketch = sketch
		obj.addProperty("App::PropertyLength","Thickness","ThickenedSection","Thickness of the material").Thickness = 1.0
		nWires = len(sketch.Shape.Wires)
		obj.addProperty("App::PropertyIntegerList","Sides","ThickenedSection","List of wire orientations").Sides = [1]*nWires
		obj.Proxy = self


	def execute(self, fp):
		while len(fp.Sides) < len(fp.Sketch.Shape.Wires):
			fp.Sides = fp.Sides + [1]
		updateThickenedSection(fp,fp.Sketch,fp.Thickness,fp.Sides)
