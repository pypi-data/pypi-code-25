"""

    

"""

# Zope imports
from plone import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.component import getUtility, getUtilitiesFor
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFCore.interfaces import IFolderish, ISiteRoot

# Plone imports

from Products.Archetypes.Field import FileField
from Products.Archetypes.interfaces import IBaseContent
from plone.namedfile.interfaces import INamedFile
from plone.dexterity.content import DexterityContent
from plone.portlets.interfaces import IPortletManager              
from plone.portlets.interfaces import IPortletAssignment           
from plone.portlets.interfaces import IPortletAssignmentMapping    
from zope.component.hooks import setHooks, setSite, getSite
from urllib import quote
import transaction



class DeletePortlet(BrowserView):
    """
    """

  

    def __call__(self):
        pcurl = self.request.get('pcurl') #url of portletcontainer
        #vhmprefix = self.request.get('vhmprefix')
        #print '\n deletePortlet | pcurl: ' +pcurl + 'vhmprefix:' +vhmprefix+'\n'
        pman= self.request.get('pman') #manager_name
        id = self.request.get('id')  #portlet id 
        portal = api.portal.get()
        portlet_container = portal.unrestrictedTraverse(pcurl)
        manager = getUtility(IPortletManager, name=pman, context=portlet_container)
        assignment_mapping = getMultiAdapter((portlet_container, manager), IPortletAssignmentMapping)
        # import ipdb;ipdb.set_trace()
        for portlet in assignment_mapping:
            if portlet == id:
                del  assignment_mapping[portlet]
                transaction.commit()
                break                                    
        return self.request.response.redirect(
                self.context.absolute_url() + '/@@portlet-admin')
 