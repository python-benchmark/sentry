from rest_framework.request import Request
from rest_framework.response import Response

from sentry.api.base import region_silo_endpoint
from sentry.api.bases import SentryAppInstallationBaseEndpoint
from sentry.api.serializers import serialize
from sentry.mediators.external_issues import IssueLinkCreator
from sentry.models import Group, Project


@region_silo_endpoint
class SentryAppInstallationExternalIssueActionsEndpoint(SentryAppInstallationBaseEndpoint):
    def post(self, request: Request, installation) -> Response:
        data = request.data.copy()

        if not {"groupId", "action", "uri"}.issubset(data.keys()):
            return Response(status=400)

        group_id = data.get("groupId")
        del data["groupId"]

        try:
            group = Group.objects.get(
                id=group_id,
                project_id__in=Project.objects.filter(organization_id=installation.organization_id),
            )
        except Group.DoesNotExist:
            return Response(status=404)

        action = data["action"]
        del data["action"]

        uri = data.get("uri")
        del data["uri"]

        try:
            external_issue = IssueLinkCreator.run(
                install=installation,
                group=group,
                action=action,
                fields=data,
                uri=uri,
                user=request.user,
            )
        except Exception:
            return Response({"error": "Error communicating with Sentry App service"}, status=400)

        return Response(serialize(external_issue))
