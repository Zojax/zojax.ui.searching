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
""" zojax.blogger tests

$Id$
"""
import os, unittest, doctest
from zope import interface, component, event
from zope import interface, schema
from zojax.content.type.item import PersistentItem
from zope.app.security.interfaces import IAuthentication
from zope.app.testing import functional
from zope.app.component.hooks import setSite
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
from zope.component._api import getUtility
from zope.lifecycleevent import ObjectCreatedEvent
from zope.schema.fieldproperty import FieldProperty
from zope.security.management import newInteraction, endInteraction
from zojax.catalog.catalog import Catalog, ICatalog
from zojax.content.type.interfaces import INameChooserConfiglet
from zojax.content.space.content import ContentSpace
from zojax.personal.space.manager import PersonalSpaceManager, IPersonalSpaceManager


zojaxUiSearchingLayer = functional.ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'zojaxUiSearchingLayer', allow_teardown=True)


class IContent(interface.Interface):
    title = schema.TextLine(
        readonly=False,
        title=u'Test Title',
        description=u'Test content title.',
        default=u'',
        missing_value=u'',
        required=True)


class Content(PersistentItem):
    interface.implements(IContent, )

    title = FieldProperty(IContent['title'])




def FunctionalDocFileSuite(*paths, **kw):
    layer = zojaxUiSearchingLayer

    globs = kw.setdefault('globs', {})
    globs['http'] = functional.HTTPCaller()
    globs['getRootFolder'] = functional.getRootFolder
    globs['sync'] = functional.sync

    kw['package'] = doctest._normalize_module(kw.get('package'))

    kwsetUp = kw.get('setUp')
    def setUp(test):
        functional.FunctionalTestSetup().setUp()

        newInteraction()

        root = functional.getRootFolder()
        setSite(root)
        sm = root.getSiteManager()
        sm.getUtility(INameChooserConfiglet).short_url_enabled = True

        # IIntIds
        root['ids'] = IntIds()
        sm.registerUtility(root['ids'], IIntIds)
        root['ids'].register(root)

        # catalog
        root['catalog'] = Catalog()
        sm.registerUtility(root['catalog'], ICatalog)

        # vontent
        root['content'] = Content()
        sm.registerUtility(root['content'], IContent)

        # space
        space = ContentSpace(title=u'Space')
        event.notify(ObjectCreatedEvent(space))
        root['space'] = space

        setattr(root, 'principal', getUtility(IAuthentication).getPrincipal('zope.mgr'))
        # people
        people = PersonalSpaceManager(title=u'People')
        event.notify(ObjectCreatedEvent(people))
        root['people'] = people
        sm.registerUtility(root['people'], IPersonalSpaceManager)

        endInteraction()

    kw['setUp'] = setUp

    kwtearDown = kw.get('tearDown')
    def tearDown(test):
        setSite(None)
        functional.FunctionalTestSetup().tearDown()

    kw['tearDown'] = tearDown

    if 'optionflags' not in kw:
        old = doctest.set_unittest_reportflags(0)
        doctest.set_unittest_reportflags(old)
        kw['optionflags'] = (old|doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)

    suite = doctest.DocFileSuite(*paths, **kw)
    suite.layer = layer
    return suite


def test_suite():
    return unittest.TestSuite((
            FunctionalDocFileSuite("testbrowser.txt"),
            ))
