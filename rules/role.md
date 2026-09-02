# Role Permission Testing Rules

## Purpose

Define what to test for role-based access control and how to classify findings.

## Scope

Role permission testing verifies that each role can only perform its authorized operations and is correctly denied for unauthorized operations.

## Test Rules

### ROLE-001: Positive Permission (Allow)

**Rule:** If a role has a permission, requests from that role must succeed.

**Test:**
1. For each role R and each permission P assigned to R
2. Identify the API(s) that correspond to P
3. Send a request as a user with role R to each API
4. Expected: 200 (or appropriate success code)

**Violation:** Authorized request is denied (false positive — permission misconfiguration).

**Severity:** Medium (functional issue, not security issue)

---

### ROLE-002: Negative Permission (Deny)

**Rule:** If a role does NOT have a permission, requests from that role must be denied.

**Test:**
1. For each role R and each permission P NOT assigned to R
2. Identify the API(s) that correspond to P
3. Send a request as a user with role R to each API
4. Expected: 403 Forbidden

**Violation:** Unauthorized request succeeds (privilege escalation).

**Severity:** High to Critical (depending on the operation)

---

### ROLE-003: Role Hierarchy Boundaries

**Rule:** If roles are hierarchical, verify that boundary permissions are correctly enforced.

**Test:**
1. Identify role hierarchy (e.g., admin > manager > employee)
2. For each boundary between adjacent roles:
   - Test that the higher role can do things the lower role cannot
   - Test that the lower role cannot do things only the higher role should
3. Expected: Clear permission boundary at each level

**Violation:** Lower role can perform higher role's operations, or higher role is unexpectedly restricted.

**Severity:** High

---

### ROLE-004: Multi-Role Users

**Rule:** If a user has multiple roles, the effective permissions should be the union (or as defined by policy).

**Test:**
1. Identify users with multiple roles
2. Verify that the user can access all resources from all assigned roles
3. Verify that the user cannot access resources from unassigned roles
4. Expected: Permission matches the union of all role permissions

**Violation:** User gets permissions from roles they don't have, or is denied permissions they should have.

**Severity:** Medium

---

### ROLE-005: Role Change Propagation

**Rule:** When a user's role changes, their effective permissions must update immediately.

**Test:**
1. Authenticate as a user with role R1
2. Have an admin change the user's role to R2
3. Use the original token to make requests
4. Expected: Requests allowed by R2 but not R1 should fail until re-authentication, OR the system should reflect the change immediately (depending on design)

**Violation:** User retains permissions from a removed role.

**Severity:** High

---

## Test Matrix Construction

For N roles and M APIs, the role permission test matrix has N x M entries:

```
              API-1    API-2    API-3   ...  API-M
role-1       allow    deny     allow        deny
role-2       deny     allow    deny         allow
...
role-N       deny     deny     allow        deny
```

Every cell in this matrix must have at least one test case.

## Classification Guide

| Finding | Classification |
|---|---|
| Role can access unauthorized API | Vertical Privilege Escalation |
| Role denied authorized API | Permission Misconfiguration |
| Hierarchy boundary not enforced | Role Hierarchy Violation |
| Role change not reflected | Stale Permission |
