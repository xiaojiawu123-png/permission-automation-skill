---
name: permission-automation-testing
description: Analyze and automate API permission testing for RBAC and similar authorization models. Use when testing authentication, role permissions, data permissions, IDOR, horizontal or vertical privilege escalation, parameter tampering, batch authorization, permission matrices, token management, or permission security risks.
---

# Permission Automation Testing Skill / 权限自动化测试技能

> **Version / 版本:** v1.0.0
>
> A technology-agnostic, reusable AI skill for automated permission model analysis, permission matrix generation, test scenario creation, token management, privilege escalation detection, and security risk reporting.
>
> 一个技术无关的、可复用的 AI 技能，用于自动化权限模型分析、权限矩阵生成、测试场景创建、令牌管理、权限提升检测和安全风险报告。

---

## 1. Skill Metadata / 技能元数据

| Field / 字段 | Value / 值 |
|---|---|
| **Name / 名称** | Permission Automation Testing Skill / 权限自动化测试技能 |
| **Version / 版本** | v1.0.0 |
| **Type / 类型** | AI Agent Skill (Methodology + Execution Flow) / AI 代理技能（方法论 + 执行流程） |
| **Technology / 技术** | Technology-agnostic / 技术无关 |
| **Language / 语言** | Bilingual (English + Chinese) / 双语（英文 + 中文） |

---

## 2. Scope / 适用范围

### 2.1 In Scope / 适用场景

This skill applies when / 本技能适用于以下场景：

- The target project has an API layer with permission controls / 目标项目有带权限控制的 API 层
- The project uses role-based access control (RBAC) or similar permission models / 项目使用基于角色的访问控制（RBAC）或类似权限模型
- Permission testing is needed but not yet automated / 需要权限测试但尚未自动化
- Existing permission tests need to be expanded or validated / 需要扩展或验证现有权限测试

### 2.2 Out of Scope / 不适用场景

This skill does NOT cover / 本技能不涵盖：

- Performance testing or load testing / 性能测试或负载测试
- Business logic validation (only permission boundaries) / 业务逻辑验证（仅权限边界）
- Frontend UI permission rendering (only API-level enforcement) / 前端 UI 权限渲染（仅 API 级别强制执行）
- Penetration testing beyond permission boundaries / 权限边界之外的渗透测试
- Code review or static analysis / 代码审查或静态分析

### 2.3 Prerequisites / 前提条件

The AI agent needs / AI 代理需要：

- Access to the target project source code / 目标项目源代码的访问权限
- A running target API environment (dev/staging) with test accounts / 运行中的目标 API 环境（开发/预发布）及测试账户
- Network access to the target API / 目标 API 的网络访问权限

---

## 3. Inputs and Outputs / 输入与输出

### 3.1 Inputs / 输入

| Input / 输入 | Source / 来源 | Description / 描述 |
|---|---|---|
| Source code / 源代码 | Project files | For discovering permissions, roles, APIs / 用于发现权限、角色、API |
| Running API / 运行中的 API | Target environment | For executing tests / 用于执行测试 |
| Test accounts / 测试账户 | User-provided or discovered | Credentials for each role / 每个角色的凭证 |
| Permission model / 权限模型 | Source code or user-provided | Role-permission mappings / 角色-权限映射 |

### 3.2 Outputs / 输出

| Output / 输出 | Format / 格式 | Description / 描述 |
|---|---|---|
| `permissions.yaml` | YAML | System permission model / 系统权限模型 |
| `permission_matrix.yaml` | YAML | Test scenario matrix / 测试场景矩阵 |
| `users.yaml` | YAML | Test user configuration / 测试用户配置 |
| Test code / 测试代码 | Project language | Executable permission tests / 可执行的权限测试 |
| Security report / 安全报告 | Markdown | Permission security assessment / 权限安全评估 |

---

## 4. Core Concepts / 核心概念

All terminology below is **abstract**. Concrete mappings depend on the target project.

以下所有术语均为**抽象概念**。具体映射取决于目标项目。

| Concept / 概念 | Description / 描述 |
|---|---|
| **User / 用户** | An identity that can authenticate to the system / 可以认证到系统的身份 |
| **Role / 角色** | A named set of permissions assigned to users / 分配给用户的命名权限集合 |
| **Permission / 权限** | A specific allowed operation on a resource / 对资源的特定允许操作 |
| **Resource / 资源** | Any protected entity (API endpoint, page, data record, menu item) / 任何受保护的实体（API端点、页面、数据记录、菜单项） |
| **Operation / 操作** | An action on a resource (create, read, update, delete, export, etc.) / 对资源的操作（创建、读取、更新、删除、导出等） |
| **Data Scope / 数据范围** | The subset of data a role is allowed to access / 角色被允许访问的数据子集 |
| **Token / Credential / 令牌/凭证** | The artifact produced by authentication, used in subsequent requests / 认证产生的制品，用于后续请求 |
| **Permission Matrix / 权限矩阵** | A structured mapping of Role x Resource x Operation x Expected Result / 角色 x 资源 x 操作 x 预期结果的结构化映射 |

