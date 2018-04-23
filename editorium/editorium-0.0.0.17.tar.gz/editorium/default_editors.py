import sip
from typing import Dict, Iterable, List, Optional, Sequence, cast

import stringcoercion
from PyQt5.QtCore import QMargins, Qt
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QAbstractSpinBox, QCheckBox, QComboBox, QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QRadioButton, QSizePolicy, QSpacerItem, QSpinBox, QToolButton, QWidget
from editorium import constants
from editorium.bases import AbstractEditor, EditorInfo
# noinspection PyPackageRequirements
from flags import Flags
from mhelper import EFileMode, FileNameAnnotation, Filename, HReadonly, SwitchError, abstract, ignore, override, sealed, virtual, Password
from mhelper_qt import exceptToGui
from stringcoercion import AbstractEnumCoercer


def __combine( x: Dict[Flags, QCheckBox] ) -> Flags:
    t = next( iter( x.keys() ) )
    # noinspection PyUnresolvedReferences
    value = t.__no_flags__
    
    for k, v in x:
        if v.isChecked():
            value |= k
    
    return value


class NullableEditor( AbstractEditor ):
    """
    Edits: Optional[T] (as a fallback for editors of `T` not supporting `None` as an option)
    """
    
    
    def __init__( self, info: EditorInfo ):
        layout = QHBoxLayout()
        layout.setContentsMargins( QMargins( 0, 0, 0, 0 ) )
        
        self.editor = QFrame()
        self.editor.setLayout( layout )
        
        self.checkbox = QCheckBox()
        self.checkbox.stateChanged[int].connect( self.__on_checkbox_toggled )
        self.checkbox.setSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed )
        
        self.option_visual_tristate = info.messages.get( constants.OPTION_VISUAL_TRISTATE, False )
        self.option_hide = info.messages.get( constants.OPTION_HIDE, False )
        self.option_show_text = info.messages.get( constants.OPTION_SHOW_TEXT, "" )
        self.option_hide_text = info.messages.get( constants.OPTION_HIDE_TEXT, self.option_show_text )
        self.option_align_left = self.option_hide and info.messages.get( constants.OPTION_ALIGN_LEFT, False )
        
        if self.option_visual_tristate:
            self.checkbox.setTristate( True )
        
        layout.addWidget( self.checkbox )
        
        underlying_type = info.annotation.optional_type
        
        self.sub_editor = info.editorium.get_editor( underlying_type, messages = info.messages )
        self.sub_editor.editor.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
        layout.addWidget( self.sub_editor.editor )
        
        if self.option_align_left:
            self.non_editor = QLabel()
            self.non_editor.setText( "" )
            self.non_editor.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
            layout.addWidget( self.non_editor )
        
        self.__on_checkbox_toggled( self.checkbox.isChecked() )
        
        super().__init__( info, self.editor )
    
    
    @exceptToGui()
    def __on_checkbox_toggled( self, _: int ):
        if self.option_visual_tristate:
            if self.checkbox.checkState() == Qt.Unchecked:
                self.checkbox.setCheckState( Qt.PartiallyChecked )
                return
        
        state = self.checkbox.checkState() == Qt.Checked
        
        if self.option_hide:
            self.sub_editor.editor.setVisible( state )
        else:
            self.sub_editor.editor.setEnabled( state )
        
        if self.option_align_left:
            self.non_editor.setVisible( not state )
        
        if state:
            self.checkbox.setText( self.option_show_text )
        elif self.option_hide:
            self.checkbox.setText( self.option_hide_text )
    
    
    def get_value( self ) -> Optional[object]:
        if self.checkbox.isChecked():
            return self.sub_editor.get_value()
        else:
            return None
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        return info.annotation.is_optional
    
    
    def set_value( self, value: Optional[object] ) -> None:
        self.checkbox.setChecked( value is not None )
        self.__on_checkbox_toggled( self.checkbox.isChecked() )
        
        if value is not None:
            self.sub_editor.set_value( value )


