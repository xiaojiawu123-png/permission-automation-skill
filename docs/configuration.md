# Configuration Reference

This document describes the configuration files used by the Permission Automation Testing Skill. All test data is stored in external YAML files, never hardcoded in test code.

## File Overview

| File | Purpose | Required |
|---|---|---|
| `users.yaml` | User accounts and role assignments | Yes |
| `permissions.yaml` | Permission definitions and role mappings | Yes |
| `permission_matrix.yaml` | Complete role x resource x operation matrix | Yes |
| `.env` or environment variables | Environment-specific settings | Yes (base URL at minimum) |

## users.yaml

Defines the test accounts used for permission testing.

### Template Structure

```yaml
# users.yaml
# Define test accounts for each role in the system.
# Adapt field names to match your project's authentication API.

auth:
  endpoint: /api/auth/login        # Login endpoint path
  method: POST                      # HTTP method
  body_format: json                 # json | form | query
  username_field: username          # Field name for username in request
  password_field: password          # Field name for password in request
  token_field: data.token           # JSON path to token in response
  token_transport: header           # header | cookie | query
  token_header_name: Authorization  # Header name
  token_header_prefix: Bearer      # Header prefix

users:
  - username: admin_user
    password: "${ADMIN_PASSWORD}"
    role: admin
    description: "System administrator with full access"

  - username: manager_user
    password: "${MANAGER_PASSWORD}"
    role: manager
    department: department_a
    description: "Department manager with department-scoped access"

  - username: employee_user_a
    password: "${EMPLOYEE_PASSWORD}"
    role: employee
    department: department_a
    description: "Regular employee in department A"

  - username: employee_user_b
    password: "${EMPLOYEE_PASSWORD}"
    role: employee
    department: department_b
    description: "Regular employee in department B (for cross-user tests)"
```

### Field Reference

| Field | Description |
|---|---|
| `auth.endpoint` | The login API path |
| `auth.method` | HTTP method for login |
| `auth.body_format` | How credentials are sent |
| `auth.username_field` | Request field name for username |
| `auth.password_field` | Request field name for password |
| `auth.token_field` | JSON path to extract token from response |
| `auth.token_transport` | How to pass token in subsequent requests |
| `auth.token_header_name` | Header name for token |
| `auth.token_header_prefix` | Header value prefix (e.g., "Bearer") |
| `users[].username` | Login username |
| `users[].password` | Login password (use env var references) |
| `users[].role` | The role this user has |
| `users[].department` | Optional: department for data scope tests |
| `users[].description` | Optional: human-readable description |

## permissions.yaml

Defines the permission model for the target system.

### Template Structure

```yaml
# permissions.yaml
# Define all permissions and their role mappings.

resources:
  - name: employee
    description: "Employee records"
    operations:
      - query
      - create
      - update
      - delete

role_permissions:
  - role: admin
    permissions:
      - employee.query
      - employee.create
      - employee.update
      - employee.delete
    data_scope: all

  - role: manager
    permissions:
      - employee.query
      - employee.create
      - employee.update
    data_scope: department

  - role: employee
    permissions:
      - employee.self.query
      - employee.self.update
    data_scope: self
```

### Field Reference

| Field | Description |
|---|---|
| `resources[].name` | Resource identifier |
| `resources[].description` | Human-readable description |
| `resources[].operations` | List of valid operations |
| `role_permissions[].role` | Role name |
| `role_permissions[].permissions` | List of granted permissions |
| `role_permissions[].data_scope` | Data scope for this role (`all`, `department`, `self`, or custom) |

## permission_matrix.yaml

The complete matrix of role x resource x operation x expected result.

### Template Structure

```yaml
# permission_matrix.yaml
# Each entry defines one testable permission boundary.

matrix:
  # Admin can do everything
  - role: admin
    resource: employee
    operation: query
    api: GET /api/employees
    expected: allow
    data_scope: all

  - role: admin
    resource: employee
    operation: delete
    api: DELETE /api/employees/{id}
    expected: allow
    data_scope: all

  # Manager cannot delete
  - role: manager
    resource: employee
    operation: delete
    api: DELETE /api/employees/{id}
    expected: deny
    expected_status: 403

  # Employee cannot create
  - role: employee
    resource: employee
    operation: create
    api: POST /api/employees
    expected: deny
    expected_status: 403

  # Employee can only access own data
  - role: employee
    resource: employee
    operation: self.query
    api: GET /api/employees/{id}
    expected: allow
    data_scope: self
    condition: "id == current_user.id"

  - role: employee
    resource: employee
    operation: self.query
    api: GET /api/employees/{id}
    expected: deny
    expected_status: 403
    condition: "id != current_user.id"
```

### Field Reference

| Field | Description |
|---|---|
| `matrix[].role` | The role being tested |
| `matrix[].resource` | The resource being accessed |
| `matrix[].operation` | The operation being performed |
| `matrix[].api` | The API endpoint (`METHOD /path`) |
| `matrix[].expected` | `allow` or `deny` |
| `matrix[].expected_status` | Expected HTTP status code (default: 200 for allow, 403 for deny) |
| `matrix[].data_scope` | Data scope constraint |
| `matrix[].condition` | Optional condition expression |

## Environment Variables

Environment-specific values are loaded from `.env` or system environment:

| Variable | Description | Required |
|---|---|---|
| `BASE_URL` | API base URL (e.g., `http://localhost:8080`) | Yes |
| `ADMIN_PASSWORD` | Admin user password | Yes |
| `MANAGER_PASSWORD` | Manager user password | Yes |
| `EMPLOYEE_PASSWORD` | Employee user password | Yes |
| `AUTH_ENDPOINT` | Override login endpoint (optional) | No |
| `TOKEN_HEADER` | Override token header name (optional) | No |

## Configuration Guidelines

1. **Use environment variables for secrets** — passwords and tokens should never be in plain text in YAML files
2. **Use `${VAR}` syntax** — reference environment variables in YAML values
3. **One file per concern** — users, permissions, and matrix are separate files
4. **Version control** — YAML files can be committed; `.env` should be in `.gitignore`
5. **Document custom fields** — if your project has non-standard fields, document them in the YAML comments