---

## 5. Execution Phases / 执行阶段

The AI MUST execute these phases in order. Each phase builds on the previous.

AI 必须按顺序执行这些阶段。每个阶段建立在前一个阶段之上。

### Phase 1: Project Analysis / 第一阶段：项目分析

**Goal / 目标：** Understand the target project structure and technology. / 了解目标项目结构和技术。

Actions / 操作：
1. Scan the project root for configuration files, dependency manifests, and framework indicators / 扫描项目根目录的配置文件、依赖清单和框架标识
2. Identify the programming language, test framework, and API framework in use / 识别使用的编程语言、测试框架和 API 框架
3. Identify existing test directories, fixtures, and test utilities / 识别现有的测试目录、固件和测试工具
4. Identify existing authentication/login modules / 识别现有的认证/登录模块
5. Record findings for use in subsequent phases / 记录发现以供后续阶段使用

**Output / 输出：** Project profile (language, framework, test framework, existing infrastructure). / 项目概况（语言、框架、测试框架、现有基础设施）。

---

### Phase 2: Authentication Identification / 第二阶段：认证识别

**Goal / 目标：** Discover how the system authenticates users. / 发现系统如何认证用户。

Actions / 操作：
1. Search for login endpoints, authentication routes, or auth middleware / 搜索登录端点、认证路由或认证中间件
2. Identify the authentication protocol (JWT, OAuth2, Session, API Key, SAML, custom, etc.) / 识别认证协议（JWT、OAuth2、Session、API Key、SAML、自定义等）
3. Identify how tokens/credentials are obtained (API call, configuration, environment variable, etc.) / 识别如何获取令牌/凭证（API调用、配置、环境变量等）
4. Identify how tokens are passed in requests (Header, Cookie, Query param, etc.) / 识别令牌如何在请求中传递（Header、Cookie、Query参数等）
5. Check if the project already has token management utilities / 检查项目是否已有令牌管理工具

**Reuse rule / 复用规则：** If the project already has login utilities, token managers, or auth fixtures, the AI MUST reuse them. / 如果项目已有登录工具、令牌管理器或认证固件，AI 必须复用它们。

**Output / 输出：** Authentication profile (protocol, token acquisition, token transport). / 认证概况（协议、令牌获取方式、令牌传输方式）。

---

### Phase 3: User and Role Discovery / 第三阶段：用户和角色发现

**Goal / 目标：** Identify all users and roles in the system. / 识别系统中的所有用户和角色。

Actions / 操作：
1. Search for role definitions (database schemas, configuration files, seed data, constants, enums) / 搜索角色定义（数据库模式、配置文件、种子数据、常量、枚举）
2. Search for user accounts (seed data, test fixtures, environment variables, configuration) / 搜索用户账户（种子数据、测试固件、环境变量、配置）
3. Map users to roles / 映射用户到角色
4. Identify if roles are hierarchical / 识别角色是否具有层级关系

**Output / 输出：** User list, role list, user-to-role mapping. / 用户列表、角色列表、用户-角色映射。

---

### Phase 4: Permission Discovery / 第四阶段：权限发现

**Goal / 目标：** Identify all permissions defined in the system. / 识别系统中定义的所有权限。

Actions / 操作：
1. Search for permission definitions (constants, enums, database records, configuration) / 搜索权限定义（常量、枚举、数据库记录、配置）
2. Search for permission checks in code (decorators, middleware, guards, interceptors) / 搜索代码中的权限检查（装饰器、中间件、守卫、拦截器）
3. Map permissions to resources and operations / 将权限映射到资源和操作
4. Identify permission naming conventions / 识别权限命名约定

**Output / 输出：** Permission catalog (permission name, resource, operation, type). / 权限目录（权限名称、资源、操作、类型）。

---

### Phase 5: API Discovery / 第五阶段：API 发现

**Goal / 目标：** Identify all APIs/endpoints that require permission protection. / 识别所有需要权限保护的 API/端点。

