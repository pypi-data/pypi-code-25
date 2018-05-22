# -*- coding: utf-8 -*-
"""MLS Plone Embedding Control Panel."""

from plone.app.registry.browser import controlpanel
from plone.registry.interfaces import IRegistry
from plone.z3cform import layout
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ps.plone.mls import _
from ps.plone.mls import interfaces
from z3c.form import field
from zope.component import getUtility
from zope.interface import implementer


class SelfHealingRegistryEditForm(controlpanel.RegistryEditForm):
    """Registers the schema if an error occured."""

    def getContent(self):
        registry = getUtility(IRegistry)
        try:
            return registry.forInterface(  # noqa
                self.schema,
                prefix=self.schema_prefix,
            )
        except KeyError:
            self.ignoreContext = True
            self.fields = field.Fields()
            registry.registerInterface(self.schema)
            self.status = _(
                u'Registry has been updated. Please reload this page.',
            )
            return None


class MLSBaseSettingsControlPanel(SelfHealingRegistryEditForm):
    schema = interfaces.IMLSBaseSettings
    label = _(u'Propertyshelf MLS Base Settings')
    description = _(
        u'This MLS configuration will be used as the default for this '
        u'Plone site. You can add more MLS configurations by activating '
        u'the local MLS settings on any content item within the site.',
    )


class MLSBaseSettingsFormWrapper(layout.FormWrapper):
    """Use this form as the layout wrapper to get the controlpanel layout."""

    index = ViewPageTemplateFile('controlpanel_layout_base.pt')


MLSBaseSettingsPanelView = layout.wrap_form(
    MLSBaseSettingsControlPanel,
    MLSBaseSettingsFormWrapper,
)


class MLSUISettingsControlPanel(SelfHealingRegistryEditForm):
    schema = interfaces.IMLSUISettings
    label = _(u'Propertyshelf MLS UI Settings')
    description = _(
        u'Adjust the UI settings for this Plone site.',
    )


class MLSUISettingsFormWrapper(layout.FormWrapper):
    """Use this form as the layout wrapper to get the controlpanel layout."""

    index = ViewPageTemplateFile('controlpanel_layout_ui.pt')


MLSUISettingsPanelView = layout.wrap_form(
    MLSUISettingsControlPanel,
    MLSUISettingsFormWrapper,
)


@implementer(interfaces.IGlobalContactSettingsForm)
class MLSContactInfoSettingsControlPanel(SelfHealingRegistryEditForm):
    schema = interfaces.IMLSContactInfoSettings
    label = _(u'Propertyshelf MLS Contact Information Settings')
    description = _(
        u'The contact information provided will be used as the default for '
        u'this Plone site. You can add more specific MLS contact '
        u'information by activating the local MLS contact settings on any '
        u'content item within the site.',
    )


class MLSContactInfoSettingsFormWrapper(layout.FormWrapper):
    """Use this form as the layout wrapper to get the controlpanel layout."""

    index = ViewPageTemplateFile('controlpanel_layout_contact_info.pt')


MLSContactInfoSettingsPanelView = layout.wrap_form(
    MLSContactInfoSettingsControlPanel,
    MLSContactInfoSettingsFormWrapper,
)


class MLSCachingSettingsControlPanel(SelfHealingRegistryEditForm):
    schema = interfaces.IMLSCachingSettings
    label = _(u'Propertyshelf MLS Caching Settings')
    description = _(u'Adjust the MLS caching behhavior for this Plone site.')


class MLSCachingSettingsFormWrapper(layout.FormWrapper):
    """Use this form as the layout wrapper to get the controlpanel layout."""

    index = ViewPageTemplateFile('controlpanel_layout_caching.pt')


MLSCachingSettingsPanelView = layout.wrap_form(
    MLSCachingSettingsControlPanel,
    MLSCachingSettingsFormWrapper,
)
