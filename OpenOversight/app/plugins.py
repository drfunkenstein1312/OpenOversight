from sqlalchemy_continuum.plugins import Plugin

class VersionInheritancePlugin(Plugin):
    """ SQL Alchemy Continuum's versioned class doesn't inherit from the
    parent class. This fixes that.
    """

    def after_version_class_built(self, parent_cls, version_cls):
        for key in parent_cls.__dict__.keys():
            if key[0] == '_':
                continue
            elif key in version_cls.__dict__:
                continue

            setattr(version_cls, key, parent_cls.__dict__[key])