Actions / 操作：
1. Scan route definitions, controller files, or API specifications / 扫描路由定义、控制器文件或 API 规范
2. For each API, identify: HTTP method, path, required permissions, expected role / 对每个 API，识别：HTTP 方法、路径、所需权限、预期角色
3. Identify which APIs are public vs. protected / 识别哪些 API 是公开的，哪些是受保护的
4. Group APIs by resource domain / 按资源域对 API 分组

**Output / 输出：** API catalog (method, path, required permission, resource domain). / API 目录（方法、路径、所需权限、资源域）。

---

### Phase 6: Data Permission Discovery / 第六阶段：数据权限发现

**Goal / 目标：** Identify data-level access controls. / 识别数据级别的访问控制。

Actions / 操作：
1. Search for data filtering logic based on user attributes / 搜索基于用户属性的数据过滤逻辑
2. Identify data scope rules (all data, own department, own data only, custom) / 识别数据范围规则
3. Identify how data ownership is determined / 识别如何确定数据所有权

**Output / 输出：** Data scope rules per role. / 每个角色的数据范围规则。

---

### Phase 7: Permission Matrix Generation / 第七阶段：权限矩阵生成

**Goal / 目标：** Build a complete permission matrix from all discovered information. / 从所有发现的信息构建完整的权限矩阵。

Actions / 操作：
1. Cross-reference roles, permissions, APIs, and data scopes / 交叉引用角色、权限、API 和数据范围
2. For each role x API combination, determine expected result (allow/deny) / 对每个角色 x API 组合，确定预期结果（允许/拒绝）
3. Document data scope constraints / 记录数据范围约束
4. Flag any ambiguities or gaps for user review / 标记任何歧义或缺失以供用户审查
5. Present the matrix for user confirmation before proceeding / 在继续之前展示矩阵供用户确认

**Output / 输出：** `permissions.yaml` + `permission_matrix.yaml` / 权限模型 + 测试场景矩阵

---

### Phase 8: Test Scenario Generation / 第八阶段：测试场景生成

**Goal / 目标：** Generate comprehensive test scenarios from the permission matrix. / 从权限矩阵生成全面的测试场景。

The AI MUST generate scenarios for ALL of the following categories / AI 必须为以下所有类别生成场景：

1. **Authentication Tests / 认证测试** — No token, invalid token, expired token / 无令牌、无效令牌、过期令牌
2. **Role Permission Tests / 角色权限测试** — Positive and negative per role / 每个角色的正向和反向测试
3. **Data Permission Tests / 数据权限测试** — Within scope and outside scope / 范围内和范围外
4. **Horizontal Privilege Escalation / 水平权限提升** — IDOR patterns / IDOR 模式
5. **Vertical Privilege Escalation / 垂直权限提升** — Lower role performing admin ops / 低角色执行管理员操作
6. **Parameter Tampering / 参数篡改** — Injecting IDs, roles, scopes / 注入ID、角色、范围
7. **Batch Authorization / 批量授权** — Mixed authorized/unauthorized IDs / 混合授权/未授权ID

**Output / 输出：** Test scenario list integrated into `permission_matrix.yaml`. / 集成到 `permission_matrix.yaml` 中的测试场景列表。

---

### Phase 9: Test Code Generation / 第九阶段：测试代码生成

**Goal / 目标：** Generate executable test code matching the project's technology stack. / 生成匹配项目技术栈的可执行测试代码。

**Code generation rules / 代码生成规则：**
- Reuse existing project infrastructure (HTTP client, auth helpers, fixtures) / 复用项目现有基础设施
- NEVER hardcode credentials, tokens, URLs, or IDs / 绝不在测试代码中硬编码凭证、令牌、URL 或 ID
- Load all test data from external YAML/JSON configuration files / 从外部 YAML/JSON 配置文件加载所有测试数据
- Use environment variables for environment-specific values / 对环境特定值使用环境变量
- Follow the project's existing code style and naming conventions / 遵循项目现有的代码风格和命名约定
- Index tokens by user name, not by role / 按用户名索引令牌，而非按角色
- Handle Bearer prefix correctly (no double-prefix) / 正确处理 Bearer 前缀（不重复添加）

**Output / 输出：** Test files ready to execute. / 准备执行的测试文件。

---

### Phase 10: Test Execution / 第十阶段：测试执行

**Goal / 目标：** Run the generated tests and collect results. / 运行生成的测试并收集结果。

**Output / 输出：** Raw test results (pass/fail/error/skip). / 原始测试结果。

---

### Phase 11: Failure Analysis / 第十一阶段：失败分析

**Goal / 目标：** Analyze test failures to distinguish between permission bugs and test issues. / 分析测试失败以区分权限缺陷和测试问题。

