from datetime import timedelta

from django.db.models import F
from django.urls import reverse

from sentry import audit_log
from sentry.auth.authenticators import TotpInterface
from sentry.models import (
    AuditLogEntry,
    Authenticator,
    AuthProvider,
    InviteStatus,
    Organization,
    OrganizationMember,
)
from sentry.testutils import TestCase


class AcceptInviteTest(TestCase):
    def setUp(self):
        super().setUp()
        self.organization = self.create_organization(owner=self.create_user("foo@example.com"))
        self.user = self.create_user("bar@example.com")

    def _require_2fa_for_organization(self):
        self.organization.update(flags=F("flags").bitor(Organization.flags.require_2fa))
        assert self.organization.flags.require_2fa.is_set

    def _assert_pending_invite_details_in_session(self, om):
        assert self.client.session["invite_token"] == om.token
        assert self.client.session["invite_member_id"] == om.id

    def _assert_pending_invite_details_not_in_session(self, response):
        session_invite_token = self.client.session.get("invite_token", None)
        session_invite_member_id = self.client.session.get("invite_member_id", None)
        assert session_invite_token is None
        assert session_invite_member_id is None

    def _enroll_user_in_2fa(self):
        interface = TotpInterface()
        interface.enroll(self.user)
        assert Authenticator.objects.user_has_2fa(self.user)

    def test_invalid_member_id(self):
        resp = self.client.get(reverse("sentry-api-0-accept-organization-invite", args=[1, 2]))
        assert resp.status_code == 400

    def test_invalid_token(self):
        om = OrganizationMember.objects.create(
            email="newuser@example.com", token="abc", organization=self.organization
        )
        resp = self.client.get(reverse("sentry-api-0-accept-organization-invite", args=[om.id, 2]))
        assert resp.status_code == 400

    def test_invite_not_pending(self):
        user = self.create_user(email="test@gmail.com")
        om = OrganizationMember.objects.create(
            email="newuser@example.com", token="abc", organization=self.organization, user=user
        )
        resp = self.client.get(
            reverse("sentry-api-0-accept-organization-invite", args=[om.id, om.token])
        )
        assert resp.status_code == 400

    def test_invite_unapproved(self):
        om = OrganizationMember.objects.create(
            email="newuser@example.com",
            token="abc",
            organization=self.organization,
            invite_status=InviteStatus.REQUESTED_TO_JOIN.value,
        )
        resp = self.client.get(
            reverse("sentry-api-0-accept-organization-invite", args=[om.id, om.token])
        )
        assert resp.status_code == 400

    def test_needs_authentication(self):
        om = OrganizationMember.objects.create(
            email="newuser@example.com", token="abc", organization=self.organization
        )
        resp = self.client.get(
            reverse("sentry-api-0-accept-organization-invite", args=[om.id, om.token])
        )
        assert resp.status_code == 200
        assert resp.data["needsAuthentication"]

    def test_not_needs_authentication(self):
        self.login_as(self.user)

        om = OrganizationMember.objects.create(
            email="newuser@example.com", token="abc", organization=self.organization
        )
        resp = self.client.get(
            reverse("sentry-api-0-accept-organization-invite", args=[om.id, om.token])
        )
        assert resp.status_code == 200
        assert not resp.data["needsAuthentication"]

    def test_user_needs_2fa(self):
        self._require_2fa_for_organization()
        assert not Authenticator.objects.user_has_2fa(self.user)

        self.login_as(self.user)

        om = OrganizationMember.objects.create(
            email="newuser@example.com", token="abc", organization=self.organization
        )
        resp = self.client.get(
            reverse("sentry-api-0-accept-organization-invite", args=[om.id, om.token])
        )
        assert resp.status_code == 200
        assert resp.data["needs2fa"]

        self._assert_pending_invite_details_in_session(om)

    def test_user_has_2fa(self):
        self._require_2fa_for_organization()
        self._enroll_user_in_2fa()

        self.login_as(self.user)

        om = OrganizationMember.objects.create(
            email="newuser@example.com", token="abc", organization=self.organization
        )
        resp = self.client.get(
            reverse("sentry-api-0-accept-organization-invite", args=[om.id, om.token])
        )
        assert resp.status_code == 200
        assert not resp.data["needs2fa"]

        self._assert_pending_invite_details_not_in_session(resp)

    def test_user_can_use_sso(self):
        AuthProvider.objects.create(organization=self.organization, provider="google")
        self.login_as(self.user)

        om = OrganizationMember.objects.create(
            email="newuser@example.com", token="abc", organization=self.organization
        )
        resp = self.client.get(
            reverse("sentry-api-0-accept-organization-invite", args=[om.id, om.token])
        )
        assert resp.status_code == 200
        assert resp.data["needsSso"]
        assert resp.data["hasAuthProvider"]
        assert resp.data["ssoProvider"] == "Google"

    def test_can_accept_while_authenticated(self):
        self.login_as(self.user)

        om = OrganizationMember.objects.create(
            email="newuser@example.com", role="member", token="abc", organization=self.organization
        )
        resp = self.client.post(
            reverse("sentry-api-0-accept-organization-invite", args=[om.id, om.token])
        )
        assert resp.status_code == 204

        om = OrganizationMember.objects.get(id=om.id)
        assert om.email is None
        assert om.user == self.user

        ale = AuditLogEntry.objects.get(
            organization=self.organization, event=audit_log.get_event_id("MEMBER_ACCEPT")
        )

        assert ale.actor == self.user
        assert ale.target_object == om.id
        assert ale.target_user == self.user
        assert ale.data

    def test_cannot_accept_expired(self):
        self.login_as(self.user)

        om = OrganizationMember.objects.create(
            email="newuser@example.com", token="abc", organization=self.organization
        )
        OrganizationMember.objects.filter(id=om.id).update(
            token_expires_at=om.token_expires_at - timedelta(days=31)
        )
        resp = self.client.post(
            reverse("sentry-api-0-accept-organization-invite", args=[om.id, om.token])
        )
        assert resp.status_code == 400

        om = OrganizationMember.objects.get(id=om.id)
        assert om.is_pending, "should not have been accepted"
        assert om.token, "should not have been accepted"

    def test_cannot_accept_unapproved_invite(self):
        self.login_as(self.user)

        om = OrganizationMember.objects.create(
            email="newuser@example.com",
            role="member",
            token="abc",
            organization=self.organization,
            invite_status=InviteStatus.REQUESTED_TO_JOIN.value,
        )
        resp = self.client.post(
            reverse("sentry-api-0-accept-organization-invite", args=[om.id, om.token])
        )
        assert resp.status_code == 400

        om = OrganizationMember.objects.get(id=om.id)
        assert not om.invite_approved
        assert om.is_pending
        assert om.token

    def test_member_already_exists(self):
        self.login_as(self.user)

        om = OrganizationMember.objects.create(
            email="newuser@example.com", role="member", token="abc", organization=self.organization
        )
        resp = self.client.post(
            reverse("sentry-api-0-accept-organization-invite", args=[om.id, om.token])
        )
        assert resp.status_code == 204

        om = OrganizationMember.objects.get(id=om.id)
        assert om.email is None
        assert om.user == self.user

        om2 = OrganizationMember.objects.create(
            email="newuser1@example.com",
            role="member",
            token="abcd",
            organization=self.organization,
        )
        resp = self.client.post(
            reverse("sentry-api-0-accept-organization-invite", args=[om2.id, om2.token])
        )
        assert resp.status_code == 400
        assert not OrganizationMember.objects.filter(id=om2.id).exists()

    def test_can_accept_when_user_has_2fa(self):
        self._require_2fa_for_organization()
        self._enroll_user_in_2fa()

        self.login_as(self.user)

        om = OrganizationMember.objects.create(
            email="newuser@example.com", role="member", token="abc", organization=self.organization
        )

        resp = self.client.post(
            reverse("sentry-api-0-accept-organization-invite", args=[om.id, om.token])
        )
        assert resp.status_code == 204

        self._assert_pending_invite_details_not_in_session(resp)

        om = OrganizationMember.objects.get(id=om.id)
        assert om.email is None
        assert om.user == self.user

        ale = AuditLogEntry.objects.get(
            organization=self.organization, event=audit_log.get_event_id("MEMBER_ACCEPT")
        )

        assert ale.actor == self.user
        assert ale.target_object == om.id
        assert ale.target_user == self.user
        assert ale.data

    def test_cannot_accept_when_user_needs_2fa(self):
        self._require_2fa_for_organization()
        self.assertFalse(Authenticator.objects.user_has_2fa(self.user))

        self.login_as(self.user)

        om = OrganizationMember.objects.create(
            email="newuser@example.com", role="member", token="abc", organization=self.organization
        )
        resp = self.client.post(
            reverse("sentry-api-0-accept-organization-invite", args=[om.id, om.token])
        )
        assert resp.status_code == 400

    def test_2fa_cookie_deleted_after_accept(self):
        self._require_2fa_for_organization()
        self.assertFalse(Authenticator.objects.user_has_2fa(self.user))

        self.login_as(self.user)

        om = OrganizationMember.objects.create(
            email="newuser@example.com", role="member", token="abc", organization=self.organization
        )
        resp = self.client.get(
            reverse("sentry-api-0-accept-organization-invite", args=[om.id, om.token])
        )
        assert resp.status_code == 200
        self._assert_pending_invite_details_in_session(om)

        self._enroll_user_in_2fa()
        resp = self.client.post(
            reverse("sentry-api-0-accept-organization-invite", args=[om.id, om.token])
        )
        assert resp.status_code == 204

        self._assert_pending_invite_details_not_in_session(resp)
