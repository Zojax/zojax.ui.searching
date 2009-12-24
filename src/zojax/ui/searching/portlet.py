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
""" Search portlet

$Id$
"""
from zojax.layout.interfaces import IPagelet
from zope.traversing.browser import absoluteURL
from zope.app.component.interfaces import ISite


class SearchPortlet(object):

    def update(self):
        super(SearchPortlet, self).update()

        context = self.context
        while IPagelet.providedBy(context):
            context = context.__parent__

        self.isSite = ISite.providedBy(context)
        self.contextUrl = absoluteURL(context, self.request)
