from colin.checks.abstract.cmd import CmdCheck


class DockerEnvCheck(CmdCheck):

    def __init__(self):
        super(self.__class__, self) \
            .__init__(name="dockerenv",
                      message="a",
                      description="b",
                      reference_url="https://docs.docker.com/engine/reference/builder/#maintainer-deprecated",
                      tags=["dockerenv", "cmd", "output"],
                      cmd=['ls', '/.dockerenv'])
