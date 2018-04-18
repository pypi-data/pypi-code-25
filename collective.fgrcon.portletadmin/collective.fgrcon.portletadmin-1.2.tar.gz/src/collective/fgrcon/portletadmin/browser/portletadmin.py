"""
??
    

"""

# Zope imports
from plone import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import ComponentLookupError
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
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.portlets.interfaces import IPortletAssignment           
from plone.portlets.interfaces import IPortletAssignmentMapping    
from zope.component.hooks import setHooks, setSite, getSite
from urllib import quote




def _recurse_content(context, all_content):
        if IFolderish.providedBy(context):            
            # import ipdb; ipdb.set_trace();
            for id, item in context.contentItems():
                all_content.append(item)
                _recurse_content(item, all_content)

def move_form(scont,sman, sid,vhmprefix):
    #import ipdb; ipdb.set_trace();
    sconturl =  scont.absolute_url_path()
    tooltip1 = '<a href="#" data-toggle="tooltip" class="pat-tooltip" '\
            'title="Target URL (relative).\n Leave as is when moving to other '\
            'portletmanager within same container/item">'\
            '<img width="20" src="++resource++collective.fgrcon.portletadmin/info.png">'\
            '</a>'
    #onchange = 'alert(`getting ....`)'
    onchange = 'javascript:get_portletmanagers(`{}`, `{}`, `{}`)'.format(sconturl.replace('/',''), sid,vhmprefix) 
    out = '<div style="width:100%;" ><form method="post" action = {}'\
          '/@@move-portlet>'.format(api.portal.get().absolute_url())
    out +='<label class="fgrportletadm" style="width:45%" for="target-document">'\
          ' {}Target: <input class="fgrportletadm" type="text" '\
          'id = "p-{}-{}"'\
          'name="target-document" value="{}" onchange="{}"></label>'\
          .format(tooltip1, sconturl.replace('/',''), sid, sconturl , onchange)
    out +='<label class="fgrportletadm" style="width:40%" for="sel-managers">Portletmanager:'\
          '<select class="fgrportletadm" name="sel-managers" '\
          'id = "sel-{}-{}">'.format(sconturl.replace('/',''), sid)
    for manager_name, manager in getUtilitiesFor(IPortletManager, context=scont):
        if  'plone.dashboard' not in manager_name and manager_name != sman:
        #import ipdb; ipdb.set_trace()
            out += ' <option class="fgrportletadm" value="{}">{}</option>'\
            .format(manager_name, manager_name)
    out += '</select></label>'
    out += '<input class="fgrportletadm" "width: 2%;display:inline-block" '\
        'type="submit" value="Move">'
    out += '<input type="hidden" name="scont" value="{}">'.format(sconturl)
    out += '<input type="hidden" name="sman" value="{}">'.format(sman)
    out += '<input type="hidden" name="sid" value="{}">'.format(sid)
    out += '<input type="hidden" name="vhmprefix" value="{}">'.format(vhmprefix)
    out += '</form></div>'
        
    return out

class PortletAdmin(BrowserView):
    """
    You can call this view by
    1) Starting Plone in debug mode (console output available)

    2) Visit site.com/[.../]@@portlets-admin URL

    """

    def xrender(self):
        out = ''
        portal = api.portal.get()
        context = self.context
        vhmprefix=''
        if not portal.getPhysicalPath()[1] in portal.absolute_url_path():
            vhmprefix = "/"+portal.getPhysicalPath()[1]  
        catalog = portal.portal_catalog
        if context == portal:
            all_content = catalog(show_inactive=True, 
                  language="ALL") #, object_provides=ILocalPortletAssignable.__identifier__)
            all_content = [ content.getObject() for content in all_content ]
            all_content.insert(0,context)    
        else:
            all_content = []
            all_content.append(context)
            _recurse_content(context,all_content)

        # browse all content recursively
        ci=0
        currcont =''
        for cont in all_content:
            ci += 1
            conturl = cont.absolute_url_path()
            if cont != currcont:                
                cheader = "<h2> {} ({})</h2>".format(
                         conturl,
                        cont.portal_type)
                currcont = cont
                ccount = 0
            mi = 0
            curman = ""
            for manager_name, manager in getUtilitiesFor(IPortletManager, context=cont):
                if manager_name != curman:                
                    mheader = '<h3 class="fgrportletadm-managr">{}</h3>'.format(manager_name)
                    curman = manager_name
                    mcount = 0                
                try:
                    mapping = getMultiAdapter((cont, manager), IPortletAssignmentMapping)                    
                    for mapitem in mapping.items():
                        portlet_id = mapitem[0]
                        ass = mapitem[1]
                        ccount += 1
                        mcount += 1
                        if ccount == 1:
                            out += cheader
                            out += '<a class="fgrportletadm-view" href="{}">view...</a>'\
                            .format(conturl)
                        if mcount == 1:
                            out += mheader
                        out += '<div class="fgrportletadm"><h3>{} ({})</h3>'\
                        .format(portlet_id,unicode(getattr(ass,'header', '')))
                        param1 ="pcurl={}&pman={}&id={}"\
                        .format(vhmprefix+conturl,
                                manager_name,portlet_id) #,str(ass))
                        # edit link
                        out += '<p><a class="fgrportletadm-edit" href="{}/++contextportlets++{}/{}/edit">Edit</a>'.format(vhmprefix+conturl, manager_name, portlet_id)
                        # Remove portlet link
                        out += ' | Be careful, Remove cannot be undone: <a class="fgrportletadm-delete" href="{}/@@delete-portlet?{}">Remove </a></p>'.format(api.portal.get().absolute_url(), param1)
                        out += move_form(cont, curman, portlet_id, vhmprefix )
                        out += '</div>'
                except ComponentLookupError as e:
                    #import ipdb; ipdb.set_trace()
                    #ignore assigned discussion items  
                    if not 'plone.app.discussion.comment' in  str(e.args[0]):
                        raise
                    else:
                        pass
        return out
 