class StringEditor( AbstractEditor ):
    """
    Edits: str
    """
    
    
    def __init__( self, info: EditorInfo ):
        self.editor = QLineEdit()
        
        super().handle_changes( self.editor.textChanged[str] )
        
        super().__init__( info, self.editor )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ):
        return info.annotation.is_directly_below( str )
    
    
    def set_value( self, value: str ):
        if value is None:
            value = ""
        
        self.editor.setText( value )
    
    
    def get_value( self ) -> str:
        return self.editor.text()


class PasswordEditor( AbstractEditor ):
    """
    Edits: Password
    """
    
    
    def __init__( self, info: EditorInfo ):
        self.editor = QLineEdit()
        self.editor.setEchoMode( QLineEdit.Password )
        super().handle_changes( self.editor.textChanged[str] )
        
        super().__init__( info, self.editor )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ):
        return info.annotation.is_directly_below( Password )
    
    
    def set_value( self, value: Password ):
        if value is None:
            value = Password( "" )
        
        self.editor.setText( value.value )
    
    
    def get_value( self ) -> Password:
        return Password( self.editor.text() )


class AnnotationEditor( AbstractEditor ):
    def __init__( self, info: EditorInfo ):
        self.delegate = info.editorium.get_editor( info.annotation.mannotation_arg, messages = info.messages )
        
        super().__init__( info, self.delegate.editor )
    
    
    def set_value( self, value: Optional[object] ):
        self.delegate.set_value( value )
    
    
    def get_value( self ) -> Optional[object]:
        return self.delegate.get_value()
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        return info.annotation.is_mannotation


class ListTEditor( AbstractEditor ):
    """
    Edits: List[T]
    """
    
    
    def __init__( self, info: EditorInfo ):
        self.list_type = info.annotation.generic_list_type
        
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins( QMargins( 0, 0, 0, 0 ) )
        
        self.spinner = QSpinBox()
        self.spinner.setValue( 1 )
        self.spinner.valueChanged.connect( self.__valueChanged )
        self.spinner.setButtonSymbols( QAbstractSpinBox.UpDownArrows )
        self.layout.addWidget( self.spinner )
        
        self.editor = QFrame()
        self.editor.setLayout( self.layout )
        
        self.editors = []
        
        super().__init__( info, self.editor )
        
        self.__add_editor()
    
    
    @exceptToGui()
    def __valueChanged( self, num_editors: int ):
        while len( self.editors ) > num_editors:
            self.__remove_editor()
        
        while len( self.editors ) < num_editors:
            self.__add_editor()
    
    
    def __add_editor( self ) -> None:
        editor = self.info.editorium.get_editor( self.list_type )
        self.layout.addWidget( editor.editor )
        self.editors.append( editor )
    
    
    def __remove_editor( self ) -> None:
        editor = self.editors.pop()
        self.layout.removeWidget( editor.editor )
        sip.delete( editor.editor )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        return info.annotation.is_generic_list
    
    
    def set_value( self, value: List[object] ) -> None:
        if value is None:
            value = []
        
        self.spinner.setValue( len( value ) )
        
        for i, x in enumerate( value ):
            self.editors[i].set_value( x )
    
    
    def get_value( self ) -> List[object]:
        r = []
        
        for x in self.editors:
            v = x.get_value()
            r.append( v )
        
        return r


class FallbackEditor( AbstractEditor ):
    """
    Last resort editor for concrete objects that just returns strings.
    
    Edits: object
    """
    
    
    def __init__( self, info: EditorInfo ) -> None:
        self.editor = QLineEdit()
        self.editor.setPlaceholderText( "(empty)" )
        super().__init__( info, self.editor )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        return not info.annotation.is_optional
    
    
    def set_value( self, value: object ) -> None:
        self.editor.setText( str( value ) if value is not None else "" )
    
    
    def get_value( self ) -> str:
        return self.editor.text()


