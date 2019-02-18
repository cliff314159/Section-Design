#import FreeCADGui
import os, sys
import Section_Design_dummy

pathWB= os.path.dirname(Section_Design_dummy.__file__)
sys.path.append(os.path.join(pathWB, 'Gui'))

pathWBIcons =  os.path.join( pathWB, 'Resources', 'Icons')

global mainWBIcon
mainWBIcon = os.path.join( pathWBIcons , 'SectionDesign.svg')

class SectionDesignWorkbench (Workbench):

	def __init__(self):
		self.__class__.Icon = mainWBIcon
		#self.__class__.Icon = FreeCAD.getUserAppDataDir()+"Mod" + "/Silk/Resources/Icons/Silk.svg"
		self.__class__.MenuText = "Section Design"
		self.__class__.ToolTip = "Section Design and Analysis for Engineers"

	def Initialize(self):
		"Initialize the workbench on FreeCAD start"
		import _ThickenedSection
		commandList = ["ThickenedSection"]
		self.appendToolbar("Section Design",commandList)

	def Activated(self):
		"This function is executed when the workbench is activated"
		return

	def Deactivated(self):
		"This function is executed when the workbench is deactivated"
		return

	def ContextMenu(self, recipient):
		"This is executed whenever the user right-clicks on screen"
		self.appendContextMenu("Section Design",commandList)

	def GetClassName(self): 
		# this function is mandatory if this is a full python workbench
		return "Gui::PythonWorkbench"
		
Gui.addWorkbench(SectionDesignWorkbench())



