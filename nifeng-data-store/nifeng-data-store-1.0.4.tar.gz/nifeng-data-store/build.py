import subprocess

subprocess.run("flake8", shell=True, check=True)
subprocess.run("pipenv run py.test", shell=True, check=True)
subprocess.run("nohup pipenv run python application.py --active_profile=apitest  > nohup.log 2>&1 &", shell=True,
               check=True)
subprocess.run("newman run tests/api_tests/assets-center-apis-tests.postman_collection.json", shell=True, check=True)

subprocess.run("rm -rf nohup.out", shell=True, check=True)
subprocess.run("rm -rf nohup.log", shell=True, check=True)