class AbstractEnumEditor( AbstractEditor ):
    """
    Base class for enumerative edits (things with combo boxes)
    """
    
    
    def __init__( self, info: EditorInfo ):
        self.editor: QComboBox = QComboBox()
        self.items: Sequence[object] = self.get_options( info )
        
        if info.annotation.is_optional:
            self.items: Sequence[object] = cast( List[object], [None] ) + list( self.items )
        
        self.names: List[str] = [self.get_option_name( info, x ) for x in self.items]
        self.editor.setEditable( self.get_accepts_user_options() )
        self.editor.addItems( self.names )
        
        super().handle_changes( self.editor.currentTextChanged )
        
        super().__init__( info, self.editor )
        
        self.set_value( None )
    
    
    def get_accepts_user_options( self ) -> bool:
        return False
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        raise NotImplementedError( "still abstract" )
    
    
    def set_value( self, value: object ):
        if value is None:
            if not self.info.annotation.is_optional:
                self.editor.setCurrentIndex( 0 )
                return
        
        try:
            index = self.items.index( value )
        except ValueError:
            if self.editor.isEditable():
                self.editor.setCurrentText( self.get_option_name( self.info, value ) )
        else:
            self.editor.setCurrentIndex( index )
    
    
    def get_value( self ) -> object:
        if self.editor.currentIndex() == -1:
            raise ValueError( "A selection must be made." )
        
        index = self.editor.currentIndex()
        
        if self.get_option_name( self.info, self.items[index] ) == self.editor.currentText():
            return self.items[index]
        
        if self.editor.isEditable():
            return self.get_option_from_name( self.editor.currentText() )
    
    
    @virtual
    def get_option_from_name( self, text: str ):
        raise ValueError( "Not supported because `get_accepts_user_options` is not set" )
    
    
    @virtual
    def get_none_name( self, info: EditorInfo ) -> str:
        return info.messages.get( str( constants.OPTION_ENUM_NONE ), "None" )
    
    
    @abstract
    def get_options( self, info: EditorInfo ) -> Sequence[object]:
        raise NotImplementedError( "abstract" )
    
    
    @virtual
    def get_option_name( self, info: EditorInfo, item: object ) -> str:
        ignore( info )
        
        if item is None:
            return self.get_none_name()
        
        return str( item )


class StringCoercionEnumEditor( AbstractEnumEditor ):
    """
    Edits:  Anything handled by a `stringcoercion.AbstractEnumCoercer`.
            This includes enums.
    """
    
    
    def __init__( self, info: EditorInfo ):
        self.coercer_info = stringcoercion.CoercionInfo( info.annotation, None, None )
        self.coercer: AbstractEnumCoercer = self.__get_coercer( info )
        super().__init__( info )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        return cls.__get_coercer( info ) is not None
    
    
    @classmethod
    def __get_coercer( cls, info: EditorInfo ) -> Optional[AbstractEnumCoercer]:
        dc = stringcoercion.get_default_coercer()
        ci = stringcoercion.CoercionInfo( info.annotation, dc, None )
        
        for sc in dc.coercers:
            if isinstance( sc, stringcoercion.AbstractEnumCoercer ):
                if sc.can_handle( ci ):
                    return sc
        
        return None
    
    
    def get_accepts_user_options( self ):
        return self.coercer.get_accepts_user_options()
    
    
    def get_option_from_name( self, text: str ):
        return self.coercer.coerce( stringcoercion.CoercionInfo( self.info.annotation, None, text ) )
    
    
    def get_option_name( self, info: EditorInfo, item: object ):
        return self.coercer.get_option_name( item )
    
    
    def get_options( self, info: EditorInfo ) -> Sequence[object]:
        return self.coercer.get_options( self.coercer_info )


