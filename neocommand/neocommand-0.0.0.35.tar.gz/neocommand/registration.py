def init():
    import neocommand.drivers
    import neocommand.helpers.coercion_extensions
    from mhelper import reflection_helper
    from intermake import MENV
    from neocommand.core import constants
    from neocommand.core.core import CORE
    
    neocommand.drivers.init()
    neocommand.helpers.coercion_extensions.init()
    
    if MENV.configure( name = "NeoCommand",
                       root = CORE ):
        MENV.constants.update( (k, str( v )) for k, v in reflection_helper.public_dict( constants.__dict__ ).items() )
