import creaturecast_rigging.rigging.transform_array as tay
import creaturecast_rigging.rigging.capsule as cap


class CapsuleArray(tay.TransformArray):

    default_data = dict(
        icon='capsule_array',
        suffix='cay'
    )
    node_constructor = cap.Capsule

    def __init__(self, *args, **kwargs):
        super(CapsuleArray, self).__init__(*args, **kwargs)
        self.create_plug('size', type='double', value=1.0)

    def create(self):
        super(CapsuleArray, self).create()
        for capsule in self.nodes['items']:
            self.plugs['size'].connect_to(capsule.plugs['size'])
        return self