@abstract
class AbstractBrowserEditor( AbstractEditor ):
    """
    ABSTRACT CLASS
    
    Displays a text-box and button.
    
    The derived class should override the `@abstract` decorated methods, and optionally the `@virtual` ones:
    * can_handle
    * on_convert_from_text
    * on_convert_to_text
    * on_browse
    """
    
    
    def __init__( self, info: EditorInfo ):
        """
        CONSTRUCTOR
        :param info:        As base class 
        """
        self.validated_value = None
        
        layout = QHBoxLayout()
        layout.setContentsMargins( QMargins( 0, 0, 0, 0 ) )
        
        editor = QFrame()
        editor.setLayout( layout )
        
        self.line_edit = QLineEdit()
        self.line_edit.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
        self.line_edit.setPlaceholderText( "" )
        
        layout.addWidget( self.line_edit )
        
        edit_btn = QToolButton()
        edit_btn.setText( "BROWSE" )
        edit_btn.clicked[bool].connect( self.__btn_clicked )
        layout.addWidget( edit_btn )
        
        if info.annotation.is_optional:
            clear_btn = QToolButton()
            clear_btn.setText( "CLEAR" )
            clear_btn.clicked[bool].connect( self.__btn_clear_clicked )
            layout.addWidget( clear_btn )
        
        super().__init__( info, editor )
        
        self.set_value( None )
    
    
    @classmethod
    @abstract
    @override
    def can_handle( cls, info: EditorInfo ) -> bool:
        """
        ABSTRACT - as base class.
        
        The derived class should:
        * Return a value according to the base class definition.
        """
        raise NotImplementedError( "abstract" )
    
    
    @virtual
    def on_convert_from_text( self, text: str ) -> object:
        """
        Converts the specified object from text
        
        The derived class should:
        * Convert the text to its representative value.
        
        The default implementation returns the text, and is thus only suitable if the handled type is `str`-like.
        
        :param text:        Text, which is never empty or None.
        :return:            The object.
        :except ValueError: The derived class should raise a suitable and descriptive exception if conversion fails. 
        """
        return text
    
    
    @virtual
    def on_convert_to_text( self, value: object ) -> str:
        """
        Converts the specified object from text
        
        The derived class should:
        * Convert the value to a reversible string accurately representing it.
        
        The default implementation uses `__str__`.
        
        :param value:   A value, which is never `None`.
        """
        return str( value )
    
    
    @virtual
    def on_browse( self, value: Optional[object] ) -> Optional[str]:
        """
        Shows the browse dialogue.
        
        The derived class should:
        * Present the user with a browser displaying the available values.
        
        :param value:   The currently selected value, which may be `None` if the current selection is invalid. 
        :return:        The newly selected value, which may be `None` if the user cancels.
        """
        raise NotImplementedError( "abstract" )
    
    
    @sealed
    def set_value( self, value: Optional[object] ):
        if value is None:
            text = ""
        else:
            text = self.on_convert_to_text( value )
        
        self.line_edit.setText( text )
    
    
    @sealed
    def get_value( self ) -> Optional[object]:
        text = self.line_edit.text()
        
        if text == "":
            return None
        else:
            return self.on_convert_from_text( text )
    
    
    @exceptToGui()
    def __btn_clear_clicked( self, _ ) -> None:
        self.set_value( None )
    
    
    @exceptToGui()
    def __btn_clicked( self, _ ) -> None:
        text = self.line_edit.text()
        
        if text == "":
            value = None
        else:
            try:
                value = self.on_convert_from_text( text )
            except Exception:
                # ignore the exception, just cancel the section and move on
                value = None
        
        result = self.on_browse( value )
        
        if result is not None:
            self.set_value( result )


class FilenameEditor( AbstractBrowserEditor ):
    """
    Edits:  Filename[T, U] 
            Optional[Filename[T, U]]
    """
    
    
    def on_get_default_value( self ) -> object:
        return ""
    
    
    def on_convert_from_text( self, text ) -> Optional[str]:
        return text
    
    
    def on_convert_to_text( self, value: Filename ) -> str:
        return value
    
    
    def __init__( self, info: EditorInfo ):
        super().__init__( info )
    
    
    def on_browse( self, value: Filename ) -> str:
        d = QFileDialog()
        i = self.info  # type: EditorInfo
        t = cast( FileNameAnnotation, i.annotation.mannotation )
        
        if t.extension is not None:
            d.setNameFilters( ["{} files (*{})".format( t.extension[1:].upper(), t.extension )] )
        
        if t.mode == EFileMode.READ:
            d.setFileMode( QFileDialog.ExistingFile )
        else:
            d.setFileMode( QFileDialog.AnyFile )
        
        d.selectFile( value )
        
        if d.exec_():
            file_name = d.selectedFiles()[0]
            return file_name
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        return info.annotation.is_mannotation_of( Filename )


