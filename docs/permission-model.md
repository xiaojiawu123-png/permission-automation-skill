# Permission Model

## What Is a Permission Model?

A permission model defines **who** can do **what** to **which resources** under **which conditions**. Every application with access control has a permission model, whether it is explicitly documented or implicitly enforced through code.

## Core Entities

### User
An identity that can authenticate to the system. Users are assigned one or more roles.

### Role
A named collection of permissions. Roles simplify permission management by grouping permissions that typically go together.

### Permission
An atomic authorization to perform a specific operation on a specific resource. Permissions are the fundamental unit of access control.

### Resource
Any protected entity in the system. Resources can be:
- **API endpoints** (e.g., `POST /users`, `DELETE /orders/{id}`)
- **UI elements** (e.g., menus, buttons, pages)
- **Data records** (e.g., a specific user's profile, a department's reports)
- **System functions** (e.g., export, import, admin panel)

### Operation
An action performed on a resource. Common operations:
- `query` / `read` — view or retrieve
- `create` — add new
- `update` — modify existing
- `delete` — remove
- `export` — extract data
- `approve` / `reject` — workflow actions

### Data Scope
The subset of data that a role is allowed to access. Data scope is orthogonal to operation permission — a role may have `query` permission but only on data within its scope.

Common data scope patterns:
- **All data** — no filtering (typically admin)
- **Department scope** — data belonging to the user's department
- **Organization scope** — data belonging to the user's organization
- **Self scope** — only the user's own data
- **Custom scope** — arbitrary business rules

## Permission Model Types

### Role-Based Access Control (RBAC)
Permissions are assigned to roles, and users are assigned to roles.

```
User → Role → Permission → Resource + Operation
```

**Characteristics:**
- Simple to understand and manage
- Works well for organizations with clear role hierarchies
- Most common model in enterprise applications

### Attribute-Based Access Control (ABAC)
Permissions are evaluated based on attributes of the user, resource, and environment.

```
Access = f(User.attributes, Resource.attributes, Environment.attributes)
```

**Characteristics:**
- More flexible than RBAC
- Can express complex policies (time-of-day, location, data classification)
- Harder to audit and test

### Policy-Based Access Control
Permissions are defined through policies that combine multiple conditions.

```
Policy: IF user.department == resource.department AND user.level >= 3 THEN allow
```

**Characteristics:**
- Most expressive model
- Often used in combination with RBAC
- Policies can be difficult to maintain at scale

## Permission Granularity

### Coarse-Grained
Permissions at the module or page level:
```
can_access_user_module: true
can_access_order_module: false
```

### Fine-Grained
Permissions at the individual operation level:
```
user.query: true
user.create: true
user.update: false
user.delete: false
```

### Data-Level
Permissions filtered by data attributes:
```
user.query: true
data_scope: department
```

## Common Vulnerability Patterns

### 1. Missing Permission Check
An API endpoint exists without any permission verification.

### 2. Inconsistent Enforcement
Permission is checked on some endpoints but not others for the same resource.

### 3. Frontend-Only Protection
Permission is enforced only in the UI, not at the API level.

### 4. Broken Data Scope
API returns data outside the user's authorized scope.

### 5. IDOR (Insecure Direct Object Reference)
User can access another user's resource by changing an ID parameter.

### 6. Mass Assignment
User can modify fields they should not have access to by including them in the request body.

### 7. Batch Bypass
Single-item permission check is bypassed through batch/bulk operations.

### 8. Role Manipulation
User can change their effective role through request parameters.

## Why Test Permissions?

Permission vulnerabilities are among the most critical security issues because they:
- Expose sensitive data to unauthorized users
- Allow unauthorized modifications or deletions
- Can lead to complete system compromise through privilege escalation
- Are often invisible to functional testing (the system "works" but is insecure)
- Are commonly introduced during development and rarely caught by standard test suites
