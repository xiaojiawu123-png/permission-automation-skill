# Privilege Escalation Testing Rules

## Purpose

Define what to test for privilege escalation vulnerabilities and how to classify findings.

## Scope

Privilege escalation testing verifies that users cannot elevate their permissions beyond what their role allows, either vertically (to a higher role) or horizontally (to another user's resources).

## Vertical Privilege Escalation

Vertical privilege escalation occurs when a lower-privilege user can perform actions reserved for higher-privilege roles.

### VERT-001: Direct Operation Escalation

**Rule:** Lower-privilege roles must not be able to perform higher-privilege operations.

**Test:**
1. Identify the role hierarchy (e.g., admin > manager > employee)
2. For each role boundary:
   - Identify operations available to the higher role but not the lower
   - Attempt each operation as a user with the lower role
   - Expected: 403 Forbidden

**Violation:** Lower role can perform higher role's operations.

**Severity:** Critical

**Example:**
```
manager → DELETE /employees/{id} → should be denied (only admin can delete)
employee → POST /employees → should be denied (only admin/manager can create)
```

---

### VERT-002: Role Parameter Injection

**Rule:** Users must not be able to set or modify their own role through request parameters.

**Test:**
1. Identify APIs that accept user data (create user, update user, update profile)
2. Include role-related fields in the request body:
   - `role: "admin"`
   - `roleId: <admin_role_id>`
   - `permissions: ["admin.all"]`
   - `isAdmin: true`
3. Expected: Role fields are ignored, or request is rejected

**Violation:** User can set their own role to a higher-privilege role.

**Severity:** Critical

---

### VERT-003: Permission Parameter Injection

**Rule:** Users must not be able to grant themselves permissions through request parameters.

**Test:**
1. Identify APIs that accept permission-related data
2. Include permission fields in the request:
   - `permissions: ["user.delete"]`
   - `authorities: ["ROLE_ADMIN"]`
   - `scope: "all"`
3. Expected: Permission fields are ignored, or request is rejected

**Violation:** User can grant themselves additional permissions.

**Severity:** Critical

---

### VERT-004: Admin Function Access

**Rule:** Administrative functions must be restricted to admin roles only.

**Test:**
1. Identify all admin functions (user management, system config, role assignment, etc.)
2. Attempt each function as every non-admin role
3. Expected: 403 Forbidden for all

**Violation:** Non-admin role can access admin functions.

**Severity:** Critical

---

## Horizontal Privilege Escalation

Horizontal privilege escalation occurs when a user can access resources belonging to another user at the same privilege level.

### HORIZ-001: IDOR — Path Parameter

**Rule:** Users must not access other users' resources by changing ID path parameters.

**Test:**
1. User A has resource with ID-X
2. User B has resource with ID-Y
3. User B sends `GET /resources/ID-X`
4. Expected: 403 Forbidden

**Violation:** User B can access User A's resource by ID (IDOR vulnerability).

**Severity:** High

---

### HORIZ-002: IDOR — Query Parameter

**Rule:** Users must not access other users' resources by changing query parameters.

**Test:**
1. User B sends `GET /resources?ownerId=User-A-ID`
2. Or `GET /resources?userId=User-A-ID`
3. Expected: 403 or empty result

**Violation:** User can query another user's resources via query parameter.

**Severity:** High

---

### HORIZ-003: IDOR — Request Body

**Rule:** Users must not access or modify other users' resources by including their IDs in request body.

**Test:**
1. User B sends `POST /resources` with body `{ "ownerId": "User-A-ID" }`
2. Or `PUT /resources` with body containing User A's resource ID
3. Expected: 403 or the ownerId field is ignored

**Violation:** User can create resources owned by another user, or modify another user's resources.

**Severity:** High

---

### HORIZ-004: Nested Resource Access

**Rule:** Users must not access other users' nested resources.

**Test:**
1. User A has nested resources at `/users/User-A-ID/resources`
2. User B sends `GET /users/User-A-ID/resources`
3. Expected: 403 Forbidden

**Violation:** User can access another user's nested resources.

**Severity:** High

---

### HORIZ-005: Sequential ID Enumeration

**Rule:** The system must prevent resource enumeration through sequential IDs.

**Test:**
1. Identify a resource with sequential or predictable IDs
2. Attempt to access IDs not belonging to the current user
3. Expected: 403 for resources not owned by the user (even if they exist)

**Violation:** User can enumerate and access resources by guessing IDs.

**Severity:** Medium (if IDs are predictable), High (if data is sensitive)

---

## Parameter Tampering

### TAMPER-001: Identity Field Tampering

**Rule:** Modifying identity fields in requests must not grant unauthorized access.

**Fields to test:**
- `userId`, `ownerId`, `createdBy`, `updatedBy`
- `accountId`, `profileId`

**Test:**
1. Send a legitimate request with your own identity fields
2. Send the same request with another user's identity fields
3. Expected: Second request is denied or identity fields are ignored

**Violation:** Changing identity fields grants access to another user's data.

**Severity:** High

---

### TAMPER-002: Scope Field Tampering

**Rule:** Modifying scope fields in requests must not grant access outside authorized scope.

**Fields to test:**
- `departmentId`, `organizationId`, `tenantId`
- `companyId`, `groupId`, `teamId`

**Test:**
1. Send a legitimate request with your own scope fields
2. Send the same request with a different scope field value
3. Expected: Second request is denied or scope fields are ignored

**Violation:** Changing scope fields grants access to data outside authorized scope.

**Severity:** High

---

### TAMPER-003: Resource ID Tampering

**Rule:** Modifying resource identifiers must not grant access to unauthorized resources.

**Fields to test:**
- `resourceId`, `entityId`, `recordId`
- `fileId`, `documentId`, `orderId`

**Test:**
1. Send a legitimate request with an authorized resource ID
2. Send the same request with an unauthorized resource ID
3. Expected: Second request is denied

**Violation:** Changing resource IDs grants access to unauthorized resources.

**Severity:** High

---

## Batch Authorization Bypass

### BATCH-001: Mixed Authorization Batch

**Rule:** Batch operations must check authorization for each item individually.

**Test:**
1. Create a batch request containing:
   - IDs the user is authorized to access
   - IDs the user is NOT authorized to access
2. Send the batch request
3. Verify that the response only contains authorized items

**Violation:** Batch response includes data from unauthorized IDs.

**Severity:** High

---

### BATCH-002: Batch Scope Bypass

**Rule:** Batch operations must respect data scope for each item.

**Test:**
1. User has department scope (Department A)
2. Send batch request with IDs from both Department A and Department B
3. Expected: Only Department A data is returned

**Violation:** Batch operation returns data from outside the user's scope.

**Severity:** High

---

## Severity Summary

| Category | Typical Severity |
|---|---|
| Vertical escalation (direct) | Critical |
| Role/permission injection | Critical |
| IDOR (path parameter) | High |
| IDOR (query/body) | High |
| Parameter tampering (identity) | High |
| Parameter tampering (scope) | High |
| Batch authorization bypass | High |
| Sequential ID enumeration | Medium to High |
