from unittest import TestCase


class Test(TestCase):
    def test_constants(self):
        import ec2_sizes
        self.assertTrue(ec2_sizes.INSTANCE_TYPES)
