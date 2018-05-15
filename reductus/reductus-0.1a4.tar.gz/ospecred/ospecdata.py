import numpy as np
import datetime
from copy import deepcopy

class OffspecData(object):
    """ 
    Primary data object for off-specular reduction 
    
    axes are specified [[x (dim=M)], [y (dim=N)], [z (dim=P)]...] e.g. then data has 
    dimensions (M, N, P...)
    
    "axes": [[
        {
            "name": "theta",
            "values": np.ndarray([0,1,2,...], dtype="float"),
            "errors": np.ndarray([0,1,1,...], dtype="float"),
            ...
        },
      ],
      [
        {
            "name": "two_theta",
            "values": np.ndarray([0,2,4...], dtype="float"),
            "errors": np.ndarray([1,1,1,...], dtype="float"),
            ...
        }
      ],
    ], 
    
    "data": [
        {
            "name": "counts", 
            "values": np.ndarray([[...]], dtype="int"), # shape = MxN
            "variance": ...
            "normalization": ...            
        }
    ]
    """
    
    def __init__(self, axes=None, data=None, metadata=None, name=""):
        self.axes = axes
        self.data = data
        self.metadata = metadata
        self.name = name
        self.ndim = list(self.data.values())[0].ndim
    
    def copy(self):
        return deepcopy(self)
                
    def get_axis(self, axis_dim=None, axis_name=None):
        """ axis_dim is e.g. 0 for x, 1 for y, 2 for z """
        if axis_dim is None:
            # search all axes for axis_name
            ax = next((a for axis in self.axes for a in axis if a.get('name', None) == axis_name), None) 
        else:
            ax = next((a for a in self.axes[axis_dim] if a.get('name', None) == axis_name), None)
        
        if ax is None:
            raise KeyError('axis ' + str(axis_name) + ' not found')
        return ax
        
    def get_plottable_2d(self):
        primary_key = self.data.keys()[0]
        array_out = self.data[primary_key] / self.data['monitor']
        dump = {}
        dims = {}
        # can't display zeros effectively in log... set zmin to smallest non-zero
        
        lowest = 1e-10
        non_zeros = array_out[array_out > lowest]
        if len(non_zeros) > 0:
            dims['zmin'] = float(non_zeros.min())
            dims['zmax'] = float(non_zeros.max())
        else:
            dims['zmin'] = float(lowest)
            dims['zmax'] = float(lowest)

        axis = ['x', 'y']
        axes = {}
        for index, label in enumerate(axis):
            arr = self.axes[index][0]['values']
            dims[axis[index] + 'min'] = float(arr.min())
            dims[axis[index] + 'max'] = float(arr.max())
            dims[axis[index] + 'dim'] = len(arr)
            axes[label+'axis'] = {"label": self.axes[index][0].get('name', label + '-axis')}
        
        z = array_out.T.tolist()
        zlabel = self.data.get("name", "z")
        title =  self.name
        plot_type = '2d'
        transform = 'log' # this is nice by default
        dump.update( dict(type=plot_type, z=z, title=title, dims=dims,
                    axes=axes, zlabel=zlabel,
                    transform=transform) )
        return [dump]
        
    def to_dict(self):
        return _toDictItem(self.__dict__)
        #return dict(axes=dict(self.axes), data=dict(self.data), metadata=dict(self.metadata), name=self.name)


def _get_pol(das, pol):
    if pol in das:
        direction = das[pol+'/direction'][0]
        if direction == 'UP':
            result = '+'
        elif direction == 'DOWN':
            result = '-'
        elif direction == '' or direction == 'BEAM_OUT' or direction == 'UNPOLARIZED':
            result = ''
        else:
            raise ValueError("Don't understand DAS_logs/%s/direction=%r"%(pol,direction))
    else:
        result = ''
    return result

def _toDictItem(obj):
    if isinstance(obj, np.integer):
        obj = int(obj)
    elif isinstance(obj, np.floating):
        obj = float(obj)
    elif isinstance(obj, np.ndarray):
        obj = obj.tolist()
    elif isinstance(obj, datetime.datetime):
        obj = [obj.year, obj.month, obj.day, obj.hour, obj.minute, obj.second]
    elif isinstance(obj, list):
        obj = [_toDictItem(a) for a in obj]
    elif isinstance(obj, dict):
        obj = dict([(k, _toDictItem(v)) for k,v in obj.items()])
    return obj
    
def test():
    data =  {
        "name": "counts", 
        "value": np.ones((6,7), dtype="int"), # shape = MxN
        "variance": np.ones((6,7), dtype="float") * 0.5,
        "normalization": np.ones((6,7), dtype="float"),
    }
    
    axes = [
      [
        {
          "name": "pixels",
          "values": np.arange(6, dtype="float"),
        }
      ],
      [
        {
          "name": "theta",
          "values": np.linspace(1.0, 2.0, 7),
        }
      ],
    ]
          
    d = OffspecData(axes=axes, data=data, metadata={}, name="test")
    return d
    
if __name__ == '__main__':
    print(test().get_plottable_2d())
