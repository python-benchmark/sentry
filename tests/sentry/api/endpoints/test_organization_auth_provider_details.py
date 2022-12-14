from django.urls import reverse

from sentry.testutils import PermissionTestCase
from sentry.testutils.silo import region_silo_test


@region_silo_test
class OrganizationAuthProviderPermissionTest(PermissionTestCase):
    def setUp(self):
        super().setUp()
        self.path = reverse(
            "sentry-api-0-organization-auth-provider", args=[self.organization.slug]
        )

    def test_member_can_get(self):
        with self.feature("organizations:sso-basic"):
            self.assert_member_can_access(self.path)
