==============
Rating Package
==============

The rating package implements a rating system which can be plugged to any
content type.

  >>> from lovely import rating

Let's first create an object that can be rated:

  >>> import zope.annotation
  >>> import zope.interface

  >>> from lovely.rating.interfaces import (IRatable,
  ...                                       IRatingsManager,
  ...                                       IRatingDefinition)
  >>> class Application(object):
  ...     zope.interface.implements(zope.annotation.IAttributeAnnotatable,
  ...                               IRatable)
  ...     def __init__(self, name):
  ...         self.name = name
  ...
  ...     def __repr__(self):
  ...         return '<%s %r>' % (self.__class__.__name__, self.name)

  >>> kde = Application(u'KDE')

In order for an object to be ratable, it also must be annotatable. The easiest
is to make it attribute-annotatble. Now we register an adapter that can adapt
``IRatable`` providing objects to ``IRatingsManagers``.

  >>> import zope.component
  >>> zope.component.provideAdapter(rating.getRatingsManager)

  >>> from zope.annotation import attribute
  >>> zope.component.provideAdapter(attribute.AttributeAnnotations)


It is now trivial to get the ratings manager.

  >>> manager = IRatingsManager(kde)
  >>> manager
  <RatingsManager for <Application u'KDE'>>

The ratings manager manages all ratings that can be made for an object. For
example, you might want to be able to rate an application for usability,
functionality, stability and documentation. The rating manager would then
manage the ratings of those four points of interest.

Before we can rate the application, we have to create a rating definition for
each of the four points of interest. To do this, we first have to
create a score system for the ratings:

  >>> from decimal import Decimal
  >>> from schooltool.requirement import scoresystem

  >>> fiveSteps = scoresystem.DiscreteValuesScoreSystem(
  ...    u'Five Steps', u' A five step scoring system',
  ...    [(u'Awesome', Decimal(4)), (u'Good', Decimal(3)),
  ...     (u'Okay', Decimal(2)), (u'Poor', Decimal(1)),
  ...     (u'Crap', Decimal(0))])

Note: For more details on score systems see the documentation in the
``schooltool.requirement`` package.

Now we can create the rating definition and register it as a utility:

  >>> usability = rating.RatingDefinition(
  ...     u'Usability', fiveSteps, u'How is the usability of the application?')
  >>> zope.component.provideUtility(
  ...     usability, IRatingDefinition, name='usability')

We are finally ready to rate KDE for usability:

  >>> manager.rate('usability', u'Good', u'srichter')
  >>> manager.rate('usability', u'Okay', u'kartnaller')

The ``rate()`` method's arguments are the id of the rating definition, the
value and the user id of the user making the rating. Note that you cannot add
invalid ratings:

  >>> manager.rate('usability', u'Divine', u'jodok')
  Traceback (most recent call last):
  ...
  ValueError: Invalid rating value u'Divine' for 'usability'.

  >>> manager.rate('stability', u'Awesome', u'jodok')
  Traceback (most recent call last):
  ...
  ValueError: No rating definition named 'stability' found.

The rest of the rating manager API deals with retrieving the ratings. First
you can ask for all ratings made for a rating definition:

  >>> sorted([rating.__repr__() for rating in manager.getRatings('usability')])
  ["<Rating u'Good' by u'srichter'>", "<Rating u'Okay' by u'kartnaller'>"]

You can also ask for the rating of a particular user:

  >>> manager.getRating('usability', u'srichter')
  <Rating u'Good' by u'srichter'>

The rating has the following attributes:

  >>> manager.getRating('usability', u'srichter').value
  u'Good'
  >>> manager.getRating('usability', u'srichter').user
  u'srichter'
  >>> manager.getRating('usability', u'srichter').timestamp
  datetime.datetime(...)

Note that the rating object is read-only:

  >>> manager.getRating('usability', u'srichter').value = u'Awesome'
  Traceback (most recent call last):
  ...
  AttributeError: can't set attribute

A new rating can be given by rating the application again:

  >>> manager.rate('usability', u'Awesome', u'srichter')
  >>> manager.getRating('usability', u'srichter')
  <Rating u'Awesome' by u'srichter'>

Ratings are removed using the following:

  >>> manager.rate('usability', u'Crap', u'badcarma')
  >>> manager.getRating('usability', u'badcarma')
  <Rating u'Crap' by u'badcarma'>

  >>> manager.remove('usability', 'badcarma')
  >>> manager.getRating('usability', u'badcarma')

Finally, the manager also provides some basic statistical features:

  >>> manager.computeAverage('usability')
  Decimal("3")

  >>> manager.countScores('usability')
  [((u'Awesome', Decimal("4")), 1),
   ((u'Good', Decimal("3")), 0),
   ((u'Okay', Decimal("2")), 1),
   ((u'Poor', Decimal("1")), 0),
   ((u'Crap', Decimal("0")), 0)]

