"""

Sample script usually supplied to gaudirun.py application.

To be tested for LHCbDataset.new

Taken from $STRIPPINGSELECTIONS/tests/data/Reco15_NoBias.py

"""

from Gaudi.Configuration import *
from GaudiConf import IOHelper
IOHelper('ROOT').inputFiles([
  'root://eoslhcb.cern.ch//eos/lhcb/user/r/rvazquez/DSTsForS23/114088641_NoBias_2015_0xEE63_Hlt.dst'
,'root://eoslhcb.cern.ch//eos/lhcb/user/r/rvazquez/DSTsForS23/114088646_NoBias_2015_0xEE63_Hlt.dst'
,'root://eoslhcb.cern.ch//eos/lhcb/user/r/rvazquez/DSTsForS23/114088652_NoBias_2015_0xEE63_Hlt.dst'
], clear=True)
