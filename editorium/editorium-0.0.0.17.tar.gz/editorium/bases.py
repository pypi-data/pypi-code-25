from typing import Dict, Optional, List

from mhelper import AnnotationInspector
from mhelper_qt import exceptToGui


class EditorInfo:
    def __init__( self, editorium: "Editorium", type_, messages: Dict[object, object] ) -> None:
        self.editorium = editorium
        self.annotation = AnnotationInspector( type_ )
        self.messages = messages
    
    
    def __str__( self ):
        return str( self.annotation )


class AbstractEditorType( type ):
    def can_handle( cls, info: EditorInfo ) -> bool:
        """
        Determines if this type can handle editing this type.
        
        :param info: Contains the type information
        """
        raise NotImplementedError( "abstract" )


class AbstractEditor( metaclass = AbstractEditorType ):
    """
    Base editor class
    """
    
    
    def __init__( self, info: EditorInfo, editor ):
        """
        CONSTRUCTOR
        :param info:        `info` passed to derived class constructor 
        :param editor:      Editor widget created by derived class 
        """
        from PyQt5.QtWidgets import QWidget
        assert isinstance( editor, QWidget )
        self.info = info
        self.editor: QWidget = editor
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        """
        Determines if this type can handle editing this type.
        
        :param info: Contains the type information
        """
        raise NotImplementedError( "abstract" )
    
    
    def get_value( self ) -> Optional[object]:
        """
        Obtains the value stored in the editor.
        This method should generally return the correct type, though this is not guaranteed.
        This method may raise an exception if the user has made an invalid selection.
        
        :except Exception: Invalid selection 
        """
        raise NotImplementedError( "abstract" )
    
    
    def set_value( self, value: Optional[object] ):
        """
        Sets the value of the editor.
        
        :param value:   A value that commutes with `self.info`.
                        The value `None` should also always be accepted as a default.
        """
        raise NotImplementedError( "abstract" )
    
    
    def handle_changes( self, signal ) -> None:
        """
        Connects the specified `signal` to the __change_occurred handler.
        """
        signal.connect( self.__change_occurred )
    
    
    # noinspection PyUnusedLocal
    @exceptToGui()
    def __change_occurred( self, *args, **kwargs ) -> None:
        """
        Handles changes to the editor.
        """
        pass


class Editorium:
    """
    Holds the set of editors.
    
    :attr editors:              Array of editor types.
    :attr default_messages:     Always appended to `messages`. 
    """
    
    
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        self.editors: List[AbstractEditorType] = []
        self.default_messages = { }
    
    
    def register( self, editor: AbstractEditorType ):
        """
        Registers an editor with this Editorium.
        """
        self.editors.insert( len( self.editors ) - 1, editor )
    
    
    def get_editor( self, type_: type, *, messages: Optional[Dict[object, object]] = None ) -> AbstractEditor:
        """
        Constructs a suitable editor for this type.
        :param messages:    Optional array of messages to pass to the editors. e.g. the OPTION_* fields in `editorium.constants`. See also `Editorium().default_messages` 
        :param type_:       Type of value to create editor for. Basic types, as well as most of `typing` and `mhelper.special_types` should be handled.
        :return: 
        """
        messages_d = dict( self.default_messages )
        
        if messages is not None:
            messages_d.update( messages )
        
        info = EditorInfo( self, type_, messages_d )
        
        for x in self.editors:
            if x.can_handle( info ):
                r = x( info )
                assert hasattr( r, "editor" ) and r.editor is not None, "«{}» didn't call the base class constructor.".format( x )
                return r
        
        raise ValueError( "No suitable editor found for «{}». This is an internal error and suggests that a working fallback editor has not been provided. The list of editors follows: {}".format( type_, self.editors ) )
