from typing import Optional, cast

from PyQt5.QtWidgets import QDialog, QWidget

from editorium import EditoriumGrid, EEditGridMode
from intermake_qt.forms.designer.frm_arguments_designer import Ui_Dialog
from intermake_qt.forms.designer.resource_files import resources_rc

from intermake.engine.environment import MENV
from intermake.engine.plugin import Plugin
from mhelper import string_helper, ArgsKwargs, FnArgValueCollection
from mhelper.reflection_helper import FnArg, AnnotationInspector
from mhelper_qt import qt_gui_helper, exceptToGui, exqtSlot


cast( None, resources_rc )

__author__ = "Martin Rusilowicz"

_Coords_ = "Coords"


class FrmArguments( QDialog ):
    def __init__( self, parent: QWidget, plugin: Plugin, defaults: ArgsKwargs ) -> None:
        """
        CONSTRUCTOR
        """
        QDialog.__init__( self, parent )
        self.ui = Ui_Dialog( self )
        self.setWindowTitle( "{} - {}".format( parent.windowTitle(), plugin ) )
        
        self.__plugin = plugin
        
        self.result: FnArgValueCollection = None
        self.ui.CHK_HELP.setChecked( _global_options.inline_help )
        self.ui.CHK_HELP.stateChanged[int].connect( self.on_help_toggled )
        
        help_text = FnArgValueCollection()
        help_text.append( FnArg( plugin.name, AnnotationInspector( None ), None, plugin.get_description() ) )
        
        self.values = FnArgValueCollection( plugin.args, defaults )
        self.editorium_grid = EditoriumGrid( grid = self.ui.GRID_ARGS,
                                             targets = (help_text, self.values),
                                             fn_description = lambda x: MENV.host.substitute_text( x.description ) )
        
        self.__init_controls()
    
    
    @exceptToGui()
    def on_help_toggled( self, _state: int ) -> None:
        _global_options.inline_help = self.ui.CHK_HELP.isChecked()
        self.__init_controls()
    
    
    def __init_controls( self ):
        info = self.__plugin.visualisable_info()
        self.ui.LBL_PLUGIN_NAME.setText( string_helper.capitalise_first_and_fix( info.name ) )
        self.editorium_grid.mode = EEditGridMode.INLINE_HELP if self.ui.CHK_HELP.isChecked() else EEditGridMode.NORMAL
        self.editorium_grid.recreate()
    
    
    @staticmethod
    def request( owner_window: QWidget, plugin: Plugin, *args, **kwargs ) -> Optional[FnArgValueCollection]:
        """
        Shows the arguments request form.
        
        :param owner_window:    Owning window 
        :param plugin:          Plugin to show arguments for 
        :param args:            Optional defaults.
        :param kwargs:          Optional defaults.
        """
        args_kwargs = ArgsKwargs( *args, **kwargs )
        
        try:
            form = FrmArguments( owner_window, plugin, args_kwargs )
            
            if form.exec_():
                return form.result
            else:
                return None
        except Exception as ex:
            from mhelper import ansi_format_helper
            print( ansi_format_helper.format_traceback( ex ) )
            raise
    
    
    def __save_options( self ):
        MENV.local_data.store.commit( _global_options )
        self.__init_controls()
    
    
    @exqtSlot()
    def on_pushButton_clicked( self ) -> None:
        """
        Signal handler:
        """
        
        try:
            self.editorium_grid.commit()
            incomplete = self.values.get_incomplete()
            
            if incomplete:
                raise ValueError( "The following arguments have not been provided:\n{}".format( "\n".join( [("    * " + x) for x in incomplete] ) ) )
            
            self.result = self.values
            
            self.accept()
        except Exception as ex:
            qt_gui_helper.show_exception( self, "Error", ex )
            return


class _FrmArguments_Options:
    """
    :attr alternate_theme:   Use the alternate theme
    :attr inline_help:       Show help text alongside the arguments, rather than requiring a mouse-over
    """
    
    
    def __init__( self ):
        self.alternate_theme = False
        self.inline_help = True


_global_options = MENV.local_data.store.bind( "gui_arguments", _FrmArguments_Options() )
