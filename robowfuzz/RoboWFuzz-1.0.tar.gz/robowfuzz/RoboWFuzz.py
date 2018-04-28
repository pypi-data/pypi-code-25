import wfuzz
from robot.api import logger

class RoboWFuzz(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, dirfile):
        self.dirfile = dirfile

    def brute_directories(self, url_fuzz, concur = "1", file_name = "directory_brute.txt", follow = "False"):
        sess = wfuzz.FuzzSession(url=url_fuzz, printer=(file_name, "raw"), concurrent=int(concur), follow = bool(follow))

        for req in sess.fuzz(hc = [404], payloads = [("file", dict(fn = self.dirfile))]):
            logger.info(req)
