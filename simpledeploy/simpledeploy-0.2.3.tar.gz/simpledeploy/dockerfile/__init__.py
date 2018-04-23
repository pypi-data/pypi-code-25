from string import Template

def dockerFrom(image='scratch'):
    return 'FROM %s' % image

def appDirectory(dir='/app'):
    dockerContents = (
        "RUN mkdir -p %s" % dir,
        "ADD . %s" % dir,
        "WORKDIR %s" % dir
        )
    print(dockerContents)
    return dockerContents
