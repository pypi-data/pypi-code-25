# Enthought library imports.
from traits.api import Callable, HasTraits, Str, Unicode


class TaskFactory(HasTraits):
    """ A factory for creating a Task with some additional metadata.
    """

    # The task factory's unique identifier. This ID is assigned to all tasks
    # created by the factory.
    id = Str

    # The task factory's user-visible name.
    name = Unicode

    # A callable with the following signature:
    #
    #     callable(**traits) -> Task
    #
    # Often this attribute will simply be a Task subclass.
    factory = Callable

    def create(self, **traits):
        """ Creates the Task.

        The default implementation simply calls the 'factory' attribute.
        """
        return self.factory(**traits)

    def create_with_extensions(self, extensions, **traits):
        """ Creates the Task using the specified TaskExtensions.
        """
        task = self.create(**traits)
        for extension in extensions:
            task.extra_actions.extend(extension.actions)
            task.extra_dock_pane_factories.extend(extension.dock_pane_factories)
        return task
