from Acquisition import aq_inner
from ftw.dashboard.portlets.recentlymodified import _
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.constants import USER_CATEGORY
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zope import schema
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.formlib import form
from zope.interface import implements


class IRecentlyModifiedPortlet(IPortletDataProvider):

    count = schema.Int(title=_(u"Number of items to display"),
                       description=_(u"How many items to list."),
                       required=True,
                       default=5)

    section = schema.Choice(
            title=_(u"label_section_path", default=u"Section"),
            description=_(u'help_section_path',
                          default=u"Search for section path, "
                                    "empty means search from root"),
            required=False,
            source=SearchableTextSourceBinder({'is_folderish': True},
                                              default_query='path:'))


class Assignment(base.Assignment):
    implements(IRecentlyModifiedPortlet)

    def __init__(self, count=5, section=None):
        self.count = count
        self.section = section

    @property
    def title(self):
        return _(u"title_recentlyModifed_portlet",
                 default=u"recently modified Portlet")


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('templates/recentlymodified.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        context = aq_inner(self.context)
        portal_state = getMultiAdapter(
            (context, self.request),
            name=u'plone_portal_state')
        self.anonymous = portal_state.anonymous()
        self.portal = portal_state.portal()
        self.portal_path = '/'.join(self.portal.getPhysicalPath())
        self.portal_url = portal_state.portal_url()
        self.typesToShow = portal_state.friendly_types()
        self.typesToShow = \
            [type_ for type_ in self.typesToShow if type_ not in ['Image', ]]

        plone_tools = getMultiAdapter(
            (context, self.request),
            name=u'plone_tools')
        self.catalog = plone_tools.catalog()

    def render(self):
        return xhtml_compress(self._template())

    def recent_items(self):
        return self._data()

    def get_contettype_class_for(self, brain):
        normalize = getUtility(IIDNormalizer).normalize
        return 'contenttype-%s' % normalize(brain.portal_type)

    @property
    def title(self):
        brains = self.catalog(
            path={'query': self.portal_path + str(self.data.section),
                  'depth': 0})
        if len(brains) == 1:
            section_title = brains[0].Title.decode('utf-8')
        else:
            section_title = self.portal.Title()
        if not isinstance(section_title, unicode):
            section_title = section_title.decode('utf-8')
        return section_title

    @memoize
    def _data(self):
        section = self.data.section
        if not section:
            section = ''
        limit = self.data.count
        references = self.context.portal_catalog({
            'path': {'query': self.portal_path + str(section),
                     'depth': 0, }})

        if references and len(references)>0 and \
            references[0].portal_type == "Topic":
            query = references[0].getObject().buildQuery()
        else:
            query = {
                'path': self.portal_path + str(section),
            }

        query["sort_on"] = 'modified'
        query["sort_order"] = 'reverse'
        query["sort_limit"] = limit
        if "portal_type" in query.keys():
            if type(query["portal_type"]) not in (list, tuple):
                query["portal_type"] = list(query["portal_type"])
            query["portal_type"] = filter(
                lambda a: a in self.typesToShow, query["portal_type"])
        else:
            query["portal_type"] = self.typesToShow


        return self.catalog(query)[:limit]

    def more_link(self):
        section = self.data.section
        if not section:
            section = ''
        references = self.context.portal_catalog({
            'path': {'query': self.portal_path + str(section),
                     'depth': 0, }})
        if references:
            if references[0].getObject().portal_type == "Topic":
                return '%s' % references[0].getURL()
            else:
                return '%s/recently_modified_view' % references[0].getURL()
        else:
            return '%s/recently_modified_view' % self.context.absolute_url()


class AddForm(base.AddForm):

    form_fields = form.Fields(IRecentlyModifiedPortlet)
    form_fields['section'].custom_widget = UberSelectionWidget
    label = _(u"Add recently modified Portlet")
    description = _(u"This portlet displays recently"
        u" modified content in a selected section.")

    def create(self, data):
        return Assignment(
            count=data.get('count', 5),
            section=data.get('section', ''))


class EditForm(base.EditForm):
    form_fields = form.Fields(IRecentlyModifiedPortlet)
    form_fields['section'].custom_widget = UberSelectionWidget
    label = _(u"Edit recently modified Portlet")
    description = _(u"This portlet displays recently" \
        u" modified content in a selected section.")


class AddPortlet(object):

    def __call__(self):
        # This is only for a 'recently modified'-user-portlet in dashboard
        # column 1 now, not at all abstracted
        column_manager = getUtility(IPortletManager, name='plone.dashboard1')
        membership_tool = getToolByName(self.context, 'portal_membership')
        userid = membership_tool.getAuthenticatedMember().getId()
        column = column_manager.get(USER_CATEGORY, {}).get(userid, {})
        id_base = 'recentlyModified'
        id_number = 0

        while id_base + str(id_number) in column.keys():
            id_number += 1
        portal_state = getMultiAdapter(
            (self.context, self.context.REQUEST),
            name=u'plone_portal_state')
        context_path = '/'.join(self.context.getPhysicalPath())
        portal = portal_state.portal()
        portal_path = '/'.join(portal.getPhysicalPath())
        relative_context_path = portal_path

        if context_path != portal_path:
            relative_context_path = context_path.replace(portal_path, '')
        column[id_base + str(id_number)] = Assignment(
            count=5,
            section=relative_context_path)

        request = getattr(self.context, 'REQUEST', None)
        if request is not None:

            title = self.context.Title() or self.context.id
            if isinstance(title, unicode):
                # The title is usually encoded in utf8, but in some dexterity
                # versions it may be unicode in certain circumstances.
                title = title.encode('utf-8')

            message = _(
                u"${title} added to dashboard.",
                mapping={'title': title.decode('utf8')})
            IStatusMessage(request).addStatusMessage(message, type="info")
        return self.context.REQUEST.RESPONSE.redirect(
            self.context.absolute_url())


class QuickPreview(BrowserView):
    """Quick preview
    """


class RecentlyModifiedView(BrowserView):
    """Shows all recently modified items
    """
