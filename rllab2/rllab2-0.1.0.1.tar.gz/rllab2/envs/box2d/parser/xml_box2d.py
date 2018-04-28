# pylint: disable=no-init, too-few-public-methods, old-style-class

from __future__ import division
from __future__ import absolute_import
import xml.etree.ElementTree as ET

import Box2D
import numpy as np
from rllab2.envs.box2d.parser.xml_types import XmlElem, XmlChild, XmlAttr, \
    XmlChildren

from rllab2.envs.box2d.parser.xml_attr_types import Tuple, Float, Choice, \
    String, List, Point2D, Hex, Int, Angle, Bool, Either


class XmlBox2D(XmlElem):

    tag = u"box2d"

    class Meta(object):
        world = XmlChild(u"world", lambda: XmlWorld, required=True)

    def __init__(self):
        self.world = None

    def to_box2d(self, extra_data, world=None):
        return self.world.to_box2d(extra_data, world=world)


class XmlWorld(XmlElem):

    tag = u"world"

    class Meta(object):
        bodies = XmlChildren(u"body", lambda: XmlBody)
        gravity = XmlAttr(u"gravity", Point2D())
        joints = XmlChildren(u"joint", lambda: XmlJoint)
        states = XmlChildren(u"state", lambda: XmlState)
        controls = XmlChildren(u"control", lambda: XmlControl)
        warmStarting = XmlAttr(u"warmstart", Bool())
        continuousPhysics = XmlAttr(u"continuous", Bool())
        subStepping = XmlAttr(u"substepping", Bool())
        velocityIterations = XmlAttr(u"velitr", Int())
        positionIterations = XmlAttr(u"positr", Int())
        timeStep = XmlAttr(u"timestep", Float())

    def __init__(self):
        self.bodies = []
        self.gravity = None
        self.joints = []
        self.states = []
        self.controls = []
        self.warmStarting = True
        self.continuousPhysics = True
        self.subStepping = False
        self.velocityIterations = 8
        self.positionIterations = 3
        self.timeStep = 0.02

    def to_box2d(self, extra_data, world=None):
        if world is None:
            world = Box2D.b2World(allow_sleeping=False)
        world.warmStarting = self.warmStarting
        world.continuousPhysics = self.continuousPhysics
        world.subStepping = self.subStepping
        extra_data.velocityIterations = self.velocityIterations
        extra_data.positionIterations = self.positionIterations
        extra_data.timeStep = self.timeStep
        if self.gravity:
            world.gravity = self.gravity
        for body in self.bodies:
            body.to_box2d(world, self, extra_data)
        for joint in self.joints:
            joint.to_box2d(world, self, extra_data)
        for state in self.states:
            state.to_box2d(world, self, extra_data)
        for control in self.controls:
            control.to_box2d(world, self, extra_data)
        return world


class XmlBody(XmlElem):

    tag = u"body"

    TYPES = [u"static", u"kinematic", u"dynamic"]

    class Meta(object):
        color = XmlAttr(u"color", List(Float()))
        name = XmlAttr(u"name", String())
        typ = XmlAttr(u"type", Choice(u"static", u"kinematic", u"dynamic"),
                      required=True)
        fixtures = XmlChildren(u"fixture", lambda: XmlFixture)
        position = XmlAttr(u"position", Point2D())

    def __init__(self):
        self.color = None
        self.name = None
        self.typ = None
        self.position = None
        self.fixtures = []

    def to_box2d(self, world, xml_world, extra_data):
        body = world.CreateBody(type=self.TYPES.index(self.typ))
        body.userData = dict(
            name=self.name,
            color=self.color,
        )
        if self.position:
            body.position = self.position
        for fixture in self.fixtures:
            fixture.to_box2d(body, self, extra_data)
        return body


