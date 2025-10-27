from eodc_cf._version import __version__
from eodc_cf._version import __commit__

name = "eodc_cf"

from eodc_cf._core import CFDataset, CFDataVariable, CFFlagVariable, CFCoordinate, CFMultiscaleAttributes, CFMultiscaleDataset
from eodc_cf._lib import CFLonCoordinate, CFLatCoordinate, CFXCoordinate, CFYCoordinate, CFTimeCoordinate

__all__ = ['CFDataset', 
           'CFDataVariable', 
           'CFFlagVariable', 
           'CFCoordinate', 
           'CFMultiscaleAttributes', 
           'CFMultiscaleLayout', 
           'CFMultiscaleDataset',
           'CFLonCoordinate', 
           'CFLatCoordinate', 
           'CFXCoordinate', 
           'CFYCoordinate', 
           'CFTimeCoordinate']