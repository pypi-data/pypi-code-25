from catnado.utils.environment import setup_cloud_sdk_paths


def pytest_configure():
  setup_cloud_sdk_paths()
