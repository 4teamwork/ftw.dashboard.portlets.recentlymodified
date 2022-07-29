from Acquisition import aq_inner
from ftw.dashboard.portlets.recentlymodified import _
from plone import api
from plone.app.portlets.portlets import base
from plone.app.portlets.storage import UserPortletAssignmentMapping
from plone.app.uuid.utils import uuidToObject
from plone.app.vocabularies.catalog import CatalogSource
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.constants import USER_CATEGORY
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zope import schema
from zope.component import getMultiAdapter
from zope.component import getUtility
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
        source=CatalogSource(is_folderish=True))


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
    portletClass = 'portletRecent'

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        context = aq_inner(self.context)
        portal_state = getMultiAdapter(
            (context, self.request),
            name=u'plone_portal_state')
        registry = getUtility(IRegistry)
        types_to_exclude = registry.get(
            'ftw.dashboard.portlets.recentlymodified.types_to_exclude', [])
        self.exclude_members_folder = registry.get(
            'ftw.dashboard.portlets.recentlymodified.exclude_members_folder',
            True)
        self.anonymous = portal_state.anonymous()
        self.portal = portal_state.portal()
        self.portal_path = '/'.join(self.portal.getPhysicalPath())
        self.portal_url = portal_state.portal_url()
        self.typesToShow = portal_state.friendly_types()
        self.typesToShow = \
            [type_ for type_ in self.typesToShow if type_ not in types_to_exclude]

        plone_tools = getMultiAdapter(
            (context, self.request),
            name=u'plone_tools')
        self.catalog = plone_tools.catalog()

    def render(self):
        return xhtml_compress(self._template())

    @memoize
    def recent_items(self):
        return self._data()

    def get_contettype_class_for(self, brain):
        normalize = getUtility(IIDNormalizer).normalize
        return 'contenttype-%s' % normalize(brain.portal_type)

    @property
    def title(self):
        section = uuidToObject(self.data.section)
        if not section:
            return self.portal.Title().decode('utf-8')
        else:
            return section.Title().decode('utf-8')

    def _data(self):
        section = uuidToObject(self.data.section)
        if not section:
            section = self.portal
        limit = self.data.count
        references = self.context.portal_catalog({
            'path': {'query': '/'.join(section.getPhysicalPath()),
                     'depth': 0, }})

        if references and len(references) > 0 and \
                references[0].portal_type == "Collection":
            query = references[0].getObject().getQuery() or {}
        else:
            query = {
                'path': '/'.join(section.getPhysicalPath()),
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

        items = self.catalog(query)

        # Remove items inside the members folder, they must not be displayed
        # in the portlet.
        if self.exclude_members_folder:
            membership_tool = getToolByName(self.portal, 'portal_membership')
            members_folder = membership_tool.getMembersFolder()
            if members_folder:
                members_folder_path = members_folder.getPhysicalPath()
                members_folder_path = '/'.join(members_folder_path)
                items = [item for item in items
                         if not item.getPath().startswith(members_folder_path)]

        return items[:limit]

    def more_link(self):
        section = uuidToObject(self.data.section)
        if not section:
            section = self.portal
        references = self.context.portal_catalog({
            'path': {'query': '/'.join(section.getPhysicalPath()),
                     'depth': 0, }})
        if references:
            if references[0].getObject().portal_type == "Collection":
                return '%s' % references[0].getURL()
            else:
                return '%s/recently_modified_view' % references[0].getURL()
        else:
            return '%s/recently_modified_view' % self.context.absolute_url()


class AddForm(base.AddForm):
    schema = IRecentlyModifiedPortlet
    label = _(u"Add recently modified Portlet")
    description = _(u"This portlet displays recently"
                    u" modified content in a selected section.")

    def create(self, data):
        return Assignment(
            count=data.get('count', 5),
            section=data.get('section', ''))


class EditForm(base.EditForm):
    schema = IRecentlyModifiedPortlet
    label = _(u"Edit recently modified Portlet")
    description = _(u"This portlet displays recently"
                    u" modified content in a selected section.")


class AddPortlet(object):

    def __call__(self):
        # This is only for a 'recently modified'-user-portlet in dashboard
        # column 1 now, not at all abstracted
        dashboard_name = 'plone.dashboard1'
        column = getUtility(IPortletManager, name=dashboard_name)
        membership_tool = getToolByName(self.context, 'portal_membership')
        userid = membership_tool.getAuthenticatedMember().getId()
        category = column.get(USER_CATEGORY, None)

        manager = category.get(userid, None)
        if manager is None:
            manager = UserPortletAssignmentMapping(
                manager=dashboard_name,
                category=USER_CATEGORY,
                name=userid)
            category[userid] = manager

        id_base = 'recentlyModified'
        id_number = 0

        while id_base + str(id_number) in manager.keys():
            id_number += 1

        uid = ''
        if api.portal.get() != self.context:
            uid = IUUID(self.context)
        manager[id_base + str(id_number)] = Assignment(
            count=5,
            section=uid)

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
    """Shows recently modified items of friendly types. Optionally the
    contents from the members folder is excluded.
    """
    def get_data(self):
        # Get config options.
        registry = getUtility(IRegistry)
        types_to_exclude = registry.get(
            'ftw.dashboard.portlets.recentlymodified.types_to_exclude', [])
        exclude_members_folder = registry.get(
            'ftw.dashboard.portlets.recentlymodified.exclude_members_folder',
            True)

        # Get info about the portal.
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal = portal_state.portal()
        portal_path = '/'.join(portal.getPhysicalPath())

        # Put together the query.
        types_to_show = portal_state.friendly_types()
        types_to_show = [type_ for type_ in types_to_show
                         if type_ not in types_to_exclude]

        query = {'path': portal_path, 'sort_on': 'modified',
                 'sort_order': 'reverse', 'portal_type': types_to_show}

        # Get the data.
        catalog = getToolByName(self.context, 'portal_catalog')
        data = catalog(query)

        # Optionally remove items inside the members folder.
        if exclude_members_folder:
            membership_tool = getToolByName(portal, 'portal_membership')
            members_folder = membership_tool.getMembersFolder()
            if members_folder:
                members_folder_path = members_folder.getPhysicalPath()
                members_folder_path = '/'.join(members_folder_path)
                data = [item for item in data
                        if not item.getPath().startswith(members_folder_path)]

        return data
