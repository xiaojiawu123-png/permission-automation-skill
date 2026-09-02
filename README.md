# Permission Automation Testing Skill / 权限自动化测试技能

> **Version / 版本:** v1.0.0
>
> A technology-agnostic, reusable AI skill for automated permission testing — from permission model analysis to security risk reporting.
>
> 一个技术无关的、可复用的 AI 技能，用于自动化权限测试——从权限模型分析到安全风险报告。

---

## What This Solves / 解决什么问题

Permission vulnerabilities (privilege escalation, IDOR, data leakage, missing auth checks) are among the most critical security issues in any application. They are rarely caught by functional tests because the system "works" — it just works insecurely.

权限漏洞（权限提升、IDOR、数据泄露、缺少认证检查）是任何应用中最关键的安全问题之一。功能测试很少能发现这些问题，因为系统"能工作"——只是工作得不安全。

This skill gives AI agents a **standardized methodology** to / 本技能为 AI 代理提供**标准化方法论**：

1. Analyze any project's permission model / 分析任何项目的权限模型
2. Build a complete permission matrix / 构建完整的权限矩阵
3. Generate and execute permission test suites / 生成并执行权限测试套件
4. Detect privilege escalation vulnerabilities / 检测权限提升漏洞
5. Produce a security risk report / 生成安全风险报告

---

## Supported Test Categories / 支持的测试类别

| Category / 类别 | What It Tests / 测试内容 |
|---|---|
| **Authentication / 认证** | Missing tokens, invalid tokens, expired tokens / 缺少令牌、无效令牌、过期令牌 |
| **Role Permission / 角色权限** | Each role can only do what it's authorized for / 每个角色只能执行其被授权的操作 |
| **Data Permission / 数据权限** | Users only see data within their scope / 用户只能看到其范围内的数据 |
| **Vertical Privilege Escalation / 垂直权限提升** | Lower roles can't perform admin operations / 低角色不能执行管理员操作 |
| **Horizontal Privilege Escalation / 水平权限提升** | Users can't access other users' resources (IDOR) / 用户不能访问其他用户的资源（IDOR） |
| **Parameter Tampering / 参数篡改** | Modifying IDs/roles/scopes doesn't bypass permissions / 修改ID/角色/范围不能绕过权限 |
| **Batch Authorization / 批量授权** | Batch operations enforce per-item checks / 批量操作执行逐项检查 |

---

## Technology Agnostic / 技术无关

This skill does not assume any specific technology. The AI agent / 本技能不假设任何特定技术。AI 代理会：

1. Scans the target project / 扫描目标项目
2. Identifies the language, framework, test framework, and HTTP client / 识别语言、框架、测试框架和 HTTP 客户端
3. Generates test code matching the project's stack / 生成匹配项目技术栈的测试代码

| If the project uses / 如果项目使用 | The AI generates / AI 生成 |
|---|---|
| Python + pytest | pytest test files with requests / pytest 测试文件 + requests |
| Java + JUnit | JUnit test classes with RestAssured / JUnit 测试类 + RestAssured |
| JavaScript + Jest | Jest test files with axios/fetch / Jest 测试文件 + axios/fetch |
| Go + testing | Go test files with net/http / Go 测试文件 + net/http |
| Something else / 其他 | Adapts accordingly / 相应适配 |

---

## Quick Start / 快速开始

### Prerequisites / 前提条件

- A project with API endpoints and permission controls / 一个有 API 端点和权限控制的项目
- A running target API environment (dev/staging) with test accounts / 运行中的目标 API 环境（开发/预发布）及测试账户
- An AI agent that supports Skill execution (e.g., Qoder, Cursor, Copilot) / 支持 Skill 执行的 AI 代理

### 1. Add to Your Project / 添加到你的项目

Copy the `permission-automation-skill/` directory into your project, or add it as a submodule:

将 `permission-automation-skill/` 目录复制到你的项目中，或添加为子模块：

