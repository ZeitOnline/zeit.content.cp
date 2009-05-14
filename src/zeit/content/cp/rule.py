# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from __future__ import with_statement
import gocept.cache.method
import itertools
import logging
import urllib2
import zeit.content.cp.interfaces
import zeit.workflow.timebased
import zope.app.appsetup.product
import zope.component
import zope.interface


log = logging.getLogger(__name__)


ERROR = 'error'
WARNING = 'warning'


class Break(Exception):
    pass


class Status(object):

    status = None
    message = None


class Rule(object):
    def __init__(self, code):
        self.code = compile(code, '<string>', 'exec')

    def apply(self, context):
        status = Status()

        globs = dict(
            applicable=self.applicable,
            error_if=lambda *args: self.error_if(status, *args),
            error_unless=lambda *args: self.error_unless(status, *args),
            warning_if=lambda *args: self.warning_if(status, *args),
            warning_unless=lambda *args: self.warning_unless(status, *args),
            context=context,
        )

        defaults = ['area', 'layout', 'position', 'count',
                    'is_block', 'is_area']
        for key in defaults:
            globs[key] = None
        globs.update(zeit.content.cp.interfaces.IRuleGlobs(context))

        try:
            eval(self.code, globs)
        except Break:
            pass

        return status

    def applicable(self, condition):
        if not condition:
            raise Break

    def error_if(self, status, condition, message=None):
        if condition:
            status.status = ERROR
            status.message = message
        raise Break

    def error_unless(self, status, condition, message=None):
        self.error_if(status, not condition, message)

    def warning_if(self, status, condition, message=None):
        if condition:
            status.status = WARNING
            status.message = message

    def warning_unless(self, status, condition, message=None):
        self.warning_if(status, not condition, message)


@zope.component.adapter(zeit.content.cp.interfaces.IBlock)
@zope.interface.implementer(zeit.content.cp.interfaces.IRuleGlobs)
def globs_for_block(context):
    area = context.__parent__
    globs = dict(
        is_block=True,
        type=context.type,
        area=area.__name__,
        position=area.keys().index(context.__name__) + 1,
        )
    return globs


@zope.interface.implementer(zeit.content.cp.interfaces.IRuleGlobs)
def globs_for_teaser(context):
    globs = globs_for_block(context)
    globs['layout'] = context.layout.id
    return globs

@zope.component.adapter(zeit.content.cp.interfaces.IArea)
@zope.interface.implementer(zeit.content.cp.interfaces.IRuleGlobs)
def globs_for_area(context):
    globs = dict(
        is_area=True,
        count=len(context),
        area=context.__name__
        )
    return globs


class RulesManager(object):

    zope.interface.implements(zeit.content.cp.interfaces.IRulesManager)

    @gocept.cache.method.Memoize(360)
    def get_rules(self):
        rules = []
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.content.cp')
        url = config['rules-url']
        file_rules = urllib2.urlopen(url)
        log.info('Loading rules from %s' % url)
        noop = True
        rule = []
        for line in file_rules:
            line = unicode(line, 'utf-8')
            if line.startswith('applicable') and noop:
                # start a new rule
                if rule:
                    rules.append(self.create_rule(rule))
                rule = []
            noop = line.strip().startswith('#') or not line.strip()
            if not noop:
                rule.append(line)
        if rule:
            rules.append(self.create_rule(rule))
        file_rules.close()
        return rules

    def create_rule(self, commands):
        code = '\n'.join(commands)
        compile(code, '<string>', 'exec') # syntax check
        rule = Rule(code)
        return rule

    @property
    def rules(self):
        try:
            rules = self.get_rules()
        except SyntaxError, e:
            log.exception(e)
            return self.cached_rules
        else:
            self.cached_rules = rules
            return rules


class Validator(object):

    zope.interface.implements(zeit.content.cp.interfaces.IValidator)

    status = None

    def __init__(self, context):
        self.messages = []
        self.context = context
        rm = zope.component.getUtility(
            zeit.content.cp.interfaces.IRulesManager)
        for rule in rm.rules:
            status = rule.apply(context)
            if status.status and self.status != ERROR:
                self.status = status.status
            if status.message:
                self.messages.append(status.message)


class CenterPageValidator(object):

    zope.interface.implements(zeit.content.cp.interfaces.IValidator)

    status = None

    def __init__(self, context):
        self.messages = []
        self.context = context
        areas = context.values()
        for item in itertools.chain(areas, *[a.values() for a in areas]):
            validator = zeit.content.cp.interfaces.IValidator(item)
            if validator.status and self.status != ERROR:
                # Set self status when there was an error or warning, but only
                # if there was no error before. If there was an error the whole
                # validation will stay in error state
                self.status = validator.status
            if validator.messages:
                self.messages.extend(validator.messages)


class ValidatingWorkflow(zeit.workflow.timebased.TimeBasedWorkflow):

    def can_publish(self):
        validator = zeit.content.cp.interfaces.IValidator(self.context)
        if validator.status == zeit.content.cp.rule.ERROR:
            return False
        return True
