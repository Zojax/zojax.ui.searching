##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
from zope import interface
from zope.component import getUtility
from zope.dublincore.interfaces import IDCTimes
from zope.app.component.hooks import getSite
from zope.app.component.interfaces import ISite
from zope.index.text.parsetree import ParseError
from zope.proxy import removeAllProxies
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.traversing.api import getParents

from z3c.form import button, form, interfaces

from zojax.batching.batch import Batch
from zojax.formatter.utils import getFormatter
from zojax.layoutform import Fields, PageletForm
from zojax.ownership.interfaces import IOwnership
from zojax.catalog.interfaces import ICatalogConfiglet
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.portal.interfaces import IPortal
from zojax.content.type.interfaces import IItem
from zojax.content.shortcut.interfaces import IShortcuts

from interfaces import _, ISearchForm, ISearchConfig


class SearchForm(PageletForm):

    ignoreContext = True
    fields = Fields(ISearchForm)
    fields['fromRoot'].mode = interfaces.HIDDEN_MODE

    label = _('Advanced search for content')
    description = _("This search form enables you to find content on "
                    "the site by specifying one or more search terms. "
                    "Remember that you can use the quick search anytime, "
                    "it's normally good enough, this search form is just "
                    "if you want to be more specific.")

    searchDone = False
    pageSize = 25
    results = ()
    method = 'get'
    currentLocation = False

    def update(self):
        if ISite.providedBy(self.context):
            self.fields = self.fields.omit('currentLocation')

        if ('fromRoot' not in self.request.form \
                and getUtility(ISearchConfig).fromRoot):
            self.request.form['%swidgets.fromRoot'%self.prefix] = ['true']

        super(SearchForm, self).update()

    @button.buttonAndHandler(_('Search'), name='search')
    def handleSearch(self, action):
        data, errors = self.extractData()
        if errors:
            IStatusMessage(self.request).add(self.formErrorsMessage, 'warning')
            return

        request = self.request
        catalog = getUtility(ICatalogConfiglet).catalog

        query = {}

        if data['text']:
            query['searchableText'] = data['text']

        if data['contentType']:
            query['type'] = {'any_of': data['contentType']}

        if data.get('currentLocation'):
            query['traversablePath'] = {'any_of': (self.context, )}
        if data.get('fromRoot'):
            portal = getSite()
            while portal is not None and not IPortal.providedBy(portal):
                portal = portal.__parent__
            if portal is not None:
                query['searchContext'] = portal
        elif not query:
            # we don't want to show all content we have
            # TODO: reword
            IStatusMessage(request).add(
                _(u'Please, specify a query that makes sense.'), 'warning')
            raise interfaces.WidgetActionExecutionError(
                            'text', interface.Invalid(
                    _(u'Please, specify a query that makes sense.')))

        query['isDraft'] = {'any_of': (False,)}
        try:
            results = catalog.searchResults(**query)
        except (ParseError, NotImplementedError), e:
            IStatusMessage(self.request).add(e, 'error')
            raise interfaces.WidgetActionExecutionError(
                'text', interface.Invalid(e))

        self.searchDone = True
        self.total = len(results)
        self.results = Batch(results, size=self.pageSize, request=request)
        self.formatter = getFormatter(request, 'humanDatetime', 'medium')
        self.currentLocation = data.get('currentLocation')

    def getInfo(self, item):
        dc = IDCTimes(item)
        item = IItem(item, None)
        ownership = IOwnership(item, None)
        if (ownership is None) or (not ownership.ownerId):
            owner = _('Unknown')
        else:
            try:
                owner = ownership.owner.title
            except:
                owner = ownership.ownerId

        info = {'owner': owner,
                'title': getattr(item, 'title') or item.__name__,
                'description': item.description,
                'url': self.getURL(item),
                'modified': dc.modified and self.formatter.format(dc.modified) or '---'}

        return info
    
    def getURL(self, item):
        parents = getParents(item)
        context = getattr(self.context, "__shortcut__", self.context)
        contextURL = absoluteURL(self.context, self.request)
        path = []
        for parent in [item] + parents:
            shortcuts = IShortcuts(parent, {}).items() or [parent]
            if context in shortcuts or self.context in shortcuts:
                return '%s/%s'%(contextURL, "/".join(reversed(path)))
            path.append(parent.__name__)
        return '%s/%s'%(contextURL, "/".join(reversed(path)))
