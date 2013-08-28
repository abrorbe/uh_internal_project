"""
.. module:: srsconnector.routers
   :synopsis: SRS Connector Database Routers.

.. moduleauthor:: Kyle Dodson <kdodson@caloply.edu>
.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from .settings import ALIAS, MODELS, APP_NAME


class SRSRouter(object):
    """ A database router to control interactions with the EnterpriseWizard
    REST interface.

    This router must be added to the 'DATABASE_ROUTERS' list in the project
    settings.

    The "MODELS" list defined in the application settings define which models are
    handled by the router. If a new RMS model is created it must be added to that
    list.

    This router supports reads, writes, and relations and disables "syncdb" for
    the models listed in "SRS_MODELS".

    """

    def _app(self, model):
        """ A shortcut to retrieve the provided model's application label.

        :param model: A model instance from which to retrieve information.
        :type model: model
        :returns: The provided model's app label.

        """

        return model._meta.app_label

    def _mod(self, model):
        """ A shortcut to retrieve the provided model's module name, a lower-cased version of its object name.

        :param model: A model instance from which to retrieve information.
        :type model: model
        :returns: The provided model's module name.

        """

        return model._meta.module_name

    def db_for_read(self, model, **hints):
        """Routes database read requests to the database only if the requested model belongs to a model in this application's MODELS list."""

        if self._app(model) == APP_NAME and self._mod(model) in MODELS:
            return ALIAS
        return None

    def db_for_write(self, model, **hints):
        """Routes database write requests to the database only if the requested model belongs to a model in this application's MODELS list."""

        if self._app(model) == APP_NAME and self._mod(model) in MODELS:
            return ALIAS
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Provides no constraints on relationships."""

        return None

    def allow_syncdb(self, db, model):
        """Disallows table synchronization for this application's models."""

        if self._app(model) == APP_NAME and self._mod(model) in MODELS:
            return False
        return None
