import logging
from django.shortcuts import render
from django import template
from django.conf import settings
from django.utils.module_loading import import_string
from userservice.decorators import override_admin_required
from userservice.user import (get_original_user, set_override_user,
                              get_override_user, clear_override)


@override_admin_required
def support(request):
    # timer = Timer()
    logger = logging.getLogger(__name__)

    override_error_username = None
    override_error_msg = None

    actual_user = get_original_user(request)
    if not actual_user:
        raise Exception("No user in session")

    if "override_as" in request.POST:
        transformation_module = _get_username_transform_module()
        new_user = transformation_module(request.POST["override_as"])
        validation_module = _get_validation_module()
        validation_error = validation_module(new_user)
        if validation_error is None:
            logger.info("%s is impersonating %s",
                        actual_user,
                        new_user)
            set_override_user(request, new_user)
        else:
            override_error_username = new_user
            override_error_msg = validation_error

    if "clear_override" in request.POST:
        logger.info("%s is ending impersonation of %s",
                    actual_user,
                    get_override_user(request))
        clear_override(request)

    context = {
        'original_user': actual_user,
        'override_user': get_override_user(request),
        'override_error_username': override_error_username,
        'override_error_msg': override_error_msg,
    }

    try:
        template_name = "userservice/user_override_extra_info.html"
        template.loader.get_template(template_name)
        context['has_extra_template'] = True
        context['extra_template'] = template_name
    except template.TemplateDoesNotExist:
        # This is a fine exception - there doesn't need to be an extra info
        # template
        pass

    try:
        template.loader.get_template("userservice/user_override_wrapper.html")
        context['wrapper_template'] = 'userservice/user_override_wrapper.html'
    except template.TemplateDoesNotExist:
        context['wrapper_template'] = 'support_wrapper.html'
        # This is a fine exception - there doesn't need to be an extra info
        # template
        pass

    return render(request,
                  'support.html',
                  context)


def _get_username_transform_module():
    if hasattr(settings, "USERSERVICE_TRANSFORMATION_MODULE"):
        return import_string(settings.USERSERVICE_TRANSFORMATION_MODULE)
    else:
        return transform


def _get_validation_module():
    if hasattr(settings, "USERSERVICE_VALIDATION_MODULE"):
        return import_string(settings.USERSERVICE_VALIDATION_MODULE)
    else:
        return validate


def validate(username):
    error_msg = "No override user supplied"
    if (len(username) > 0):
        error_msg = None
    return error_msg


def transform(username):
    return username.strip()
