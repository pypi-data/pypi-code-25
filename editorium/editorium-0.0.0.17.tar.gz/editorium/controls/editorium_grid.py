import editorium.bases
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QGridLayout, QSpacerItem, QSizePolicy, QGroupBox, QVBoxLayout, QLabel, QMessageBox, QWidget, QToolButton, QPushButton
from typing import Optional, Callable, Iterable, Sequence, Tuple, List

import editorium
from mhelper import MEnum, FnArgValueCollection, Coords, string_helper, NOT_PROVIDED, ResourceIcon
from mhelper.reflection_helper import FnArg
from mhelper_qt import qt_gui_helper


class EEditGridMode( MEnum ):
    NORMAL = 0
    INLINE_HELP = 1


class EditoriumGrid:
    """
    Populates a QGridLayout with a set of controls inferred from the data-types and
    annotations on the objects which they are to edit.
    
    Usage:
        * Construct the object with the appropriate parameters
        * Call `recreate` to create the controls
        * Parameters can be changed again post-construction, call `recreate` to recreate the controls
    """
    ansi_theme = qt_gui_helper.ansi_scheme_light( bg = "#00000000", fg = "#000000" )
    
    
    def __init__( self,
                  grid: QGridLayout,
                  targets: Optional[Sequence[FnArgValueCollection]],
                  mode: EEditGridMode = EEditGridMode.NORMAL,
                  fn_description: Callable[[FnArg], str] = None ):
        """
        CONSTRUCTOR
        
        :param grid:            Grid to bind to 
        :param targets:         Targets to create query for 
        :param mode:            Display mode 
        :param fn_description:  How to obtain descriptions (by default `FnArg.description`) 
        """
        self.grid: QGridLayout = grid
        self.targets: Sequence[FnArgValueCollection] = targets
        self.mode = mode
        self.fn_description = fn_description
        self.editors: List[Tuple[FnArgValueCollection, FnArg, editorium.bases.AbstractEditor]] = []
        self.help_map = { }
    
    
    def recreate( self ):
        self.help_map.clear()
        self.__delete_children()
        self.editors.clear()
        
        coords = Coords( 0, 0 )
        
        for target in self.targets:
            for plugin_arg in target:
                if self.mode == EEditGridMode.NORMAL:
                    self.__mk_editor_grid( target, plugin_arg, coords )
                else:
                    self.__mk_editor_expanded( target, plugin_arg, coords )
        
        self.grid.addItem( QSpacerItem( 1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding ) )
    
    
    def __delete_children( self ):
        for i in reversed( range( self.grid.count() ) ):
            widget = self.grid.itemAt( i ).widget()
            
            if widget is not None:
                widget.setParent( None )
    
    
    def __mk_editor_expanded( self, target: FnArgValueCollection, plugin_arg: FnArg, coords: Coords ):
        # Groupbox
        parameter_groupbox = QGroupBox()
        parameter_groupbox.setTitle( string_helper.capitalise_first_and_fix( plugin_arg.name ) )
        parameter_groupbox.setMaximumWidth( 768 )
        parameter_groupbox.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Minimum )
        parameter_groupbox.setWhatsThis( str( plugin_arg.annotation ) )
        
        # Layout
        parameter_layout = QVBoxLayout()
        parameter_groupbox.setLayout( parameter_layout )
        
        # Position
        self.grid.addWidget( parameter_groupbox, coords.row, coords.col )
        
        coords.row += 1
        
        # Help label
        help_widget = self.create_help_label( self.__get_description( plugin_arg ), [parameter_groupbox] )
        parameter_layout.addWidget( help_widget )
        editor = self.__mk_editorium( target, plugin_arg, target.get_value( plugin_arg ) )
        
        parameter_layout.addWidget( editor.editor )
    
    
    @classmethod
    def create_help_label( cls, html: str, controls: Optional[Iterable[QWidget]] = () ) -> QWidget:
        """
        A class method that creates a `QWidget` with the specified `help_text`.
        Also sets the `toolTip` and `whatsThis` text on any specified `controls` to the `help_text`.
        :return: The created `QWidget`
        """
        help_label = QLabel()
        help_label.setProperty( "theme", "helpbox" )
        help_label.setWordWrap( True )
        help_label.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Preferred )
        help_label.setText( html )
        help_label.setWhatsThis( html )
        
        for control in controls:
            control.setToolTip( html )
            control.setWhatsThis( html )
        
        return help_label
    
    
    def __mk_editorium( self, target: FnArgValueCollection, arg: FnArg, value: object ):
        messages = { }
        
        if self.mode == EEditGridMode.INLINE_HELP:
            messages[editorium.OPTION_BOOLEAN_RADIO] = True
        else:
            messages[editorium.OPTION_ALIGN_LEFT] = True
        
        editor = editorium.default_editorium().get_editor( arg.annotation.value, messages = messages )
        editor.editor.setSizePolicy( QSizePolicy.Minimum, QSizePolicy.Minimum )
        
        if value is NOT_PROVIDED:
            value = arg.default
        
        if value is NOT_PROVIDED:
            value = None
        
        editor.set_value( value )
        
        self.editors.append( (target, arg, editor) )
        return editor
    
    
    def __mk_editor_grid( self, target: FnArgValueCollection, arg: FnArg, coords: Coords ):
        description = self.__get_description( arg )
        
        # Help button
        button = QPushButton()
        button.setFlat( True )
        button.setIcon( ResourceIcon( "help" ).icon() )
        button.setIconSize( QSize( 16, 16 ) )
        button.setText( "" )
        button.setMaximumSize( 24, 24 )
        button.clicked.connect( self.help_button_clicked )
        self.help_map[button] = arg
        self.grid.addWidget( button, coords.row, coords.col+1 )
        
        # Name label
        label = QLabel()
        label.setText( arg.name )
        label.setWhatsThis( description )
        self.grid.addWidget( label, coords.row, coords.col + 0 )
        
        # Input
        editor = self.__mk_editorium( target, arg, target.get_value( arg ) )
        self.grid.addWidget( editor.editor, coords.row, coords.col + 2 )
        # self.create_help_label( description, [label, editor.editor] )
        
        coords.row += 1
    
    
    def __get_description( self, plugin_arg: FnArg ):
        if self.fn_description:
            help_text= self.fn_description( plugin_arg )
        else:
            help_text=plugin_arg.description
            
        help_text = help_text.strip()
        html = qt_gui_helper.ansi_to_html( help_text, lookup = type(self).ansi_theme )
        html = html.replace( "font-family:sans-serif", "font-family:Times New Roman" )
        return html
    
    
    def help_button_clicked( self, _: object ):
        label = self.grid.sender()
        fn: FnArg = self.help_map[label]
        html = self.__get_description( fn )
        msg = QMessageBox()
        msg.setText( fn.name )
        msg.setInformativeText( html )
        msg.setDetailedText( "This parameter is of type '{}' and the default value is '{}'.".format( fn.annotation, fn.default ) )
        msg.setWindowTitle( "Help" )
        msg.exec_()
    
    
    def commit( self ) -> List[FnArgValueCollection]:
        """
        Commits the changes and returns the modified value collection.
        """
        r = []
        
        for target, plugin_arg, value_fn in self.editors:
            if target not in r:
                r.append( target )
            
            try:
                target.set_value( plugin_arg, value_fn.get_value() )
            except Exception as ex:
                raise ValueError( "The value of the argument «{}» is invalid: ".format( plugin_arg.name ) + str( ex ) ) from ex
        
        return r
