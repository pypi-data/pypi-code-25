version = '1.12.1'
release = True
revision = ''

if release:
    fullVersion = '%s' % (version,)
else:
    fullVersion = '%s-%s' % (version, revision)

titleVersion = 'Version %s' % (fullVersion,)
