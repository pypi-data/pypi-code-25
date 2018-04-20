class Settings:
    """
        Global file for settings
    """
    def __init__(self):
        self.settings = {
            'foo': {
                'bar': {
                    'foo': 'bar'
                }
            }
        }

    # Function to get a certain setting
    def get_setting(self, key, default=None):
        """
        Example key: 'foo.bar.foo'

        Parameters
        ----------
        key     - Embedded key as string
        default - Default value
        """

        # Split the given key
        split_string = key.split('.')

        # Set returning value to default
        setting = default

        # Set the current scope in the settings directory
        setting_scope = self.settings

        # Loop through the splitted keys
        for key in split_string:
            # Check if key exists in the current setting scope
            if key in setting_scope:
                # If its not the item we need the value from
                if split_string[-1] != key:
                    # Update the scope
                    setting_scope = setting_scope[key]

                    continue

                # This is the setting we want! WOW!
                # Update the setting variable to replace it with the default value
                setting = setting_scope[key]
            else:
                # If we haven't found the setting in the scope, stop the loop
                break

        # Return the setting
        return setting
