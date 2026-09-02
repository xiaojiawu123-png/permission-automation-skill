# Configuration Reference / 配置参考

This document describes the configuration files used by the Permission Automation Testing Skill. All test data is stored in external YAML files, never hardcoded in test code.

本文介绍权限自动化测试技能所使用的配置文件。所有测试数据都存放在外部的 YAML 文件中，绝不会硬编码在测试代码里。

## File Overview / 文件概览

| File<br>文件 | Purpose<br>用途 | Required<br>是否必需 |
|---|---|---|
| `users.yaml` | User accounts and role assignments<br>用户账户与角色分配 | Yes<br>是 |
| `permissions.yaml` | Permission definitions and role mappings<br>权限定义与角色映射 | Yes<br>是 |
| `permission_matrix.yaml` | Complete role x resource x operation matrix<br>完整的“角色 × 资源 × 操作”矩阵 | Yes<br>是 |
| `.env` or environment variables<br>`.env` 或环境变量 | Environment-specific settings<br>特定环境的设置 | Yes (base URL at minimum)<br>是（至少需要基础 URL） |

## users.yaml

Defines the test accounts used for permission testing.

定义用于权限测试的测试账户。

### Template Structure / 模板结构

```yaml
# users.yaml
# Define test accounts for each role in the system.
# 为系统中的每个角色定义测试账户。
# Adapt field names to match your project's authentication API.
# 调整字段名称，以匹配你所在项目的认证 API。

auth:
  endpoint: /api/auth/login        # Login endpoint path / 登录接口路径
  method: POST                      # HTTP method / HTTP 方法
  body_format: json                 # json | form | query
  username_field: username          # Field name for username in request / 请求中用户名字段的名称
  password_field: password          # Field name for password in request / 请求中密码字段的名称
  token_field: data.token           # JSON path to token in response / 响应中令牌的 JSON 路径
  token_transport: header           # header | cookie | query
  token_header_name: Authorization  # Header name / 请求头名称
  token_header_prefix: Bearer      # Header prefix / 请求头前缀

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

### Field Reference / 字段参考

| Field<br>字段 | Description<br>说明 |
|---|---|
| `auth.endpoint` | The login API path<br>登录 API 的路径 |
| `auth.method` | HTTP method for login<br>登录所用的 HTTP 方法 |
| `auth.body_format` | How credentials are sent<br>凭证的发送方式 |
| `auth.username_field` | Request field name for username<br>请求中用户名字段的名称 |
| `auth.password_field` | Request field name for password<br>请求中密码字段的名称 |
| `auth.token_field` | JSON path to extract token from response<br>从响应中提取令牌的 JSON 路径 |
| `auth.token_transport` | How to pass token in subsequent requests<br>在后续请求中传递令牌的方式 |
| `auth.token_header_name` | Header name for token<br>令牌所用的请求头名称 |
| `auth.token_header_prefix` | Header value prefix (e.g., "Bearer")<br>请求头取值前缀（例如 "Bearer"） |
| `users[].username` | Login username<br>登录用户名 |
| `users[].password` | Login password (use env var references)<br>登录密码（使用环境变量引用） |
| `users[].role` | The role this user has<br>该用户所拥有的角色 |
| `users[].department` | Optional: department for data scope tests<br>可选：用于数据范围测试的部门 |
| `users[].description` | Optional: human-readable description<br>可选：便于阅读的描述信息 |

## permissions.yaml

Defines the permission model for the target system.

定义目标系统的权限模型。

### Template Structure / 模板结构

```yaml
# permissions.yaml
# Define all permissions and their role mappings.
# 定义所有权限及其角色映射关系。

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

### Field Reference / 字段参考