class XmlFixture(XmlElem):

    tag = u"fixture"

    class Meta(object):
        shape = XmlAttr(u"shape",
                        Choice(u"polygon", u"circle", u"edge", u"sine_chain"), required=True)
        vertices = XmlAttr(u"vertices", List(Point2D()))
        box = XmlAttr(u"box", Either(
            Point2D(),
            Tuple(Float(), Float(), Point2D(), Angle())))
        radius = XmlAttr(u"radius", Float())
        width = XmlAttr(u"width", Float())
        height = XmlAttr(u"height", Float())
        center = XmlAttr(u"center", Point2D())
        angle = XmlAttr(u"angle", Angle())
        position = XmlAttr(u"position", Point2D())
        friction = XmlAttr(u"friction", Float())
        density = XmlAttr(u"density", Float())
        category_bits = XmlAttr(u"category_bits", Hex())
        mask_bits = XmlAttr(u"mask_bits", Hex())
        group = XmlAttr(u"group", Int())

    def __init__(self):
        self.shape = None
        self.vertices = None
        self.box = None
        self.friction = None
        self.density = None
        self.category_bits = None
        self.mask_bits = None
        self.group = None
        self.radius = None
        self.width = None
        self.height = None
        self.center = None
        self.angle = None

    def to_box2d(self, body, xml_body, extra_data):
        attrs = dict()
        if self.friction:
            attrs[u"friction"] = self.friction
        if self.density:
            attrs[u"density"] = self.density
        if self.group:
            attrs[u"groupIndex"] = self.group
        if self.radius:
            attrs[u"radius"] = self.radius
        if self.shape == u"polygon":
            if self.box:
                fixture = body.CreatePolygonFixture(
                    box=self.box, **attrs)
            else:
                fixture = body.CreatePolygonFixture(
                    vertices=self.vertices, **attrs)
        elif self.shape == u"edge":
            fixture = body.CreateEdgeFixture(vertices=self.vertices, **attrs)
        elif self.shape == u"circle":
            if self.center:
                attrs[u"pos"] = self.center
            fixture = body.CreateCircleFixture(**attrs)
        elif self.shape == u"sine_chain":
            if self.center:
                attrs[u"pos"] = self.center
            m = 100
            vs = [
                (0.5/m*i*self.width, self.height*np.sin((1./m*i-0.5)*np.pi))
                for i in xrange(-m, m+1)
            ]
            attrs[u"vertices_chain"] = vs
            fixture = body.CreateChainFixture(**attrs)
        else:
            assert False
        return fixture


def _get_name(x):
    if isinstance(x.userData, dict):
        return x.userData.get(u'name')
    return None


def find_body(world, name):
    return [body for body in world.bodies if _get_name(body) == name][0]


def find_joint(world, name):
    return [joint for joint in world.joints if _get_name(joint) == name][0]


