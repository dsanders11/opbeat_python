import logging

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)
register = template.Library()


@register.inclusion_tag('opbeat/javascript_module.html', takes_context=True)
def opbeat_javascript(context, async=True, **kwargs):
    """
    Renders the HTML for Opbeat's JavaScript module.
    """

    def convert_to_js(value):
        """ Make a value friendly for use in JavaScript, e.g. True -> true """

        if type(value) is bool:
            return "true" if value else "false"

        return mark_safe(u'"{}"'.format(value))

    request = context.get('request')

    try:
        template_context = {
            'ORGANIZATION_ID': settings.OPBEAT['ORGANIZATION_ID'],
            'APP_ID': settings.OPBEAT['JAVASCRIPT_APP_ID'],
            'ASYNC': async
        }
    except (AttributeError, KeyError):
        logger.exception("Configuration error for Opbeat JavaScript module")
        return {}

    if request:
        template_context['user_context'] = user_context = {}
        is_authenticated = request.user.is_authenticated()

        if is_authenticated:
            user_context.update({
                'id': convert_to_js(request.user.id),
                'username': convert_to_js(request.user.username),
                'email': convert_to_js(request.user.email)
            })

        user_context['is_authenticated'] = convert_to_js(is_authenticated)

    if kwargs:
        template_context['extra_context'] = extra_context = {}

        for extra in kwargs:
            extra_context[extra] = convert_to_js(kwargs[extra])

    return template_context