Classifications / 分类：
- **True positive / 真阳性：** System correctly denied unauthorized action / 系统正确拒绝未授权操作
- **False negative / 假阴性：** System incorrectly allowed unauthorized action (permission bug) / 系统错误地允许了未授权操作（权限缺陷）
- **False positive / 假阳性：** System incorrectly denied authorized action (misconfiguration) / 系统错误地拒绝了授权操作（配置错误）
- **Test issue / 测试问题：** Test itself has a problem / 测试本身有问题

**Output / 输出：** Classified failure report. / 分类的失败报告。

---

### Phase 12: Security Risk Report / 第十二阶段：安全风险报告

**Goal / 目标：** Produce a comprehensive permission security assessment. / 生成全面的权限安全评估。

The report MUST include / 报告必须包含：
- Summary statistics (total APIs, scenarios, pass/fail counts) / 汇总统计
- Critical findings (privilege escalation, IDOR, data leakage) / 关键发现
- Detailed results by category / 按类别分类的详细结果
- Prioritized remediation recommendations / 优先排序的修复建议

**Output / 输出:** Markdown security assessment report. / Markdown 安全评估报告。

---

## 6. Constraints / 执行约束

### 6.1 Reuse-First Principle / 复用优先原则

Before creating ANY file, the AI MUST check if the project already has / 在创建任何文件之前，AI 必须检查项目是否已有：
- HTTP Client / HTTP客户端
- Auth Utility / 认证工具
- Test Fixtures / 测试固件
- Test Data / 测试数据

If any exist, the AI MUST reuse them. / 如果以上任何一项存在，AI 必须复用它们。

### 6.2 Non-Interference Principle / 非干扰原则

The AI MUST NOT / AI 不得：
- Modify business logic code / 修改业务逻辑代码
- Refactor existing code / 重构现有代码
- Delete existing tests / 删除现有测试
- Change API endpoints or behavior / 更改 API 端点或行为
- Modify permission configurations / 修改权限配置
- Weaken test assertions / 削弱测试断言

If modification is necessary, the AI MUST explain why and get user approval first. / 如果必须修改，AI 必须解释原因并首先获得用户批准。

### 6.3 Data Separation / 数据分离

| File / 文件 | Responsibility / 职责 |
|---|---|
| `permissions.yaml` | System permission model (resources, roles, mappings) / 系统权限模型 |
| `permission_matrix.yaml` | Test scenario matrix (testable expectations) / 测试场景矩阵 |
| `users.yaml` | Test accounts, auth config, test data references / 测试账户、认证配置、测试数据引用 |

### 6.4 No Hardcoding / 禁止硬编码

The following MUST NOT appear in test code / 以下内容不得出现在测试代码中：
- Usernames, passwords, or token values / 用户名、密码或令牌值
- IP addresses or hostnames / IP 地址或主机名
- User IDs or resource IDs (use parameterized references from YAML) / 用户ID或资源ID（使用 YAML 中的参数化引用）

### 6.5 Token Management / 令牌管理

- Tokens are indexed by **user name**, not by role / 令牌按**用户名**索引，而非按角色
- Each user in `users.yaml` must have a unique `name` field / `users.yaml` 中每个用户必须有唯一的 `name` 字段
- This allows distinguishing multiple users with the same role (e.g., alice and bob are both "employee") / 这允许区分同一角色的多个用户
- Bearer prefix is handled by the client framework — never double-prefixed / Bearer 前缀由客户端框架处理——不重复添加

---

## 7. Invocation / 调用

To use this skill, provide the following prompt to an AI agent / 要使用此技能，请向 AI 代理提供以下提示：

```
Use the Permission Automation Testing Skill (v1.0.0) to analyze and test permissions in this project.

Please follow the 12-phase execution flow defined in SKILL.md:
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

---

## 8. References / 参考

| Path / 路径 | Contents / 内容 |
|---|---|
| `docs/architecture.md` | Skill architecture and design decisions / 技能架构和设计决策 |
| `docs/permission-model.md` | Permission model theory and patterns / 权限模型理论和模式 |
| `docs/test-strategy.md` | Testing strategy and coverage model / 测试策略和覆盖模型 |
| `docs/token-strategy.md` | Token management deep dive / 令牌管理深入 |
| `docs/configuration.md` | Configuration file reference / 配置文件参考 |
| `rules/` | Detailed rules for each permission testing category / 每个权限测试类别的详细规则 |
| `templates/` | Reusable template files / 可复用的模板文件 |
| `examples/demo-api/` | Complete fictional example / 完整的虚构示例 |
