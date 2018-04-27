targz = '/tmp/singularity-clair.omy6omor.tar.gz'

# Stopped here - need to start server, generate targz, add to static folder,
# Then serve file to clair, done :)

python setup.py install
sclair vsoch-hello-world-master-latest.simg 
gunicorn my_app_module:my_web_app --bind localhost:8080 --worker-class aiohttp.GunicornWebWorker

#['vsoch-hello-world-master-latest.simg']
#======== Running on http://127.0.0.1:8080 ========
#(Press CTRL+C to quit)
