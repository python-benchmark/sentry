from django.conf import settings
from django.middleware.csrf import get_token as get_csrf_token
from rest_framework.request import Request
from rest_framework.response import Response

from sentry.models import Project
from sentry.signals import first_event_pending
from sentry.web.frontend.base import BaseView, OrganizationView
from sentry.web.helpers import render_to_response


class ReactMixin:
    def meta_tags(self, request: Request, **kwargs):
        return {}

    def handle_react(self, request: Request, **kwargs) -> Response:
        context = {
            "CSRF_COOKIE_NAME": settings.CSRF_COOKIE_NAME,
            "meta_tags": [
                {"property": key, "content": value}
                for key, value in self.meta_tags(request, **kwargs).items()
            ],
        }

        # Force a new CSRF token to be generated and set in user's
        # Cookie. Alternatively, we could use context_processor +
        # template tag, but in this case, we don't need a form on the
        # page. So there's no point in rendering a random `<input>` field.
        get_csrf_token(request)

        return render_to_response("sentry/base-react.html", context=context, request=request)


# TODO(dcramer): once we implement basic auth hooks in React we can make this
# generic
class ReactPageView(OrganizationView, ReactMixin):
    def handle_auth_required(self, request: Request, *args, **kwargs) -> Response:
        # If user is a superuser (but not active, because otherwise this method would never be called)
        # Then allow client to handle the route and respond to any API request errors
        if request.user.is_superuser:
            return self.handle_react(request)

        # For normal users, let parent class handle (e.g. redirect to login page)
        return super().handle_auth_required(request, *args, **kwargs)

    def handle(self, request: Request, organization, **kwargs) -> Response:
        if "project_id" in kwargs and request.GET.get("onboarding"):
            project = Project.objects.filter(
                organization=organization, slug=kwargs["project_id"]
            ).first()
            first_event_pending.send(project=project, user=request.user, sender=self)
        request.organization = organization
        return self.handle_react(request)


class GenericReactPageView(BaseView, ReactMixin):
    def handle(self, request: Request, **kwargs) -> Response:
        return self.handle_react(request, **kwargs)
