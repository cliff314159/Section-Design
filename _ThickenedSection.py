#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division # allows floating point division from integers
import FreeCAD, Part, math
from FreeCAD import Base
from FreeCAD import Gui
import ThickenedSection as TS
import Section_Design_dummy
import os

import logging,sys

# Locate Workbench Directory
pathWB= os.path.dirname(Section_Design_dummy.__file__)
sys.path.append(os.path.join(pathWB, 'Gui'))

pathWBIcons =  os.path.join( pathWB, 'Resources', 'Icons')

global main__ThickenedSection_Icon
main__ThickenedSection_Icon = os.path.join( pathWBIcons , 'ThickenedSection.svg')


class _ThickenedSection():

	def Activated(self):

		sel=Gui.Selection.getSelection()
		if len(sel)==1:
			sketch=Gui.Selection.getSelection()[0]
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ThickenedSection")
			TS.ThickenedSection(a,sketch)

			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			FreeCAD.ActiveDocument.recompute()




	
	def GetResources(self):
		return {'Pixmap' : main__ThickenedSection_Icon  , 'MenuText': 'ThickenedSection',
		'ToolTip': 'Thickened Section: \n Creates a planar section surface by the wires of a section. \n -Typically the input is a simple "stick figure" sketch. \n -The orientation of each wire can be independently controlled. \n -The resulting surface can then be analyzed for section properties.'}

Gui.addCommand('ThickenedSection',_ThickenedSection() )

