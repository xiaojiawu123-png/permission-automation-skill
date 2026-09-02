# API Permission Testing Rules

## Purpose

Define what to test for API-level access control and how to classify findings.

## Scope

API permission testing verifies that every API endpoint correctly enforces permission checks regardless of how the request is made.

## Test Rules

### API-001: Protected API Requires Authentication

**Rule:** Every non-public API must require authentication.

**Test:**
1. Identify all APIs that should be protected
2. For each API, send a request without any authentication
3. Expected: 401 Unauthorized

**Violation:** API returns data or performs action without authentication.

**Severity:** Critical

---

### API-002: Permission Check on Each API

**Rule:** Each API must verify that the authenticated user has the required permission.

**Test:**
1. For each API, identify the required permission
2. For each role that does NOT have the required permission:
   - Send a request as a user with that role
   - Expected: 403 Forbidden
3. For each role that HAS the required permission:
   - Send a request as a user with that role
   - Expected: 200 OK

**Violation:** API does not check permission, or checks inconsistently.

**Severity:** High to Critical

---

### API-003: Frontend Bypass

**Rule:** APIs must enforce permissions even when the frontend does not expose the action.

**Test:**
1. Identify operations that are hidden in the frontend for certain roles
2. Call the corresponding API directly as a user with that role
3. Expected: 403 Forbidden

**Violation:** API succeeds despite frontend hiding the action (frontend-only protection).

**Severity:** Critical

---

### API-004: HTTP Method Enforcement

**Rule:** Permission checks must apply to all HTTP methods, not just GET.

**Test:**
1. For each API, test all relevant HTTP methods (GET, POST, PUT, PATCH, DELETE)
2. Verify permission check on each method
3. Expected: All methods enforce permissions

**Violation:** Some methods (especially DELETE, PUT) skip permission checks.

**Severity:** High

---

### API-005: Consistent Enforcement Across Similar Endpoints

**Rule:** Similar APIs for the same resource must have consistent permission checks.

**Test:**
1. Group APIs by resource
2. Compare permission enforcement across APIs in the same group
3. Look for inconsistencies (e.g., GET /users requires permission but GET /users/search does not)

**Violation:** Inconsistent permission enforcement across similar endpoints.

**Severity:** Medium

---

### API-006: Bulk/Batch Endpoint Permission

**Rule:** Bulk/batch endpoints must enforce the same permissions as single-item endpoints.

**Test:**
1. Identify batch endpoints (e.g., `POST /users/batch`, `DELETE /users?ids=1,2,3`)
2. Test that the batch endpoint requires the same permission as the single-item endpoint
3. Test that each item in the batch is individually authorized

**Violation:** Batch endpoint bypasses per-item permission checks.

**Severity:** High

---

### API-007: API Version Permission Parity

**Rule:** All versions of an API must enforce the same permissions.

**Test:**
1. If the API has multiple versions (v1, v2, etc.), test each version
2. Verify that permission checks are consistent across versions

**Violation:** Older or newer API version has weaker permission checks.

**Severity:** High

---

## API Discovery Checklist

When discovering APIs to test, check:

- [ ] Route registration files
- [ ] Controller/handler annotations
- [ ] OpenAPI/Swagger specifications
- [ ] API gateway configuration
- [ ] Middleware chains
- [ ] GraphQL schema (if applicable)
- [ ] gRPC service definitions (if applicable)

Every discovered API must appear in the permission matrix.
