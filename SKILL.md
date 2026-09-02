# Permission Automation Testing Skill

> A technology-agnostic, reusable AI skill for automated permission model analysis, permission matrix generation, test scenario creation, token management, privilege escalation detection, and security risk reporting.

---

## 1. Purpose

This skill provides a **methodology and execution flow** for AI agents to perform comprehensive permission testing on any software project. It is not bound to any specific technology stack, framework, or business domain.

The skill guides the AI through:

1. Analyzing the target project
2. Identifying authentication mechanisms
3. Discovering users, roles, and permissions
4. Building a permission matrix
5. Generating test scenarios
6. Producing executable test code
7. Detecting privilege escalation vulnerabilities
8. Reporting security risks

---

## 2. Core Concepts

All terminology below is **abstract**. Concrete mappings depend on the target project.

| Concept | Description |
|---|---|
| **User** | An identity that can authenticate to the system |
| **Role** | A named set of permissions assigned to users |
| **Permission** | A specific allowed operation on a resource |
| **Resource** | Any protected entity (API endpoint, page, data record, menu item) |
| **Operation** | An action on a resource (create, read, update, delete, export, etc.) |
| **Data Scope** | The subset of data a role is allowed to access |
| **API** | A programmatic interface that can be protected by permissions |
| **Authentication** | The mechanism that verifies user identity and issues credentials |
| **Token / Credential** | The artifact produced by authentication, used in subsequent requests |
| **Permission Matrix** | A structured mapping of Role x Resource x Operation x Expected Result |

---

## 3. Execution Phases

The AI MUST execute these phases in order. Each phase builds on the previous.

### Phase 1: Project Analysis

**Goal:** Understand the target project structure and technology.

Actions:
1. Scan the project root for configuration files, dependency manifests, and framework indicators
2. Identify the programming language, test framework, and API framework in use
3. Identify existing test directories, fixtures, and test utilities
4. Identify existing authentication/login modules
5. Record findings for use in subsequent phases

Key questions to answer:
- What language and framework does this project use?
- What test framework is in use (if any)?
- Is there an existing HTTP/API client?
- Is there existing authentication code?
- Are there existing test fixtures or conftest files?

**Output:** Project profile (language, framework, test framework, existing infrastructure).

---

### Phase 2: Authentication Identification

**Goal:** Discover how the system authenticates users.

Actions:
1. Search for login endpoints, authentication routes, or auth middleware
2. Identify the authentication protocol (JWT, OAuth2, Session, API Key, SAML, custom, etc.)
3. Identify how tokens/credentials are obtained (API call, configuration, environment variable, etc.)
4. Identify how tokens are passed in requests (Header, Cookie, Query param, etc.)
5. Identify token refresh mechanisms if present
6. Check if the project already has token management utilities

**Reuse rule:** If the project already has login utilities, token managers, or auth fixtures, the AI MUST reuse them. Do not create duplicate authentication code.

**Output:** Authentication profile (protocol, token acquisition method, token transport, existing utilities).

---

### Phase 3: User and Role Discovery

**Goal:** Identify all users and roles in the system.

Actions:
1. Search for role definitions (database schemas, configuration files, seed data, constants, enums)
2. Search for user accounts (seed data, test fixtures, environment variables, configuration)
3. Map users to roles
4. Identify if roles are hierarchical (e.g., admin > manager > user)
5. Identify if there are role assignment APIs

**Sources to check:**
- Database migration files or schema definitions
- Configuration files (YAML, JSON, properties, env)
- Seed data or fixture files
- Source code constants and enums
- API route definitions for user/role management

**Output:** User list, role list, user-to-role mapping.

---

### Phase 4: Permission Discovery

**Goal:** Identify all permissions defined in the system.

Actions:
1. Search for permission definitions (constants, enums, database records, configuration)
2. Search for permission checks in code (decorators, middleware, guards, interceptors)
3. Map permissions to resources and operations
4. Identify permission naming conventions (e.g., `resource.action`, `resource:action`, `RESOURCE_ACTION`)
5. Identify if permissions are role-based, attribute-based, or policy-based

