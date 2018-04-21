import creaturecast_rigging.nodes.transform as trn
import creaturecast_rigging.rigging.part as prt
import copy
debug = True


class AbstractPartArray(trn.Transform):

    default_data = dict(
        base_type='abstract_part_array'
    )

    def __init__(self, *args, **kwargs):
        super(AbstractPartArray, self).__init__(*args, **kwargs)
        self.create_plug('size', type='double', value=1.0)

    def get_parts(self):
        parts = []
        for x in self.children:
            if isinstance(x, prt.AbstractPart):
                parts.append(x)
            if isinstance(x, AbstractPartArray):
                parts.extend(x.get_parts())
        return parts

    def get_part_joints(self):
        joints = []
        for part in self.get_parts():
            joints.extend(part.nodes.get('joints', []))
        return joints

    def get_hierarchy(self):
        for part in self.get_parts():
            yield (part.data['name'], str(part.nodes.get('parent_joint', None)))

    def set_hierarchy(self, data):
        parts_dictionary = dict((part.data['name'], part) for part in self.get_parts())
        joints_dictionary = dict((joint.data['name'], joint) for joint in self.get_part_joints())
        for part_name in data:
            part = parts_dictionary.get(part_name, None)
            if part:
                joint_name = data[part_name]
                joint = joints_dictionary.get(joint_name, None)
                if joint:
                    part.nodes['parent_joint'] = joints_dictionary[joint_name]
            yield part


class PartArrayTemplate(AbstractPartArray):

    default_data = dict(
        icon='part_array',
        root_name='part',
        suffix='pat',
        base_type='part_array_template'
    )

    def __init__(self, *args, **kwargs):
        super(PartArrayTemplate, self).__init__(*args, **kwargs)
        self.constructor = PartArray

    def create_rig(self, parent=None):
        data = dict(self.data)
        template_data = copy.copy(data)
        data.update(
            parent=parent,
            created=False,
            template_data=template_data
        )
        rig = self.constructor(**data)
        rig.create()
        for part in self.get_parts():
            part.create_rig(parent=rig)

        return rig


class PartArray(AbstractPartArray):

    default_data = dict(
        icon='part_array',
        root_name='part',
        suffix='pay',
        base_type='part_array'
    )

    def __init__(self, *args, **kwargs):
        super(PartArray, self).__init__(*args, **kwargs)
        self.constructor = PartArrayTemplate

    def create_template(self, parent=None):
        data = self.data['template_data']
        data.update(
            parent=parent,
            created=False
        )
        template = self.constructor(**data)
        template.create()

        for rig_child in self.get_parts():
            rig_child.create_template(parent=template)

        return template


def create_from_data(data):
    part = data['constructor'](**data['data'])
    part.create()
    for child_data in data['children']:
        child_data['parent'] = part
        create_from_data(child_data)
