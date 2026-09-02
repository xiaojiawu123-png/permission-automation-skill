# Token Strategy

## Overview

Token management is a critical part of permission testing. Tests need valid credentials for multiple roles, tokens must be reused efficiently, and the mechanism for obtaining tokens varies by project.

This document defines the abstract token management strategy that the skill follows, regardless of the target project's specific authentication protocol.

## Abstract Token Flow

```
┌──────────┐     ┌──────────────────┐     ┌──────────┐
│  User    │────>│  Authentication  │────>│  Token   │
│ Identity │     │  Mechanism       │     │ Artifact │
└──────────┘     └──────────────────┘     └────┬─────┘
                                                │
                    ┌──────────────────┐        │
                    │  Request         │<───────┘
                    │  Injection       │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Permission      │
                    │  Test Execution  │
                    └──────────────────┘
```

## Discovery Process

The AI must discover the target project's token mechanism before generating any test code. The discovery follows this priority:

### Priority 1: Existing Token Infrastructure
Check if the project already has:
- Login functions or auth utilities
- Token management classes or modules
- Test fixtures that handle authentication
- Environment variables with test credentials

If found, **reuse them**.

### Priority 2: Login API
Search for authentication endpoints:
- `POST /login`, `POST /auth`, `POST /oauth/token`
- Login controllers or handlers
- Auth middleware configuration

If found, use the login API to obtain tokens for each role.

### Priority 3: Configuration-Based Tokens
Check if tokens are provided through:
- Environment variables
- Configuration files
- Test fixture data

If found, load tokens from configuration.

### Priority 4: Manual Token Generation
If no automated method exists, document the manual process and ask the user to provide tokens for each role.

## Token Lifecycle

### Acquisition
```
For each role in the test suite:
    1. Authenticate as a user with that role
    2. Extract the token from the response
    3. Store the token in a role-keyed cache
```

### Caching
```
Token Cache:
    admin:    { token: "...", expires_at: ..., header: "..." }
    manager:  { token: "...", expires_at: ..., header: "..." }
    employee: { token: "...", expires_at: ..., header: "..." }
```

Tokens are cached for the duration of the test session. This avoids redundant login calls and keeps tests fast.

### Refresh
Before each request, check if the cached token is still valid:
- If the token has an expiration time, check it
- If a request returns 401, attempt to refresh the token
- If refresh fails, re-authenticate from scratch

### Cleanup
After the test session:
- Clear cached tokens from memory
- If tokens were created specifically for testing, invalidate them

## Token Transport

Different projects use different mechanisms to pass tokens in requests:

| Transport | Example | Where to Check |
|---|---|---|
| Authorization Header | `Authorization: Bearer <token>` | Most common for JWT/OAuth |
| Custom Header | `X-Auth-Token: <token>` | Custom auth implementations |
| Cookie | `Cookie: session=<token>` | Session-based auth |
| Query Parameter | `?token=<token>` | Less common, less secure |

The AI must discover which transport the project uses and generate test code accordingly.

## Multi-Role Token Management

Permission testing requires tokens for multiple roles simultaneously. The token manager must:

1. **Maintain separate tokens per role** — never mix tokens between roles
2. **Support role switching** — tests can specify which role's token to use
3. **Handle token dependencies** — some tests may need to create data as one role, then access it as another

### Role Token Pattern
```
# Abstract representation
role_tokens:
    admin:
        user: admin_user
        token: <acquired_at_runtime>
        transport: header
        header_name: Authorization
        header_prefix: Bearer

    manager:
        user: manager_user
        token: <acquired_at_runtime>
        transport: header
        header_name: Authorization
        header_prefix: Bearer

    employee:
        user: employee_user
        token: <acquired_at_runtime>
        transport: header
        header_name: Authorization
        header_prefix: Bearer
```

## Error Handling

| Scenario | Action |
|---|---|
| Login returns 401 | Check credentials in users.yaml |
| Login returns 403 | User account may be locked |
| Login returns 500 | Auth service may be down |
| Token returns 401 on use | Token may be expired; refresh |
| Token returns 403 on use | This may be the permission being tested |
| Refresh fails | Re-authenticate from scratch |
| All auth fails | Stop tests; report authentication failure |

## Security Considerations

1. **Never log tokens** — tokens are secrets; redact them from logs and reports
2. **Never hardcode tokens** — always obtain at runtime or load from secure config
3. **Use test accounts** — never use production credentials for testing
4. **Isolate test tokens** — tokens created for testing should not have access to production data
5. **Clean up** — invalidate test tokens after the test session
