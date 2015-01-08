from zeit.content.cp.i18n import MessageFactory as _
import zeit.edit.browser.view


class Editor(object):

    title = _('Edit centerpage')

    def validate(self, area):
        validation_class, validation_messages = (
            zeit.edit.browser.view.validate(area))
        css_class = ['editable-area']
        if validation_class:
            css_class.append(validation_class)
        css_class = ' '.join(css_class)
        return dict(class_=css_class, messages=validation_messages)
