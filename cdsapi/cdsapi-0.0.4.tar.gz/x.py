import cdsapi

c = cdsapi.Client()
c.retrieve("insitu-glaciers-elevation-mass", {"variable": "non-existent-variable", "format": "tgz"}, "dowload.data")
