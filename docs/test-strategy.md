# Test Strategy

## Testing Philosophy

Permission testing is fundamentally different from functional testing. Functional testing verifies that the system does what it should. Permission testing verifies that the system **prevents** what it should not allow.

Every permission test has two possible outcomes:
- **Expected deny:** The system correctly rejects an unauthorized action
- **Unexpected allow:** The system incorrectly permits an unauthorized action (this is a vulnerability)

## Test Categories

### 1. Authentication Tests

Verify that the system correctly requires and validates authentication.

| Scenario | Request | Expected |
|---|---|---|
| No token | Request without any credential | 401 Unauthorized |
| Malformed token | Request with invalid token format | 401 Unauthorized |
| Expired token | Request with expired credential | 401 Unauthorized |
| Revoked token | Request with deactivated user's token | 401 Unauthorized |
| Wrong environment | Token from different system/environment | 401 Unauthorized |

### 2. Role Permission Tests (Vertical)

Verify that each role can only perform its authorized operations.

For every role R and every API A:
- If R has permission for A → expect 200
- If R lacks permission for A → expect 403

This produces a matrix of `roles x APIs` test cases.

### 3. API Permission Tests

Verify that APIs enforce permissions regardless of how they are called.

Key scenarios:
- Direct API call bypassing frontend (no UI button = no protection?)
- API call with correct permission code but wrong role
- API call after role change (permission was revoked)

### 4. Data Permission Tests

Verify that data scope filtering works correctly.

| Scenario | Actor | Action | Expected |
|---|---|---|---|
| In-scope access | Dept A manager | View Dept A employee | 200 |
| Out-of-scope access | Dept A manager | View Dept B employee | 403 or empty |
| Admin full access | Admin | View any employee | 200 |
| Self-only access | Employee | View own record | 200 |
| Cross-user access | Employee | View other's record | 403 |

### 5. Horizontal Privilege Escalation Tests

Verify that users cannot access other users' resources by manipulating identifiers.

Pattern:
```
User A has resource ID-X
User B has resource ID-Y
User B requests resource ID-X → should be denied
```

Test variations:
- Path parameter: `GET /resources/{id}` with another user's ID
- Query parameter: `GET /resources?ownerId=other-user`
- Body parameter: `POST /resources` with `ownerId` set to another user
- Nested resource: `GET /users/{userId}/resources` with another user's ID

### 6. Vertical Privilege Escalation Tests

Verify that lower-privilege roles cannot perform higher-privilege operations.

Pattern:
```
Role "user" cannot DELETE /resources/{id}
Attacker with "user" role sends DELETE /resources/{id} → should be denied
```

Test variations:
- Direct operation: lower role calls higher role's API
- Role parameter injection: include `role=admin` in request body
- Permission parameter injection: include `permission=delete` in request
- Hierarchy bypass: attempt operations from intermediate roles

### 7. Parameter Tampering Tests

Verify that modifying identity/scope parameters does not bypass permissions.

Parameters to test:
- `userId`, `ownerId`, `createdBy` — ownership fields
- `departmentId`, `organizationId`, `tenantId` — scope fields
- `roleId`, `role`, `permissions` — role/permission fields
- `resourceId`, `entityId`, `recordId` — resource identifiers

For each parameter:
1. Send request with legitimate value → expect 200
2. Send request with another user's value → expect 403 or ignore
3. Send request with elevated role value → expect 403 or ignore

### 8. Batch Authorization Tests

Verify that batch operations enforce per-item permission checks.

Pattern:
```json
{
  "ids": [authorized-id-1, unauthorized-id-2, authorized-id-3]
}
```

Expected behaviors:
- **Strict:** Reject entire request if any ID is unauthorized
- **Partial:** Return results only for authorized IDs
- **Vulnerable:** Return results for all IDs including unauthorized

The test must verify that unauthorized IDs do not appear in the response.

## Coverage Model

### Minimum Coverage Requirements

Every permission test suite must cover:

1. **All roles** — every role in the system has test cases
2. **All APIs** — every protected API has positive and negative tests
3. **All boundaries** — every permission boundary is tested from both sides
4. **All data scopes** — every data scope rule has in-scope and out-of-scope tests
5. **All escalation vectors** — every IDOR, parameter tampering, and batch bypass vector

### Coverage Matrix

```
                    Auth  Role  API  Data  Horiz  Vert  Tamper  Batch
admin                -     +    +    +     -      -     +       +
manager              -     +    +    +     -      -     +       +
employee             -     +    +    +     +      +     +       +
unauthenticated      +     -    -    -     -      -     -       -
```

`+` = must have test cases
`-` = not applicable

## Test Design Principles

### 1. One Assertion Per Concern
Each test case verifies one specific permission boundary. Do not combine multiple assertions in a single test.

### 2. Clear Naming
Test names must describe:
- Who is acting (role)
- What they are doing (operation)
- What the expected outcome is (allow/deny)

Example: `test_manager_cannot_delete_employee_returns_403`

### 3. Independent Tests
Each test must be independently executable. No test should depend on the state left by a previous test.

### 4. Deterministic
Tests must produce the same result every time. Avoid dependencies on timing, random data, or external state changes.

### 5. Fast Feedback
Token caching and connection reuse keep the test suite fast. Permission tests should complete in seconds, not minutes.

## Severity Classification

| Severity | Description | Example |
|---|---|---|
| **Critical** | Complete authorization bypass | Unauthenticated access to admin API |
| **High** | Privilege escalation | Lower role can perform admin operations |
| **High** | Data leakage | Cross-tenant data access |
| **Medium** | Partial authorization bypass | Batch operation returns unauthorized data |
| **Medium** | IDOR | User can view another user's resource by ID |
| **Low** | Inconsistent enforcement | Same resource, different endpoints, different checks |
| **Low** | Information disclosure | Error message reveals permission structure |