| Field<br>字段 | Description<br>说明 |
|---|---|
| `resources[].name` | Resource identifier<br>资源标识符 |
| `resources[].description` | Human-readable description<br>便于阅读的描述信息 |
| `resources[].operations` | List of valid operations<br>有效操作的列表 |
| `role_permissions[].role` | Role name<br>角色名称 |
| `role_permissions[].permissions` | List of granted permissions<br>已授予权限的列表 |
| `role_permissions[].data_scope` | Data scope for this role (`all`, `department`, `self`, or custom)<br>该角色的数据范围（`all`、`department`、`self` 或自定义） |

## permission_matrix.yaml

The complete matrix of role x resource x operation x expected result.

“角色 × 资源 × 操作 × 预期结果”的完整矩阵。

### Template Structure / 模板结构

```yaml
# permission_matrix.yaml
# Each entry defines one testable permission boundary.
# 每一个条目都定义了一个可测试的权限边界。

matrix:
  # Admin can do everything / 管理员可以执行所有操作
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

  # Manager cannot delete / 经理不能执行删除操作
  - role: manager
    resource: employee
    operation: delete
    api: DELETE /api/employees/{id}
    expected: deny
    expected_status: 403

  # Employee cannot create / 员工不能执行创建操作
  - role: employee
    resource: employee
    operation: create
    api: POST /api/employees
    expected: deny
    expected_status: 403

  # Employee can only access own data / 员工只能访问本人数据
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

### Field Reference / 字段参考

| Field<br>字段 | Description<br>说明 |
|---|---|
| `matrix[].role` | The role being tested<br>被测试的角色 |
| `matrix[].resource` | The resource being accessed<br>被访问的资源 |
| `matrix[].operation` | The operation being performed<br>被执行的操作 |
| `matrix[].api` | The API endpoint (`METHOD /path`)<br>API 端点（`METHOD /path`） |
| `matrix[].expected` | `allow` or `deny`<br>`allow`（允许）或 `deny`（拒绝） |
| `matrix[].expected_status` | Expected HTTP status code (default: 200 for allow, 403 for deny)<br>预期的 HTTP 状态码（默认：allow 为 200，deny 为 403） |
| `matrix[].data_scope` | Data scope constraint<br>数据范围约束 |
| `matrix[].condition` | Optional condition expression<br>可选的条件表达式 |

## Environment Variables / 环境变量

Environment-specific values are loaded from `.env` or system environment:

特定环境的取值从 `.env` 文件或系统环境中加载：

| Variable<br>变量 | Description<br>说明 | Required<br>是否必需 |
|---|---|---|
| `BASE_URL` | API base URL (e.g., `http://localhost:8080`)<br>API 基础 URL（例如 `http://localhost:8080`） | Yes<br>是 |
| `ADMIN_PASSWORD` | Admin user password<br>管理员用户密码 | Yes<br>是 |
| `MANAGER_PASSWORD` | Manager user password<br>经理用户密码 | Yes<br>是 |
| `EMPLOYEE_PASSWORD` | Employee user password<br>员工用户密码 | Yes<br>是 |
| `AUTH_ENDPOINT` | Override login endpoint (optional)<br>覆盖登录端点（可选） | No<br>否 |
| `TOKEN_HEADER` | Override token header name (optional)<br>覆盖令牌请求头名称（可选） | No<br>否 |

## Configuration Guidelines / 配置准则

1. **Use environment variables for secrets** — passwords and tokens should never be in plain text in YAML files / **对机密信息使用环境变量**——密码和令牌绝不应以明文形式出现在 YAML 文件中
2. **Use `${VAR}` syntax** — reference environment variables in YAML values / **使用 `${VAR}` 语法**——在 YAML 取值中引用环境变量
3. **One file per concern** — users, permissions, and matrix are separate files / **一个文件只关注一件事**——用户、权限和矩阵分别放在不同的文件中
4. **Version control** — YAML files can be committed; `.env` should be in `.gitignore` / **版本控制**——YAML 文件可以提交；`.env` 应加入 `.gitignore`
5. **Document custom fields** — if your project has non-standard fields, document them in the YAML comments / **记录自定义字段**——如果你的项目包含非标准字段，请在 YAML 注释中加以说明
