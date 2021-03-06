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
from zope.component import getUtility, getMultiAdapter
from zope.dublincore.interfaces import IDCTimes
from zope.app.component.hooks import getSite
from zope.app.component.interfaces import ISite
from zope.index.text.parsetree import ParseError
from zope.proxy import removeAllProxies
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.traversing.api import getParents, getPath

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
from zojax.content.textannotation.interfaces import ITextAnnotation

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
        request = self.request
        dc = IDCTimes(item)
        description = getMultiAdapter((item, request), ITextAnnotation).getText()
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
                'description': description,
                'url': self.getURL(item),
                'modified': dc.modified and self.formatter.format(dc.modified) or '---'}

        return info
    
    def getURL(self, item):
        request = self.request
        try:
            parents = getParents(item)
        except TypeError:
            return '#'
        def getItemParentThreads(item):
            res = []
            parents = []
            for parent in [item]+getParents(item):
                for shortcut in IShortcuts(parent, {}).items():
                    res.append(parents + [shortcut]+ getParents(shortcut))
                parents.append(parent)
            res.append(parents)
            def getUrl(items):
                items = filter(lambda y: not ISite.providedBy(y), items)
                items.reverse()
                return "%s/%s"%(absoluteURL(items[0], request), "/".join(map(lambda x: x.__name__, items[1:])))
            return map(lambda x: getUrl(x), res)
        contextURL = absoluteURL(self.context, self.request)
        try:
            return filter(lambda x: contextURL in x, getItemParentThreads(item))[0]
        except IndexError:
            return absoluteURL(item, request)