**Sources to check:**
- Permission/authority constant files
- Role-permission mapping tables or configuration
- Middleware or decorator definitions
- Route/controller annotations
- Policy or guard classes

**Output:** Permission catalog (permission name, resource, operation, type).

---

### Phase 5: API Discovery

**Goal:** Identify all APIs/endpoints that require permission protection.

Actions:
1. Scan route definitions, controller files, or API specifications (OpenAPI/Swagger)
2. For each API, identify: HTTP method, path, required permissions, expected role
3. Identify which APIs are public vs. protected
4. Identify APIs that perform sensitive operations (create, update, delete, export)
5. Group APIs by resource domain

**Sources to check:**
- Route registration files
- Controller/handler classes
- OpenAPI/Swagger specifications
- API gateway configuration
- Middleware chains

**Output:** API catalog (method, path, required permission, resource domain).

---

### Phase 6: Data Permission Discovery

**Goal:** Identify data-level access controls.

Actions:
1. Search for data filtering logic based on user attributes (department, organization, owner, etc.)
2. Identify data scope rules (all data, own department, own data only, custom)
3. Identify how data ownership is determined (foreign keys, user IDs, department IDs, etc.)
4. Identify multi-tenancy mechanisms if present

**Sources to check:**
- Query builders or ORM filters that reference current user
- Data scope annotations or decorators
- Service layer filtering logic
- Multi-tenancy middleware

**Output:** Data scope rules per role (scope type, scope field, filtering mechanism).

---

### Phase 7: Permission Matrix Generation

**Goal:** Build a complete permission matrix from all discovered information.

The matrix has the following structure:

```yaml
- role: <role_name>
  resource: <resource_name>
  operation: <operation>
  api: <http_method> <path>
  permission: <permission_code>
  expected_result: allow | deny
  data_scope: <scope_description>
  notes: <optional>
```

Actions:
1. Cross-reference roles, permissions, APIs, and data scopes
2. For each role x API combination, determine expected result (allow/deny)
3. Document data scope constraints
4. Flag any ambiguities or gaps for user review
5. Present the matrix for user confirmation before proceeding

**Output:** `permission_matrix.yaml` — complete, reviewable permission matrix.

---

### Phase 8: Test Scenario Generation

**Goal:** Generate comprehensive test scenarios from the permission matrix.

The AI MUST generate scenarios for ALL of the following categories:

#### 8.1 Authentication Tests
- Request without any token/credential
- Request with malformed token
- Request with expired token
- Request with token for a different system/environment
- Request with revoked/deactivated user token

#### 8.2 Role Permission Tests (Vertical)
- For each role, test every API they SHOULD access (positive)
- For each role, test every API they SHOULD NOT access (negative)
- Test role hierarchy boundaries

#### 8.3 API Permission Tests
- Direct API access bypassing frontend restrictions
- API access with correct permission but wrong role
- API access after role change (user had permission, then lost it)

#### 8.4 Data Permission Tests
- Access data within allowed scope (positive)
- Access data outside allowed scope (negative)
- Cross-department data access
- Cross-organization data access
- Data access after ownership change

#### 8.5 Horizontal Privilege Escalation Tests
- User A accessing User B's resources by ID substitution
- User A modifying User B's resources
- User A deleting User B's resources
- IDOR (Insecure Direct Object Reference) patterns

#### 8.6 Vertical Privilege Escalation Tests
- Lower-privilege role performing higher-privilege operations
- Role manipulation in request parameters
- Forced role elevation attempts

#### 8.7 Parameter Tampering Tests
- Modify `userId`, `ownerId`, `createdBy` in requests
- Modify `departmentId`, `organizationId`, `tenantId` in requests
- Modify `resourceId`, `entityId` to access other users' resources
- Add or change role/permission fields in request body

#### 8.8 Batch Authorization Tests
- Batch operations containing mix of authorized and unauthorized resource IDs
- Bulk query with IDs outside data scope
- Array parameter injection to bypass single-item checks

**Output:** Test scenario list with category, description, preconditions, expected result.

---

### Phase 9: Test Code Generation

**Goal:** Generate executable test code matching the project's technology stack.