class AbstractFlagsEditor( AbstractEditor ):
    PROPERTY_NAME = "Editor_EnumerativeMultiBase_Value"
    
    
    def __init__( self, info: EditorInfo ):
        self.editor = QFrame()
        layout = QHBoxLayout()
        layout.setContentsMargins( QMargins( 0, 0, 0, 0 ) )
        self.editor.setLayout( layout )
        self.items = list( self.get_items( info ) )
        control_lookup = { }
        self.sub_editors = []
        
        for item in self.items:
            sub_editor = QCheckBox()
            sub_editor.setProperty( self.PROPERTY_NAME, item )
            layout.addWidget( sub_editor )
            sub_editor.setText( self.get_name( info, item ) )
            control_lookup[item] = sub_editor
            self.sub_editors.append( sub_editor )
        
        spacerItem = QSpacerItem( 20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum )
        layout.addItem( spacerItem )
        
        super().__init__( info, self.editor )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        raise NotImplementedError( "abstract" )
    
    
    def set_value( self, value: Flags ) -> None:
        for x in self.sub_editors:
            if self.is_set( self.info, x.property( self.PROPERTY_NAME ), value ):
                x.setChecked( True )
            else:
                x.setChecked( False )
    
    
    def is_set( self, info: EditorInfo, query: object, value: object ) -> bool:
        raise NotImplementedError( "abstract" )
    
    
    def get_value( self ) -> object:
        values = []
        for x in self.sub_editors:
            if x.isChecked():
                values.append( x.property( self.PROPERTY_NAME ) )
        
        return self.translate( self.info, values )
    
    
    def get_items( self, info: EditorInfo ) -> Iterable[object]:
        raise NotImplementedError( "abstract" )
    
    
    def get_name( self, info: EditorInfo, item: object ) -> str:
        raise NotImplementedError( "abstract" )
    
    
    def translate( self, info: EditorInfo, values: List[object] ) -> object:
        raise NotImplementedError( "abstract" )


class FlagsEditor( AbstractFlagsEditor ):
    """
    Edits: Flags
    """
    
    
    def translate( self, info: EditorInfo, values: List[Flags] ) -> Flags:
        type_ = info.annotation.value
        
        result = type_( 0 )
        
        for value in values:
            result |= value
        
        return result
    
    
    def is_set( self, info: EditorInfo, query: Flags, value: Flags ) -> bool:
        return (value & query) == query
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        return info.annotation.is_directly_below( Flags )
    
    
    def get_items( self, info: EditorInfo ) -> Iterable[object]:
        return cast( Iterable[Flags], info.annotation.type_or_optional_type )
    
    
    def get_name( self, info: EditorInfo, item: Flags ) -> str:
        return item.name


