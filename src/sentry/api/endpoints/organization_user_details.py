from rest_framework.request import Request
from rest_framework.response import Response

from sentry.api.base import region_silo_endpoint
from sentry.api.bases.organization import OrganizationEndpoint
from sentry.api.endpoints.organization_member.index import MemberPermission
from sentry.api.serializers import serialize
from sentry.models import User


@region_silo_endpoint
class OrganizationUserDetailsEndpoint(OrganizationEndpoint):
    permission_classes = (MemberPermission,)

    def get(self, request: Request, organization, user_id) -> Response:
        try:
            user = User.objects.get(
                id=user_id, sentry_orgmember_set__organization_id=organization.id
            )
        except User.DoesNotExist:
            return Response(status=404)

        return Response(serialize(user, request.user))
