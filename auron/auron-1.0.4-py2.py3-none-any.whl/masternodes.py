# 
#
# class Inductor(object):
#
#     def __init__(self, gds, data):
#         self.gds = gds
#         self.data = data
#
#
# class Resistors(object):
#
#     def __init__(self):
#         pass
#
#
# class Holes(object):
#
#     def __init__(self):
#         pass
#
#
# class Terminals(object):
#
#     def __init__(self):
#         pass
#
#
# class Via(gdspy.Label):
#     _ID = 0
#
#     def __init__(self, name, data):
#         self.id = 'v{}'.format(Via._ID)
#         Via._ID += 1
#
#         self.name = name
#         self.data = data
#
#
# class Capacitor(object):
#
#     def __init__(self, gds, data):
#         self.gds = gds
#         self.data = data
#
#
# class Junction(object):
#     _ID = 0
#
#     def __init__(self, name, data):
#         self.id = 'j{}'.format(Junction._ID)
#         Junction._ID += 1
#
#         self.name = name
#         self.data = data
