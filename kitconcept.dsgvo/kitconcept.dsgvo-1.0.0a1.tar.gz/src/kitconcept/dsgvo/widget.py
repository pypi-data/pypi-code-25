# -*- coding: utf-8 -*-
from plone.app.z3cform.widget import SingleCheckBoxBoolWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IBool

from kitconcept.dsgvo.interfaces import IDsgvoSingleCheckBoxBoolWidget
from kitconcept.dsgvo.interfaces import IKitconceptDsgvoLayer
from kitconcept.dsgvo.util import dsgvo_translate


@implementer_only(IDsgvoSingleCheckBoxBoolWidget)
class DsgvoSingleCheckBoxBoolWidget(SingleCheckBoxBoolWidget):
    """
    Single Input type checkbox widget implementation that renders
    html in the label and help and interpolates the portal url and
    site name
    """

    klass = u'single-checkbox-bool-widget'

    @SingleCheckBoxBoolWidget.label.setter
    def label(self, value):
        self._label = dsgvo_translate(value, self.request)

    @SingleCheckBoxBoolWidget.description.setter
    def description(self, value):
        self._description = dsgvo_translate(value, self.request)


@adapter(IBool, IKitconceptDsgvoLayer)
@implementer(IFieldWidget)
def DsgvoSingleCheckBoxBoolFieldWidget(field, request):
    """IFieldWidget factory for CheckBoxWidget."""
    return FieldWidget(field, DsgvoSingleCheckBoxBoolWidget(request))
