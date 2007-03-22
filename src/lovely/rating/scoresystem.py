##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
__docformat__ = "reStructuredText"

from zope import interface

from lovely.rating import IScoreSystem


class SimpleScoreSystem(object):
    interface.implements(IScoreSystem)

    def __init__(self, title, description, scores):
        self.title = title
        self.description = description
        self.scores = scores

    def isValidScore(self, value):
        return value in dict(self.scores)

    def getNumericalValue(self, value):
        return dict(self.scores)[value]