class BoolEditor( AbstractEditor ):
    """
    Edits:  bool
            Optional[bool]
    """
    
    
    def __init__( self, info: EditorInfo ):
        self.option_align_left = info.messages.get( constants.OPTION_ALIGN_LEFT, False )
        self.option_radio = info.messages.get( constants.OPTION_BOOLEAN_RADIO, False )
        self.option_texts = info.messages.get( constants.OPTION_BOOLEAN_TEXTS, ("", "", "") )
        
        # Create frame
        layout = QHBoxLayout()
        layout.setContentsMargins( QMargins( 0, 0, 0, 0 ) )
        self.editor = QFrame()
        self.editor.setLayout( layout )
        
        if self.option_radio:
            self.using_radio = True
            self.radio_yes = QRadioButton()
            self.radio_yes.setText( self.option_texts[0] or "True" )
            self.radio_no = QRadioButton()
            self.radio_no.setText( self.option_texts[1] or "False" )
            editors = [self.radio_yes, self.radio_no]
            
            if info.annotation.is_optional:
                self.radio_neither = QRadioButton()
                self.radio_neither.setText( self.option_texts[2] or "None" )
                editors.append( self.radio_neither )
            else:
                self.radio_neither = None
        else:
            self.using_radio = False
            self.check_box = QCheckBox()
            self.check_box.stateChanged[int].connect( self.__on_checkbox_stateChanged )
            
            if info.annotation.is_optional:
                self.check_box.setTristate( True )
            
            editors = (self.check_box,)
        
        for editor in editors:
            layout.addWidget( editor )
            
            if not self.option_align_left:
                editor.setSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed )
        
        if self.option_align_left:
            layout.addItem( QSpacerItem( 1, 1, QSizePolicy.Expanding, QSizePolicy.Ignored ) )
        
        super().__init__( info, self.editor )
        
        self.set_value( None )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ):
        return info.annotation.is_directly_below_or_optional( bool )
    
    
    @exceptToGui()
    def __on_checkbox_stateChanged( self, state: int ):
        if state == Qt.PartiallyChecked:
            self.check_box.setText( self.option_texts[2] )
        elif state == Qt.Checked:
            self.check_box.setText( self.option_texts[0] )
        else:
            self.check_box.setText( self.option_texts[1] )
    
    
    def set_value( self, value: Optional[object] ) -> None:
        if self.using_radio:
            if value is None:
                if self.radio_neither is not None:
                    self.radio_neither.setChecked( True )
                else:
                    self.radio_yes.setChecked( False )
                    self.radio_no.setChecked( True )
            elif value:
                self.radio_yes.setChecked( True )
            else:
                self.radio_no.setChecked( True )
        else:
            if value is None:
                if self.info.annotation.is_optional:
                    self.check_box.setCheckState( Qt.PartiallyChecked )
                else:
                    self.check_box.setChecked( Qt.Unchecked )
            elif value:
                self.check_box.setChecked( Qt.Checked )
            else:
                self.check_box.setChecked( Qt.Unchecked )
            
            self.__on_checkbox_stateChanged( self.check_box.checkState() )
    
    
    def get_value( self ) -> Optional[bool]:
        if self.using_radio:
            if self.radio_yes.isChecked():
                return True
            elif self.radio_no.isChecked():
                return False
            elif self.info.annotation.is_optional:
                return None
            else:
                raise ValueError( "A selection must be made." )
        else:
            x = self.check_box.checkState()
            
            if x == Qt.PartiallyChecked:
                return None
            elif x == Qt.Checked:
                return True
            elif x == Qt.Unchecked:
                return False
            else:
                raise SwitchError( "self.editor.checkState()", x )


class FloatEditor( AbstractEditor ):
    """
    Edits:  float
    """
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ):
        return info.annotation.value is float
    
    
    def __init__( self, info: EditorInfo ):
        self.editor = QLineEdit()
        self.editor.setPlaceholderText( "0" )
        self.editor.setValidator( QDoubleValidator() )
        super().handle_changes( self.editor.textChanged[str] )
        super().__init__( info, self.editor, )
        self.set_value( None )
    
    
    def set_value( self, value: Optional[float] ) -> None:
        self.editor.setText( str( value ) if value else "0" )
    
    
    def get_value( self ) -> Optional[float]:
        text = self.editor.text()
        
        if not text:
            return 0
        
        return float( text )


class IntEditor( AbstractEditor ):
    """
    Edits:  int
    """
    
    
    def __init__( self, info: EditorInfo ) -> None:
        self.editor = QSpinBox()
        self.editor.setMaximum( 2147483647 )
        
        super().__init__( info, self.editor )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ):
        return info.annotation.is_directly_below( int )
    
    
    def set_value( self, value: int ) -> None:
        if value is None:
            value = 0
        
        self.editor.setValue( value )
    
    
    def get_value( self ) -> int:
        return self.editor.value()


class NoneEditor( AbstractEditor ):
    
    def __init__( self, info: EditorInfo ):
        editor = QWidget()
        super().__init__( info, editor )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        return info.annotation.value is None
    
    
    def get_value( self ) -> Optional[object]:
        return None
    
    
    def set_value( self, value: Optional[object] ):
        pass


class ReadonlyEditor( AbstractEditor ):
    """
    Edits:  flags.READ_ONLY
    """
    
    
    def __init__( self, info: EditorInfo ) -> None:
        self.editor = QLineEdit()
        self.editor.setReadOnly( True )
        super().__init__( info, self.editor )
        self.value = None
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        return info.annotation.is_mannotation_of( HReadonly )
    
    
    def set_value( self, value: object ) -> None:
        self.value = value
        self.editor.setText( str( value ) )
    
    
    def get_value( self ) -> object:
        return self.value
