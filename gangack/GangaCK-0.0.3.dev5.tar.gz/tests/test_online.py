# #!/usr/bin/env py.test

# """
# Need SetupGanga invoked
# """

# import pytest

# skipif = pytest.mark.skipif('"GANGASYSROOT" not in os.environ') #, reason="Requires Ganga environment.")
# slow = pytest.mark.slow

# #==============================================================================

# def standardSetup():
#    """Function to perform standard setup for Ganga.
#    """
#    import sys, os.path
#    # insert the path to Ganga itself
#    # exeDir = os.path.abspath(os.path.normpath(os.path.dirname(sys.argv[0])))
#    # gangaDir = os.path.join(os.path.dirname(exeDir), 'python' )
#    gangaDir = os.path.normpath(os.environ['GANGASYSROOT']+'/../install/ganga/python')
#    sys.path.insert(0, gangaDir)
#    import Ganga.PACKAGE
#    Ganga.PACKAGE.standardSetup()

# try:
#   standardSetup()
#   from Ganga.Core import GangaException
#   import Ganga.Runtime
#   try:
#     # Process options given at command line and in configuration file(s)
#     # Perform environment setup and bootstrap
#     Ganga.Runtime._prog = Ganga.Runtime.GangaProgram(argv=['--no-mon', '--no-rexec'])
#     Ganga.Runtime._prog.parseOptions()
#     Ganga.Runtime._prog.configure()
#     Ganga.Runtime._prog.initEnvironment()
#     Ganga.Runtime._prog.bootstrap()
#     # Import GPI and run Ganga
#     from Ganga import GPI
#     del GPI
#   except GangaException, x:
#     Ganga.Runtime._prog.log(x)
#     import sys
#     sys.exit(-1)
# except KeyError as e:
#   print e

# #==============================================================================
# # Decorators TEST
# #==============================================================================

# # @skipif
# # def test_check_job_status_valid():
# #   from GangaCK.Decorators import check_job_status
# #   assert check_job_status(1199) == 'completed'

# # @skipif
# # def test_check_job_status_missing():
# #   with pytest.raises(KeyError):
# #     check_job_status(-1)
# #   with pytest.raises(KeyError):
# #     check_job_status(9999)
  

# # #==============================================================================
# # # RECIPE
# # #==============================================================================

# # from PythonCK.GaudiRecipe import Recipe, TEMPLATE_DB

# # @pytest.fixture(scope="module")
# # def recipe():
# #   src = '/home/khurewat/bin/python/tests/test_gaudi_simulation/recipe/read_recipe.yaml'
# #   return Recipe(src)

# # @skipif
# # def test_recipe_constructor(recipe):
# #   assert recipe.keys()[0]  == 'Gauss'
# #   assert recipe.keys()[-1] == 'Moore'

# # @slow
# # @skipif
# # def test_setup_project_options(recipe):
# #   assert recipe.ganga.Moore.setupProjectOptions == '--runtime-project Hlt v23r0'

# # @slow
# # @skipif
# # def test_read_recipe_gauss(recipe):
# #   gauss = recipe.ganga.Gauss
# #   assert gauss.version == 'v46r4'
# #   # print list(gauss.optsfile)
# #   assert all(x==y for x,y in zip(
# #   [ 
# #     f.name for f in gauss.optsfile 
# #   ], 
# #   [ '/cvmfs/lhcb.cern.ch/lib/lhcb/DBASE/AppConfig/v3r200/options/Gauss/Beam6500GeV-md100-nu4.8.py',
# #     '/cvmfs/lhcb.cern.ch/lib/lhcb/DBASE/AppConfig/v3r200/options/Gauss/EnableSpillover-50ns.py',
# #     '/cvmfs/lhcb.cern.ch/lib/lhcb/GAUSS/GAUSS_v46r4/Gen/LbPythia8/options/Pythia8.py',
# #     '/cvmfs/lhcb.cern.ch/lib/lhcb/DBASE/AppConfig/v3r200/options/Gauss/G4PL_FTFP_BERT_EmNoCuts.py',
# #     '/cvmfs/lhcb.cern.ch/lib/lhcb/DBASE/AppConfig/v3r200/options/Persistency/Compression-ZLIB-1.py',
# #   ]))
# #   dbtext = TEMPLATE_DB.format(DDDB='dddb-20130929-1', CondDB='sim-20131023-vc-mu100') 
# #   assert dbtext in gauss.extraopts # Check for DDDBtag, CondDBtag

# # @slow
# # @skipif
# # def test_read_recipe_boole(recipe):
# #   boole = recipe.ganga.Boole
# #   assert boole.version == 'v26r8'


# # @skipif
# # def test_read_recipe_bender(recipe):
# #   bender = recipe.ganga.Bender
# #   assert bender.version == 'v24r0'
# #   assert str(bender.module.name)  == '/home/khurewat/PhD_Analysis/012_Hlt2Ditau/generation/bender.py'


# #==============================================================================
# # IOUTILS
# #==============================================================================

# # if __name__ == '__main__':
#   # main()

# # ./test_my_ganga_online.py -s --durations=0
