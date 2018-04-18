""" Package-scope globals.

The default preferences node is currently used by 'PreferencesHelper' and
'PreferencesBinding' instances if no specific preferences node is set. This
makes it easy for them to access the root node of an application-wide
preferences hierarchy.

"""


# The default preferences node.
_default_preferences = None

def get_default_preferences():
    """ Get the default preferences node. """

    return _default_preferences

def set_default_preferences(default_preferences):
    """ Set the default preferences node. """

    global _default_preferences

    _default_preferences = default_preferences

    # For convenience.
    return _default_preferences

#### EOF ######################################################################
