from . import sm
from . import util

###  Use the second line for testing outside of soar
from soar.io import io
#import io

class DynamicMoveToPoint(sm.SM):
    """
    Drive to a goal point in the frame defined by the odometry.  Goal
    points are part of the input, in contrast to
    ``moveToPoint.MoveToPoint``, which takes a single goal pose at
    initialization time. 

    Assume inputs are ``(util.Point, io.SensorInput)`` pairs
    """

#!    pass
    forwardGain = 2.0
    rotationGain = 1.5
    angle_eps = 0.05
    dist_eps = 0.05
    
    start_state = False
    """State is ``True`` if we have reached the goal and ``False`` otherwise"""

    def __init__(self, maxRVel = 0.5, maxFVel = 0.5):
        """
        :param maxRVel: maximum rotational velocity
        :param maxFVel: maximum forward velocity
        """
        self.maxRVel = maxRVel
        self.maxFVel = maxFVel

    def get_next_values(self, state, inp):
        (goalPoint, sensors) = inp
        robotPose = sensors.odometry
        robotPoint = robotPose.point()
        robotTheta = robotPose.theta

        nearGoal = robotPoint.is_near(goalPoint, self.dist_eps)

        headingTheta = robotPoint.angleTo(goalPoint)
        r = robotPoint.distance(goalPoint)

        if nearGoal:
            # At the right place, so do nothing
            a = io.Action()
        elif util.near_angle(robotTheta, headingTheta, self.angle_eps):
            # Pointing in the right direction, so move forward
            a = io.Action(fvel = util.clip(r * self.forwardGain,
                                           -self.maxFVel, self.maxFVel))
        else:
            # Rotate to point toward goal
            headingError = util.fix_angle_plus_minus_pi(headingTheta - robotTheta)
            a = io.Action(rvel = util.clip(headingError * self.rotationGain,
                                           -self.maxRVel, self.maxRVel))
        return (nearGoal, a)

    def done(self, state):
        return state

#!
