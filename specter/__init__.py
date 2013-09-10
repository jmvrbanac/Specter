import gettext
gettext.install('specter', unicode=1)

def _(msg):
    """ Dealing with pylint problems"""
    return gettext.gettext(msg)