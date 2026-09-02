# Data Permission Testing Rules

## Purpose

Define what to test for data-level access control and how to classify findings.

## Scope

Data permission testing verifies that users can only access data within their authorized scope, even when they have permission to use the API.

## Data Scope Types

| Scope | Description | Example |
|---|---|---|
| **All** | No data filtering | Admin sees all records |
| **Department** | Data within the user's department | Manager sees only their department's employees |
| **Organization** | Data within the user's organization | Org admin sees only their org's data |
| **Self** | Only the user's own data | Employee sees only their own record |
| **Custom** | Arbitrary business rules | Team lead sees their team + adjacent teams |

## Test Rules

### DATA-001: In-Scope Access (Positive)

**Rule:** Users must be able to access data within their authorized scope.

**Test:**
1. For each role and its data scope:
   - Identify data records within scope
   - Send a request to access those records
   - Expected: 200 OK with data returned

**Violation:** User cannot access data within their scope (misconfiguration).

**Severity:** Medium (functional issue)

---

### DATA-002: Out-of-Scope Access (Negative)

**Rule:** Users must NOT be able to access data outside their authorized scope.

**Test:**
1. For each role and its data scope:
   - Identify data records OUTSIDE scope
   - Send a request to access those records
   - Expected: 403 Forbidden, or 200 with empty/filtered result

**Violation:** User can access data outside their scope.

**Severity:** High (data leakage)

---

### DATA-003: Cross-Department Access

**Rule:** Users with department scope must not access other departments' data.

**Test:**
1. Identify users in different departments with the same role
2. User from Department A attempts to access Department B's data
3. Expected: 403 or empty result

**Violation:** Cross-department data access.

**Severity:** High

---

### DATA-004: Cross-Organization Access

**Rule:** Users with organization scope must not access other organizations' data.

**Test:**
1. Identify users in different organizations with the same role
2. User from Organization A attempts to access Organization B's data
3. Expected: 403 or empty result

**Violation:** Cross-organization data access (multi-tenancy breach).

**Severity:** Critical

---

### DATA-005: Self-Scope Enforcement

**Rule:** Users with self scope must only access their own data.

**Test:**
1. Identify two users with self scope (User A and User B)
2. User A attempts to access User B's data by:
   - Using User B's ID in path parameter
   - Using User B's ID in query parameter
   - Using User B's ID in request body
3. Expected: 403 or empty result for all

**Violation:** User can access another user's data despite self-scope restriction.

**Severity:** High

---

### DATA-006: Scope Filter Bypass

**Rule:** Data scope filtering must not be bypassable through query manipulation.

**Test:**
1. Identify APIs that filter data by scope
2. Attempt to bypass filtering by:
   - Adding explicit scope parameters (e.g., `?department=other_dept`)
   - Using search/filter parameters that ignore scope
   - Using sort/order parameters that leak data from other scopes
   - Using pagination to iterate beyond scope boundaries
3. Expected: Scope filtering persists regardless of query parameters

**Violation:** Scope filter can be bypassed.

**Severity:** High

---

### DATA-007: Scope After Ownership Change

**Rule:** When data ownership changes, access must update accordingly.

**Test:**
1. User A owns Resource X
2. User B (same department) can access Resource X (within scope)
3. Resource X is transferred to User C (different department)
4. User B attempts to access Resource X again
5. Expected: Access denied (if scope is department-based and C is in different dept)

**Violation:** User retains access to data that has moved outside their scope.

**Severity:** Medium

---

## Test Data Requirements

Data permission tests require carefully prepared test data:

1. **Multiple departments** — at least 2 departments with data in each
2. **Multiple users per department** — at least 1 user per department per role
3. **Identifiable data** — data records must be clearly associated with a department/user
4. **Known relationships** — the test must know which data is in-scope and which is out-of-scope

## Classification Guide

| Finding | Classification |
|---|---|
| Access to data outside scope | Data Permission Violation |
| Cross-department access | Cross-Department Data Leakage |
| Cross-organization access | Multi-Tenancy Breach |
| Scope filter bypass | Data Scope Bypass |
| Self-scope violation | Horizontal Data Access Violation |
