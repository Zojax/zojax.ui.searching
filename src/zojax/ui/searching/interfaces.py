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
from zope import interface, schema
from zope.i18nmessageid import MessageFactory
from zojax.widget.checkbox.field import CheckboxList

_ = MessageFactory('zojax.ui.searching')


class ISearchConfig(interface.Interface):
    """search config"""

    fromRoot = schema.Bool(
        title = _('Search from root portal'),
        description = _('If checked, search will be done from root portal'),
        required = False,
        default = False)


class ISearchConfiglet(ISearchConfig):
    """search configlet"""


class ISearchLocation(ISearchConfig):
    """search location"""

    currentLocation = schema.Bool(
            title = _('Search only current location'),
            description = _('If checked, only current location and below '
                            'will be searched instead of whole portal.'),
            required = False,
            default = True)


class ISearchForm(ISearchLocation):
    """ search form """

    text = schema.TextLine(
        title = _('Search Text'),
        description = _(u'For a simple text search, enter your search '
                        'term here.'),
        required = False) # TODO: shouldn't this be required?

    contentType = CheckboxList(
        title = _('Content type'),
        description = _('Return contents of a specific type.'),
        vocabulary = 'zojax.content.portalContent',
        horizontal = True,
        required = False)


class ISearchPortlet(ISearchLocation):
    """search portlet"""
    
    label = schema.TextLine(title=_(u'Label'),
                            required=False)