Actions:
1. Determine the test framework from Phase 1 (pytest, JUnit, Jest, etc.)
2. Determine the HTTP client from Phase 1 (requests, axios, fetch, etc.)
3. Check for existing test infrastructure to reuse (fixtures, clients, helpers)
4. Generate test code that:
   - Uses the project's existing patterns and conventions
   - Reuses existing authentication utilities
   - Reads test data from YAML/JSON configuration files (not hardcoded)
   - Implements token caching and reuse
   - Includes clear test names describing the scenario
   - Asserts both status code and response body where appropriate

**Code generation rules:**
- NEVER hardcode credentials, tokens, URLs, or IDs in test code
- Load all test data from external configuration files
- Use environment variables for environment-specific values (base URL, etc.)
- Follow the project's existing code style and naming conventions
- Place tests in the project's existing test directory structure

**Output:** Test files ready to execute.

---

### Phase 10: Test Execution

**Goal:** Run the generated tests and collect results.

Actions:
1. Verify test environment is accessible
2. Verify test users and credentials are valid
3. Execute tests using the project's test runner
4. Collect results (pass/fail/error/skip)
5. Capture response details for failed tests

**Output:** Raw test results.

---

### Phase 11: Failure Analysis

**Goal:** Analyze test failures to distinguish between permission bugs and test issues.

Actions:
1. For each failed test, examine the actual response
2. Classify failures:
   - **True positive:** The system correctly denied an unauthorized action (test passed as expected)
   - **False negative:** The system incorrectly allowed an unauthorized action (permission bug)
   - **False positive:** The system incorrectly denied an authorized action (permission misconfiguration)
   - **Test issue:** The test itself has a problem (bad data, wrong endpoint, etc.)
3. For permission bugs, assess severity and impact
4. For test issues, fix and re-run

**Output:** Classified failure report.

---

### Phase 12: Security Risk Report

**Goal:** Produce a comprehensive permission security assessment.

The report MUST include:

#### Normal Permission Issues
- Missing permission checks on APIs
- Inconsistent permission enforcement
- Overly permissive role configurations

#### Vertical Privilege Escalation
- Lower-privilege roles able to perform admin operations
- Role boundaries not enforced at API level

#### Horizontal Privilege Escalation
- Users able to access other users' data by ID manipulation
- Missing ownership validation

#### Data Permission Issues
- Cross-department data leakage
- Missing data scope filtering
- Data scope bypass through direct API access

#### API Authorization Issues
- APIs accessible without authentication
- APIs missing permission decorators/middleware
- Inconsistent authorization across similar endpoints

#### Authentication Issues
- Weak token validation
- Missing token expiration checks
- Token reuse after logout/deactivation

#### Potential Security Risks
- IDOR vulnerabilities
- Mass assignment vulnerabilities
- Batch authorization bypass
- Parameter tampering vectors

**Output format:**
```
## Permission Security Assessment Report

### Summary
- Total APIs tested: N
- Total test scenarios: N
- Passed: N
- Failed: N
- Critical issues: N
- High issues: N
- Medium issues: N
- Low issues: N

### Critical Findings
[Detailed description of each critical finding]

### Detailed Results
[Category-by-category breakdown]

### Recommendations
[Prioritized list of remediation actions]
```

---

## 4. Token Management Strategy

### 4.1 Abstract Token Flow

```
User Identity
    |
    v
Authentication Mechanism (discovered in Phase 2)
    |
    v
Credential Artifact (Token / Session / API Key)
    |
    v
Request Injection (Header / Cookie / Query)
    |
    v
Permission Test Execution
```

### 4.2 Token Lifecycle Rules

1. **Acquire once per role:** Obtain a token for each role at the start of the test session
2. **Cache tokens:** Store tokens in memory for reuse across all test cases
3. **Refresh proactively:** If a token expires during testing, refresh it automatically
4. **Isolate per role:** Each role's token is independent; never share tokens between roles
5. **Clean up:** Invalidate or discard tokens after test session completes

### 4.3 Token Configuration

Tokens MUST be configured through external files, not hardcoded:

