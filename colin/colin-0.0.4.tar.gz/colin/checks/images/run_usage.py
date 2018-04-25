from colin.checks.abstract.images import ImageCheck


class RunUsageCheck(ImageCheck):
    def __init__(self):
        super(__class__, self) \
            .__init__(name="run_usage",
                      message="Image can be run with the command specified in the usage label.",
                      description="The label usage is used for the invoking the image.",
                      reference_url="",
                      tags=["usage", "cmd", "image"])

    def check(self, target):
        if "usage" not in target.labels:
            return None