```bash
git submodule add https://github.com/your-org/permission-automation-skill.git .skill/permission-testing
```

### 2. Invoke the AI Agent / 调用 AI 代理

Use this prompt with your AI agent / 使用以下提示与你的 AI 代理：

```
Use the Permission Automation Testing Skill (v1.0.0) to analyze and test permissions in this project.

Please follow the 12-phase execution flow defined in SKILL.md.
```

The AI will follow the 12-phase execution flow defined in `SKILL.md`.

AI 将遵循 `SKILL.md` 中定义的12阶段执行流程。

### 3. Provide Configuration / 提供配置

The AI will ask you to fill in (or will discover automatically) / AI 会要求你填写（或自动发现）：

- `users.yaml` — test accounts for each role (each user has a unique `name`) / 每个角色的测试账户（每个用户有唯一 `name`）
- `permissions.yaml` — your permission model (resources, roles, mappings) / 你的权限模型
- `permission_matrix.yaml` — test scenarios (expected role x API permissions) / 测试场景

Templates are in `templates/`. Copy them to your project and adapt.

模板在 `templates/` 中。复制到你的项目并适配。

### 4. Run Tests / 运行测试

```bash
# Python/pytest example / 示例
pytest tests/permission/ -v

# Java/JUnit example / 示例
mvn test -Dtest=PermissionTest

# JavaScript/Jest example / 示例
npx jest tests/permission/
```

---

## Project Structure / 项目结构

```
permission-automation-skill/
├── SKILL.md                    # Core skill spec: 12-phase execution flow / 核心技能规范
├── README.md                   # This file / 本文件
├── CHANGELOG.md                # Version history / 版本历史
├── LICENSE                     # MIT License / MIT 许可证
│
├── docs/                       # Strategy and theory / 策略和理论
│   ├── architecture.md         # Skill architecture / 技能架构
│   ├── permission-model.md     # Permission model theory / 权限模型理论
│   ├── test-strategy.md        # Testing strategy / 测试策略
│   ├── token-strategy.md       # Token management / 令牌管理
│   └── configuration.md        # Configuration reference / 配置参考
│
├── rules/                      # Testing rules per category / 每个类别的测试规则
│   ├── authentication.md       # Authentication testing rules / 认证测试规则
│   ├── role.md                 # Role permission rules / 角色权限规则
│   ├── menu.md                 # Menu permission rules / 菜单权限规则
│   ├── api.md                  # API permission rules / API权限规则
│   ├── data.md                 # Data permission rules / 数据权限规则
│   └── privilege-escalation.md # Privilege escalation rules / 权限提升规则
│
├── templates/                  # Copy-and-adapt templates / 可复用模板
│   ├── users.yaml              # Test user configuration / 测试用户配置
│   ├── permissions.yaml        # System permission model / 系统权限模型
│   ├── permission_matrix.yaml  # Test scenario matrix / 测试场景矩阵
│   └── permission_test.py      # Reference test implementation / 参考测试实现
│
└── examples/
    └── demo-api/               # Fictional Employee Management API demo / 虚构员工管理API示例
        ├── README.md
        ├── users.yaml
        ├── permissions.yaml
        ├── permission_matrix.yaml
        └── tests/
            └── test_permission.py
```

---

## Configuration Files / 配置文件

### File Responsibilities / 文件职责

| File / 文件 | Responsibility / 职责 |
|---|---|
| `permissions.yaml` | System permission model: resources, roles, role-permission mappings / 系统权限模型：资源、角色、角色-权限映射 |
| `permission_matrix.yaml` | Test scenario matrix: testable expectations per category / 测试场景矩阵：每个类别的可测试预期 |
| `users.yaml` | Test accounts, auth config, test data references / 测试账户、认证配置、测试数据引用 |

