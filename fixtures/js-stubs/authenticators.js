export function Authenticators() {
  return {
    Totp: params => ({
      lastUsedAt: null,
      enrollButton: 'Enroll',
      description:
        'An authenticator application that supports TOTP (like Google Authenticator or 1Password) can be used to conveniently secure your account.  A new token is generated every 30 seconds.',
      isEnrolled: true,
      removeButton: 'Remove',
      id: 'totp',
      createdAt: '2018-01-30T17:24:36.554Z',
      configureButton: 'Info',
      name: 'Authenticator App',
      allowMultiEnrollment: false,
      disallowNewEnrollment: false,
      authId: '15',
      canValidateOtp: true,
      isBackupInterface: false,
      ...params,
    }),
    Sms: params => ({
      enrollButton: 'Enroll',
      name: 'Text Message',
      allowMultiEnrollment: false,
      removeButton: 'Remove',
      canValidateOtp: true,
      isEnrolled: false,
      configureButton: 'Info',
      id: 'sms',
      isBackupInterface: false,
      disallowNewEnrollment: false,
      description:
        "This authenticator sends you text messages for verification.  It's useful as a backup method or when you do not have a phone that supports an authenticator application.",
      ...params,
    }),
    U2f: params => ({
      lastUsedAt: null,
      enrollButton: 'Enroll',
      description:
        "Authenticate with a U2F hardware device. This is a device like a Yubikey or something similar which supports FIDO's U2F specification. This also requires a browser which supports this system (like Google Chrome).",
      isEnrolled: true,
      removeButton: 'Remove',
      id: 'u2f',
      createdAt: '2018-01-30T20:56:45.932Z',
      configureButton: 'Configure',
      name: 'U2F (Universal 2nd Factor)',
      allowMultiEnrollment: true,
      disallowNewEnrollment: false,
      authId: '23',
      canValidateOtp: false,
      isBackupInterface: false,
      ...params,
    }),
    Recovery: params => ({
      lastUsedAt: null,
      enrollButton: 'Activate',
      description:
        'Recovery codes are the only way to access your account if you lose your device and cannot receive two-factor authentication codes.',
      isEnrolled: true,
      removeButton: null,
      id: 'recovery',
      createdAt: '2018-01-30T17:24:36.570Z',
      configureButton: 'View Codes',
      name: 'Recovery Codes',
      allowMultiEnrollment: false,
      authId: '16',
      canValidateOtp: true,
      isBackupInterface: true,
      codes: ['ABCD-1234', 'EFGH-5678'],
      ...params,
    }),
  };
}

export function AllAuthenticators() {
  return Object.values(Authenticators()).map(x => x());
}