class XmlJoint(XmlElem):

    tag = u"joint"

    JOINT_TYPES = {
        u"revolute": Box2D.b2RevoluteJoint,
        u"friction": Box2D.b2FrictionJoint,
        u"prismatic": Box2D.b2PrismaticJoint,
    }

    class Meta(object):
        bodyA = XmlAttr(u"bodyA", String(), required=True)
        bodyB = XmlAttr(u"bodyB", String(), required=True)
        anchor = XmlAttr(u"anchor", Tuple(Float(), Float()))
        localAnchorA = XmlAttr(u"localAnchorA", Tuple(Float(), Float()))
        localAnchorB = XmlAttr(u"localAnchorB", Tuple(Float(), Float()))
        axis = XmlAttr(u"axis", Tuple(Float(), Float()))
        limit = XmlAttr(u"limit", Tuple(Angle(), Angle()))
        ctrllimit = XmlAttr(u"ctrllimit", Tuple(Angle(), Angle()))
        typ = XmlAttr(u"type", Choice(u"revolute", u"friction", u"prismatic"), required=True)
        name = XmlAttr(u"name", String())
        motor = XmlAttr(u"motor", Bool())

    def __init__(self):
        self.bodyA = None
        self.bodyB = None
        self.anchor = None
        self.localAnchorA = None
        self.localAnchorB = None
        self.limit = None
        self.ctrllimit = None
        self.motor = False
        self.typ = None
        self.name = None
        self.axis = None

    def to_box2d(self, world, xml_world, extra_data):
        bodyA = find_body(world, self.bodyA)
        bodyB = find_body(world, self.bodyB)
        args = dict()
        if self.typ == u"revolute":
            if self.localAnchorA:
                args[u"localAnchorA"] = self.localAnchorA
            if self.localAnchorB:
                args[u"localAnchorB"] = self.localAnchorB
            if self.anchor:
                args[u"anchor"] = self.anchor
            if self.limit:
                args[u"enableLimit"] = True
                args[u"lowerAngle"] = self.limit[0]
                args[u"upperAngle"] = self.limit[1]
        elif self.typ == u"friction":
            if self.anchor:
                args[u"anchor"] = self.anchor
        elif self.typ == u"prismatic":
            if self.axis:
                args[u"axis"] = self.axis
        else:
            raise NotImplementedError
        userData = dict(
            ctrllimit=self.ctrllimit,
            motor=self.motor,
            name=self.name
        )
        joint = world.CreateJoint(type=self.JOINT_TYPES[self.typ],
                                  bodyA=bodyA,
                                  bodyB=bodyB,
                                  **args)
        joint.userData = userData
        return joint


class XmlState(XmlElem):

    tag = u"state"

    class Meta(object):
        typ = XmlAttr(
            u"type", Choice(
                u"xpos", u"ypos", u"xvel", u"yvel", u"apos", u"avel",
                u"dist", u"angle",
            ))
        transform = XmlAttr(
            u"transform", Choice(u"id", u"sin", u"cos"))
        body = XmlAttr(u"body", String())
        to = XmlAttr(u"to", String())
        joint = XmlAttr(u"joint", String())
        local = XmlAttr(u"local", Point2D())
        com = XmlAttr(u"com", List(String()))

    def __init__(self):
        self.typ = None
        self.transform = None
        self.body = None
        self.joint = None
        self.local = None
        self.com = None
        self.to = None

    def to_box2d(self, world, xml_world, extra_data):
        extra_data.states.append(self)


class XmlControl(XmlElem):

    tag = u"control"

    class Meta(object):
        typ = XmlAttr(u"type", Choice(u"force", u"torque"), required=True)
        body = XmlAttr(
            u"body", String(),
            help=u"name of the body to apply force on")
        bodies = XmlAttr(
            u"bodies", List(String()),
            help=u"names of the bodies to apply force on")
        joint = XmlAttr(
            u"joint", String(),
            help=u"name of the joint")
        anchor = XmlAttr(
            u"anchor", Point2D(),
            help=u"location of the force in local coordinate frame")
        direction = XmlAttr(
            u"direction", Point2D(),
            help=u"direction of the force in local coordinate frame")
        ctrllimit = XmlAttr(
            u"ctrllimit", Tuple(Float(), Float()),
            help=u"limit of the control input in Newton")

    def __init__(self):
        self.typ = None
        self.body = None
        self.bodies = None
        self.joint = None
        self.anchor = None
        self.direction = None
        self.ctrllimit = None

    def to_box2d(self, world, xml_world, extra_data):
        if self.body != None:
            assert self.bodies is None, u"Should not set body and bodies at the same time"
            self.bodies = [self.body]

        extra_data.controls.append(self)


class ExtraData(object):

    def __init__(self):
        self.states = []
        self.controls = []
        self.velocityIterations = None
        self.positionIterations = None
        self.timeStep = None


def world_from_xml(s):
    extra_data = ExtraData()
    box2d = XmlBox2D.from_xml(ET.fromstring(s))
    world = box2d.to_box2d(extra_data)
    return world, extra_data
