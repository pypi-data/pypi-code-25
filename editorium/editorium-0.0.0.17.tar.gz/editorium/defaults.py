from typing import List, cast

from mhelper import reflection_helper, array_helper


__default_editorium = None
__pending_editors = []  # type: List


def default_editorium():
    """
    Obtains the default editorium, creating it if it doesn't already exist.
    :return: An object of class `Editorium`.
    :rtype: Editorium  
    """
    global __default_editorium, __pending_editors
    
    if __default_editorium is None:
        from editorium.default_editors import BoolEditor, StringCoercionEnumEditor, FlagsEditor, FloatEditor, IntEditor, FilenameEditor, StringEditor, ListTEditor, NullableEditor, FallbackEditor, ReadonlyEditor, AnnotationEditor, PasswordEditor, NoneEditor
        from editorium.bases import Editorium
        from editorium.bases import AbstractEditorType

        __default_editorium = Editorium()
        __default_editorium.editors.append( ReadonlyEditor )  # must be first
        __default_editorium.editors.append( FilenameEditor )
        __default_editorium.editors.append( AnnotationEditor )
        __default_editorium.editors.append( BoolEditor )
        __default_editorium.editors.append( StringCoercionEnumEditor )
        __default_editorium.editors.append( FlagsEditor )
        __default_editorium.editors.append( FloatEditor )
        __default_editorium.editors.append( IntEditor )
        __default_editorium.editors.append( StringEditor )
        __default_editorium.editors.append( PasswordEditor )
        __default_editorium.editors.append( ListTEditor )
        __default_editorium.editors.append( NullableEditor )
        __default_editorium.editors.append( NoneEditor )
        __default_editorium.editors.append( FallbackEditor )  # must be last
        
        for editor_or_function in __pending_editors:
            for editor in array_helper.as_sequence( reflection_helper.dedelegate( editor_or_function, AbstractEditorType ) ):
                __default_editorium.register( editor )
        
        __pending_editors = cast( List, None )
    
    return __default_editorium


def register( editor_or_function ) -> None:
    """
    Deferred registration for an editor or editors with the default editorium.
    
    If the default editorium is not yet created, the registration will be deferred until it is created.
    This allows the programmer to register editors at software start, but only load Qt if the editors will actually be used.
    
    If the editor-type also requires Qt to be loaded, a function can be provided that will be called instead.
    
    :param editor_or_function: Either:
                                    * An editor (AbstractEditor-derived class. The class, not an instance.)
                                    * A sequence of editors (must be `list` or `tuple`)
                                    * A function returning an editor
                                    * A function returning a list of editors
                                    * Nb. A list of functions is not accepted 
    """
    if __default_editorium is not None:
        from editorium.bases import AbstractEditorType
        for editor in array_helper.as_sequence( reflection_helper.dedelegate( editor_or_function, AbstractEditorType ) ):
            __default_editorium.register( editor )
    else:
        __pending_editors.append( editor_or_function )
