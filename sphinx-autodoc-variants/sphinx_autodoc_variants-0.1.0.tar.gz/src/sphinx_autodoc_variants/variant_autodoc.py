"""
Provides the automatic documenter type for variants
"""

from sphinx.ext.autodoc import Documenter, ModuleDocumenter
from sphinx.ext.autodoc import ModuleLevelDocumenter, ClassLevelDocumenter
from sphinx.ext.autodoc import ClassDocumenter
from sphinx.ext.autodoc import FunctionDocumenter, MethodDocumenter
from sphinx.ext.autodoc import DocstringSignatureMixin
from sphinx.util.inspect import Signature

from variants.inspect import is_primary

__all__ = ['PrimaryFunctionDocumenter', 'PrimaryMethodDocumenter',
           'VariantFunctionDocumenter', 'VariantMethodDocumenter']

# For mypy typing
if False:  # pragma: nocover
    from typing import Any, Text # NOQA


class BasePrimaryDocumenter(Documenter, DocstringSignatureMixin):
    option_spec = ClassDocumenter.option_spec

    def format_args(self):
        # type: () -> Text
        # for primary functions, the relevant signature is __main_form__
        primary_func = self.get_attr(self.object, '__main_form__', None)

        if primary_func is None:
            # TODO: Should this be an error?
            return None

        sig = Signature(primary_func, bound_method=self.is_method)
        return sig.format_args()


class PrimaryFunctionDocumenter(BasePrimaryDocumenter, ModuleLevelDocumenter):
    objtype = 'primary_function'
    directivetype = 'function'
    is_method = False
    priority = 15

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        # type: (Any, Text, bool, Any) -> bool
        return is_primary(member)


class VariantFunctionDocumenter(PrimaryFunctionDocumenter):
    objtype = 'variant_function'
    directivetype = 'function'
    is_method = False
    priority = 14
    option_spec = FunctionDocumenter.option_spec

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        is_func = FunctionDocumenter.can_document_member(member, membername,
                                                         isattr, parent)
        return is_func and isinstance(parent, PrimaryFunctionDocumenter)

    format_args = FunctionDocumenter.format_args


class PrimaryMethodDocumenter(BasePrimaryDocumenter, ClassLevelDocumenter):
    objtype = 'primary_method'
    directivetype = 'method'
    is_method = True
    priority = 16

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        # type: (Any, Text, bool, Any) -> bool
        return is_primary(member) and not isinstance(parent, ModuleDocumenter)


class VariantMethodDocumenter(PrimaryMethodDocumenter):
    objtype = 'variant_method'
    directivetype = 'method'
    is_method = True
    priority = 15
    option_spec = MethodDocumenter.option_spec

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        is_meth = MethodDocumenter.can_document_member(member, membername,
                                                       isattr, parent)
        return is_meth and isinstance(parent, PrimaryMethodDocumenter)

    format_args = MethodDocumenter.format_args
