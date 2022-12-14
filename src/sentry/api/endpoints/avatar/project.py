from sentry.api.base import region_silo_endpoint
from sentry.api.bases.avatar import AvatarMixin
from sentry.api.bases.project import ProjectEndpoint
from sentry.models import ProjectAvatar


@region_silo_endpoint
class ProjectAvatarEndpoint(AvatarMixin, ProjectEndpoint):
    object_type = "project"
    model = ProjectAvatar