```yaml
# users.yaml - abstract structure
users:
  - username: <field_name_from_project>
    password: <field_name_from_project>
    role: <role_name>
    auth_endpoint: <endpoint_if_varies>
```

The AI MUST adapt field names to match the target project's actual authentication API.

---

## 5. Project Adaptation Rules

### 5.1 Reuse-First Principle

Before creating ANY file, the AI MUST check if the project already has:

| Component | Check For |
|---|---|
| HTTP Client | Existing API client, request wrapper, test client |
| Auth Utility | Login function, token manager, auth fixture |
| Test Fixtures | conftest, setup/teardown, before/after hooks |
| Test Data | Existing user data, seed files, fixture data |
| Assertions | Custom assertion helpers, response validators |
| Configuration | Environment config, test config, base URL settings |

If any of these exist, the AI MUST reuse them.

### 5.2 Non-Interference Principle

The AI MUST NOT:
- Modify business logic code
- Refactor existing code
- Delete existing tests
- Change API endpoints or behavior
- Modify permission configurations
- Weaken test assertions
- Change expected results

If modification is necessary, the AI MUST explain why and get user approval first.

### 5.3 Convention Matching

Generated code MUST match the project's conventions:
- File naming (snake_case, camelCase, kebab-case)
- Directory structure (where tests live)
- Import patterns
- Assertion style
- Error handling patterns

---

## 6. Data Separation Rules

### 6.1 Test Data Files

All test data MUST be in external configuration files:

| File | Contents |
|---|---|
| `users.yaml` | User accounts, credentials, role assignments |
| `permissions.yaml` | Permission definitions and mappings |
| `permission_matrix.yaml` | Complete role x resource x operation matrix |

### 6.2 No Hardcoding

The following MUST NOT appear in test code:
- Usernames or passwords
- Token values
- IP addresses or hostnames
- User IDs or resource IDs (use parameterized references)
- Database connection strings

### 6.3 Environment Configuration

Environment-specific values use environment variables or `.env` files:
- `BASE_URL` — the API base URL
- `AUTH_ENDPOINT` — the login endpoint (if not discoverable)
- `TOKEN_HEADER` — custom token header name (if non-standard)

---

## 7. Invocation

To use this skill, provide the following prompt to an AI agent:

```
Use the Permission Automation Testing Skill to analyze and test permissions in this project.

Please:
1. Analyze the current project structure and technology stack
2. Identify the authentication mechanism and token acquisition method
3. Discover all users and roles
4. Discover all permissions
5. Discover all APIs requiring permission protection
6. Identify data permission rules
7. Build a complete permission matrix
8. Generate permission test scenarios
9. Generate executable test code
10. Execute tests
11. Analyze failures
12. Output a permission security risk report
```

The AI will follow Phases 1-12 defined in this document, adapting to the project's specific technology stack and conventions.

---

## 8. Example

See `examples/demo-api/` for a complete fictional example demonstrating:
- Permission model definition (users, roles, permissions)
- Permission matrix configuration
- Test code generation
- All test categories (authentication, vertical/horizontal privilege escalation, data permissions, parameter tampering, batch authorization)

The demo uses a fictional "Employee Management API" with three roles (admin, manager, employee) and is completely decoupled from this skill definition.

---

## 9. Extensibility

This skill is designed to be extended:

- **Custom permission models:** Add new permission types (attribute-based, policy-based) in Phase 4
- **Custom test categories:** Add new test scenario categories in Phase 8
- **Custom report formats:** Adapt the Phase 12 report structure to organizational needs
- **CI/CD integration:** The generated tests can run in any CI/CD pipeline that supports the project's test framework

---

## 10. References

- `docs/architecture.md` — Skill architecture and design decisions
- `docs/permission-model.md` — Permission model theory and patterns
- `docs/test-strategy.md` — Testing strategy and coverage model
- `docs/token-strategy.md` — Token management deep dive
- `docs/configuration.md` — Configuration file reference
- `rules/` — Detailed rules for each permission testing category
- `templates/` — Reusable template files for configuration and test code
- `examples/demo-api/` — Complete working example