### users.yaml Example / 示例

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
  - name: admin_user          # unique name — used as token index / 唯一名称——用作令牌索引
    username: "${ADMIN_USERNAME}"
    password: "${ADMIN_PASSWORD}"
    role: admin
  - name: alice
    username: "${ALICE_USERNAME}"
    password: "${ALICE_PASSWORD}"
    role: user
    department: engineering
```

### Environment Variables / 环境变量

```bash
# .env (add to .gitignore / 添加到 .gitignore)
BASE_URL=http://localhost:8080
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secret
ALICE_USERNAME=alice
ALICE_PASSWORD=secret
```

See `docs/configuration.md` for full reference. / 完整参考请参见 `docs/configuration.md`。

---

## Demo / 示例

> **Important / 重要：** The demo in `examples/demo-api/` is a **fictional** example. It demonstrates how the skill generates test code, but it requires a **real target API** to actually run. There is no bundled API server.
>
> `examples/demo-api/` 中的示例是一个**虚构**示例。它演示了技能如何生成测试代码，但需要**真实的目标 API** 才能实际运行。没有捆绑的 API 服务器。

The demo uses a fictional "Employee Management API" with / 示例使用虚构的"员工管理 API"：

- 6 test users across 3 roles (admin, manager, employee) / 6个测试用户，3个角色
- 40+ test scenarios across 7 categories / 40+测试场景，7个类别
- Complete pytest test code with user-indexed token management / 完整的 pytest 测试代码，按用户名索引令牌

To run the demo tests against your own API / 要针对你自己的 API 运行示例测试：

1. Copy `examples/demo-api/` to your project / 复制 `examples/demo-api/` 到你的项目
2. Adapt `users.yaml`, `permissions.yaml`, `permission_matrix.yaml` to your API / 适配三个 YAML 文件到你的 API
3. Set up `.env` with your test credentials / 设置 `.env` 填入测试凭证
4. Run `pytest tests/test_permission.py -v`

See `examples/demo-api/README.md` for details. / 详情请参见 `examples/demo-api/README.md`。

---

## Key Principles / 核心原则

### Reuse-First / 复用优先

Before creating any utility, the AI checks if the project already has / 在创建任何工具之前，AI 检查项目是否已有：
- HTTP client -> reuse it / HTTP 客户端 -> 复用
- Auth helper -> reuse it / 认证辅助 -> 复用
- Test fixtures -> reuse them / 测试固件 -> 复用
- Test data -> reuse it / 测试数据 -> 复用

### Non-Interference / 非干扰

The skill never / 本技能绝不：
- Modifies business code / 修改业务代码
- Deletes existing tests / 删除现有测试
- Changes API behavior / 更改 API 行为
- Weakens assertions / 削弱断言

### Data-Driven / 数据驱动

All test data lives in YAML files, never hardcoded in test code. Passwords use environment variables. Tokens are indexed by user name, not role.

所有测试数据存放在 YAML 文件中，绝不在测试代码中硬编码。密码使用环境变量。令牌按用户名索引，而非按角色。

---

## Contributing / 贡献

Contributions are welcome / 欢迎贡献：

1. Fork the repository / Fork 仓库
2. Create a feature branch / 创建功能分支
3. Add your changes (new rules, templates, docs, or examples) / 添加你的更改（新规则、模板、文档或示例）
4. Ensure no real company/system information is included / 确保不包含真实公司/系统信息
5. Submit a pull request / 提交 Pull Request

### Contribution Guidelines / 贡献指南

- Keep the skill technology-agnostic / 保持技能技术无关性
- Use abstract concepts (User, Role, Resource, Permission) / 使用抽象概念（用户、角色、资源、权限）
- Put concrete examples only in `examples/` / 仅在 `examples/` 中放置具体示例
- Never include real credentials, URLs, or system details / 绝不包含真实凭证、URL 或系统详情

---

## License / 许可证

MIT License. See [LICENSE](LICENSE). / MIT 许可证。参见 [LICENSE](LICENSE)。
