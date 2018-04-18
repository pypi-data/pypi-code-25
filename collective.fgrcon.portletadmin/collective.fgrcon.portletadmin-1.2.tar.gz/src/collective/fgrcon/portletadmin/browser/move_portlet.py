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

class NoValidContainerException(Exception):
    pass

class MovePortlet(BrowserView):
    """
    """
    
    def __call__(self):
        vhmprefix = self.request.form['vhmprefix']
        tcont = vhmprefix + self.request.form['target-document'] #targetcontainer
        tman = self.request.form['sel-managers'] # target manager
        scont = vhmprefix + self.request.form['scont'] #source container
        sman= self.request.form['sman'] #  source manager
        sid= self.request.form['sid'] #  source portlet id       
        portal = api.portal.get()
        s_portlet_container = portal.unrestrictedTraverse(scont)
        try:
            t_portlet_container = portal.unrestrictedTraverse(tcont)
        except KeyError as error:
            raise NoValidContainerException("%s is not a valid container!"%tcont)
        
        s_manager = getUtility(IPortletManager, name=sman, context = s_portlet_container)
        t_manager = getUtility(IPortletManager, name=tman, context = t_portlet_container)

        s_assignment_mapping = getMultiAdapter((s_portlet_container, s_manager), IPortletAssignmentMapping)
        t_assignment_mapping = getMultiAdapter((t_portlet_container, t_manager), IPortletAssignmentMapping)
        
        assigm = None
        for portlet in s_assignment_mapping:
            if portlet == sid:
                t_assignment_mapping[portlet] = s_assignment_mapping[portlet]
                del s_assignment_mapping[portlet]
                transaction.commit()
                break  
#        import ipdb;ipdb.set_trace()            =                          
        return self.request.response.redirect(
               self.context.absolute_url() + '/@@portlet-admin')
        
class GetAvailablePOrtletManagers(BrowserView):
    def __call__(self):
        portal = api.portal.get()
        tcont = self.request['tcont']
        try:
            t_portlet_container = portal.unrestrictedTraverse(tcont)
            out = ''
            for manager_name, manager in getUtilitiesFor(IPortletManager, t_portlet_container):
                if  'plone.dashboard' not in manager_name:
                    out += ' <option class="fgrconutils" value="{}">{}</option>'\
                           .format(manager_name, manager_name)
            return out
        except KeyError as error:
            raise NoValidContainerException("%s is not a valid container!" %tcont)
 