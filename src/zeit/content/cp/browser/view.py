# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import cjson
import zeit.cms.browser.view


class Form(object):

    def __init__(self, var_name, json=False):
        self.var_name = var_name
        self.json = json

    def __get__(self, instance, class_):
        if instance is None:
            return self

        value = instance.request.form[self.var_name]
        if self.json:
            value = cjson.decode(value)
        return value


class Action(zeit.cms.browser.view.Base):

    def signal(self, when, name, *args):
        self.signals.append(dict(
            args=args,
            name=name,
            when=when,
        ))

    def render(self):
        return cjson.encode(dict(signals=self.signals))

    def __call__(self):
        self.signals = []
        self.update()
        return self.render()