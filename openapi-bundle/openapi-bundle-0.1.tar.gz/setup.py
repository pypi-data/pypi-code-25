from setuptools import setup

package = 'openapi-bundle'
version = '0.1'

setup(name=package,
      version=version,
      py_modules=["openapi_bundle"],
      install_requires=['Click', 'PyYaml'],
      entry_points='''
        [console_scripts]
        openapi-bundle=openapi_bundle:cli
      ''',
      description="Combine multiple json or yaml files "
                  "into a single readable OpenAPI specification.",
      url='https://github.com/windtail/openapi-bundle')
