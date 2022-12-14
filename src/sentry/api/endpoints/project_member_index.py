from django.db.models import Q
from rest_framework.request import Request
from rest_framework.response import Response

from sentry.api.base import region_silo_endpoint
from sentry.api.bases.project import ProjectEndpoint
from sentry.api.serializers import serialize
from sentry.models import OrganizationMember


@region_silo_endpoint
class ProjectMemberIndexEndpoint(ProjectEndpoint):
    def get(self, request: Request, project) -> Response:
        queryset = (
            OrganizationMember.objects.filter(
                Q(user__is_active=True) | Q(user__isnull=True),
                organization=project.organization,
                teams__in=project.teams.all(),
            )
            .select_related("user")
            .distinct()
        )

        member_list = sorted(
            queryset, key=lambda x: x.user.get_display_name() if x.user_id else x.email
        )

        context = serialize(member_list, request.user)

        return Response(context)
