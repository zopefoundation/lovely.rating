##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""Ratings Manager

$Id$
"""
__docformat__ = "reStructuredText"

import itertools
import persistent

from zope import annotation
import zope.component
import zope.interface
import zope.event

from BTrees import OOBTree

from zope.app.container.contained import ObjectAddedEvent, ObjectRemovedEvent

from zope.app.container import contained

from lovely.rating import IRatable, IRatingsManager, IRatingDefinition, rating

import interfaces


class RatingsManager(contained.Contained, persistent.Persistent):
    zope.interface.implements(IRatingsManager)
    zope.component.adapts(IRatable)

    def __init__(self):
        self._storage = OOBTree.OOBTree()

    def _getDefinition(self, id):
        defn = zope.component.queryUtility(IRatingDefinition,
                                           context=self,
                                           name=id)
        if defn is None:
            raise ValueError('No rating definition named %r found.' % id)
        return defn

    def rate(self, id, value, user):
        """See interfaces.IRatingsManager"""
        defn = self._getDefinition(id)

        if not defn.scoreSystem.isValidScore(value):
            raise ValueError('Invalid rating value %r for %r.' %(value, id))

        if id not in self._storage:
            self._storage[id] = OOBTree.OOBTree()
            contained.contained(self._storage[id], self._storage, id)
        existing = self._storage[id].get(user)
        if existing is not None and existing.value == value:
            # do nothing if no change
            return False
        value = rating.Rating(id, value, user)
        self._storage[id][user] = value
        if existing is None:
            zope.event.notify(interfaces.RatingAddedEvent(
                                        id, self.__parent__, user, value))
        else:
            zope.event.notify(interfaces.RatingChangedEvent(
                                        id, self.__parent__, user, value))
        return True

    def remove(self, id, user):
        """See interfaces.IRatingsManager"""
        # Just get the definition to make sure it exists.
        defn = self._getDefinition(id)

        if id not in self._storage or user not in self._storage[id]:
            return False
        value = self._storage[id][user]
        zope.event.notify(
                    interfaces.RatingRemovedEvent(id, self.__parent__, user))
        del self._storage[id][user]
        if len(self._storage[id]) == 0:
            del self._storage[id]
        return True

    def getRatings(self, id, dtMin=None, dtMax=None):
        """See interfaces.IRatingsManager"""
        # Just get the definition to make sure it exists.
        defn = self._getDefinition(id)
        ratings = list(self._storage.get(id, {}).values())
        f = None
        if dtMin is not None:
            if dtMax is not None:
                f = lambda r: r.timestamp>=dtMin and r.timestamp<=dtMax
            else:
                f = lambda r: r.timestamp>=dtMin
        elif dtMax is not None:
            f = lambda r: r.timestamp<=dtMax
        if f:
            ratings = itertools.ifilter(f, ratings)
        return list(ratings)

    def getRating(self, id, user):
        """See interfaces.IRatingsManager"""
        # Just get the definition to make sure it exists.
        defn = self._getDefinition(id)
        if id not in self._storage or user not in self._storage[id]:
            return

        return self._storage[id][user]

    def computeAverage(self, id, dtMin=None, dtMax=None):
        """See interfaces.IRatingsManager"""
        # Just get the definition to make sure it exists.
        defn = self._getDefinition(id)
        ratings = list(self.getRatings(id, dtMin, dtMax))
        total = sum([defn.scoreSystem.getNumericalValue(rating.value)
                    for rating in ratings])
        try:
            return total/len(ratings)
        except ZeroDivisionError:
            return -1

    def countScores(self, id, dtMin=None, dtMax=None):
        """See interfaces.IRatingsManager"""
        defn = self._getDefinition(id)
        ratings = list(self._storage.get(id, {}).values())
        value_count = {}
        for rating in ratings:
            value_count.setdefault(rating.value, 0)
            value_count[rating.value] += 1

        return [(score, value_count.get(score[0], 0))
                for score in defn.scoreSystem.scores]

    def countAmountRatings(self, id, dtMin=None, dtMax=None):
        """See interfaces.IRatingManager"""
        ratings = list(self._storage.get(id, {}).values())
        return len(ratings)

    def __repr__(self):
        return '<%s for %r>' %(self.__class__.__name__, self.__parent__)


getRatingsManager = annotation.factory(RatingsManager)
