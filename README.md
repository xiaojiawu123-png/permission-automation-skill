# Permission Automation Testing Skill

A technology-agnostic, reusable AI skill for automated permission testing — from permission model analysis to security risk reporting.

## What This Solves

Permission vulnerabilities (privilege escalation, IDOR, data leakage, missing auth checks) are among the most critical security issues in any application. They are rarely caught by functional tests because the system "works" — it just works insecurely.

This skill gives AI agents a **standardized methodology** to:

1. Analyze any project's permission model
2. Build a complete permission matrix
3. Generate and execute permission test suites
4. Detect privilege escalation vulnerabilities
5. Produce a security risk report

## Supported Test Categories

| Category | What It Tests |
|---|---|
| **Authentication** | Missing tokens, invalid tokens, expired tokens |
| **Role Permission** | Each role can only do what it's authorized for |
| **API Permission** | APIs enforce permissions regardless of frontend |
| **Menu Permission** | Hidden menus don't expose underlying APIs |
| **Data Permission** | Users only see data within their scope |
| **Vertical Privilege Escalation** | Lower roles can't perform admin operations |
| **Horizontal Privilege Escalation** | Users can't access other users' resources (IDOR) |
| **Parameter Tampering** | Modifying IDs/roles/scopes doesn't bypass permissions |
| **Batch Authorization** | Batch operations enforce per-item checks |

## Technology Agnostic

This skill does not assume any specific technology. The AI agent:

1. Scans the target project
2. Identifies the language, framework, test framework, and HTTP client
3. Generates test code matching the project's stack

| If the project uses | The AI generates |
|---|---|
| Python + pytest | pytest test files with requests |
| Java + JUnit | JUnit test classes with RestAssured |
| JavaScript + Jest | Jest test files with axios/fetch |
| Go + testing | Go test files with net/http |
| Something else | Adapts accordingly |

## Quick Start

### 1. Add to Your Project

Copy the `permission-automation-skill/` directory into your project, or add it as a submodule:

```bash
git submodule add https://github.com/your-org/permission-automation-skill.git .skill/permission-testing
```

### 2. Invoke the AI Agent

Use this prompt with your AI agent (Qoder, Cursor, Copilot, etc.):

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

The AI will follow the 12-phase execution flow defined in `SKILL.md`.

### 3. Provide Configuration

The AI will ask you to fill in (or will discover automatically):

- `users.yaml` — test accounts for each role
- `permissions.yaml` — your permission model
- `permission_matrix.yaml` — expected role x API permissions

Templates are in `templates/`. Copy them to your project and adapt.

### 4. Run Tests

```bash
# Python/pytest example
pytest tests/permission/ -v

# Java/JUnit example
mvn test -Dtest=PermissionTest

# JavaScript/Jest example
npx jest tests/permission/
```

## Project Structure

```
permission-automation-skill/
├── SKILL.md                    # Core skill: 12-phase execution flow
├── README.md                   # This file
├── LICENSE                     # MIT License
│
├── docs/                       # Strategy and theory
│   ├── architecture.md         # Skill architecture
│   ├── permission-model.md     # Permission model theory
│   ├── test-strategy.md        # Testing strategy
│   ├── token-strategy.md       # Token management
│   └── configuration.md        # Configuration reference
│
├── rules/                      # Testing rules per category
│   ├── authentication.md       # Authentication testing rules
│   ├── role.md                 # Role permission rules
│   ├── menu.md                 # Menu permission rules
│   ├── api.md                  # API permission rules
│   ├── data.md                 # Data permission rules
│   └── privilege-escalation.md # Privilege escalation rules
│
├── templates/                  # Copy-and-adapt templates
│   ├── users.yaml              # Test user configuration
│   ├── permissions.yaml        # Permission model definition
│   ├── permission_matrix.yaml  # Permission matrix template
│   └── permission_test.py      # Reference test implementation
│
└── examples/
    └── demo-api/               # Fictional Employee Management API demo
        ├── README.md
        ├── users.yaml
        ├── permissions.yaml
        ├── permission_matrix.yaml
        └── tests/
            └── test_permission.py
```

## Configuration

### users.yaml

Defines test accounts and how to authenticate:

```yaml
auth:
  endpoint: /api/auth/login
  method: POST
  body_format: json
  username_field: username
  password_field: password
  token_field: data.token
  token_transport: header
  token_header_name: Authorization
  token_header_prefix: "Bearer"

users:
  - username: "${ADMIN_USERNAME}"
    password: "${ADMIN_PASSWORD}"
    role: admin
  - username: "${USER_USERNAME}"
    password: "${USER_PASSWORD}"
    role: user
```

### Environment Variables

```bash
# .env (add to .gitignore)
BASE_URL=http://localhost:8080
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secret
USER_USERNAME=user
USER_PASSWORD=secret
```

See `docs/configuration.md` for full reference.

## Demo

The `examples/demo-api/` directory contains a complete fictional example:

- **Employee Management API** with 3 roles (admin, manager, employee)
- Full permission matrix with 40+ test scenarios
- Working pytest test code covering all test categories
- Completely fictional — no real systems referenced

See `examples/demo-api/README.md` for details.

## Key Principles

### Reuse-First

Before creating any utility, the AI checks if the project already has:
- HTTP client → reuse it
- Auth helper → reuse it
- Test fixtures → reuse them
- Test data → reuse it

### Non-Interference

The skill never:
- Modifies business code
- Deletes existing tests
- Changes API behavior
- Weakens assertions

### Data-Driven

All test data lives in YAML files, never hardcoded in test code. Passwords use environment variables.

## Extending

### Add a New Permission Model

Add rules in `rules/` and extend Phase 4 of `SKILL.md`.

### Add a New Test Category

Add rules, then extend Phase 8 (Test Scenario Generation).

### Add a New Technology Template

Add templates in `templates/` for your language/framework.

### Custom Report Format

Extend Phase 12 (Security Risk Report) in `SKILL.md`.

## Contributing

Contributions are welcome:

1. Fork the repository
2. Create a feature branch
3. Add your changes (new rules, templates, docs, or examples)
4. Ensure no real company/system information is included
5. Submit a pull request

### Contribution Guidelines

- Keep the skill technology-agnostic
- Use abstract concepts (User, Role, Resource, Permission)
- Put concrete examples only in `examples/`
- Document new rules with test patterns and severity classifications
- Never include real credentials, URLs, or system details

## License

MIT License. See [LICENSE](LICENSE).
