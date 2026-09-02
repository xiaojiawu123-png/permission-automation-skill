# Permission Model / 权限模型

## What Is a Permission Model? / 什么是权限模型？

A permission model defines **who** can do **what** to **which resources** under **which conditions**. Every application with access control has a permission model, whether it is explicitly documented or implicitly enforced through code.

权限模型定义了在**何种条件**下，**谁**可以对**哪些资源**执行**什么操作**。每一个具备访问控制的应用都有一个权限模型，无论它是被明确地记录成文档，还是通过代码隐式地强制执行。

## Core Entities / 核心实体

### User / 用户
An identity that can authenticate to the system. Users are assigned one or more roles.

一个可以向系统进行认证的身份。用户会被分配一个或多个角色。

### Role / 角色
A named collection of permissions. Roles simplify permission management by grouping permissions that typically go together.

一组有名称的权限集合。角色通过将通常一起使用的权限归为一组，从而简化权限管理。

### Permission / 权限
An atomic authorization to perform a specific operation on a specific resource. Permissions are the fundamental unit of access control.

对特定资源执行特定操作的原子级授权。权限是访问控制的基本单元。

### Resource / 资源
Any protected entity in the system. Resources can be:

系统中任何受保护的实体。资源可以是：
- **API endpoints** (e.g., `POST /users`, `DELETE /orders/{id}`) / **API 端点**（例如 `POST /users`、`DELETE /orders/{id}`）
- **UI elements** (e.g., menus, buttons, pages) / **界面元素**（例如菜单、按钮、页面）
- **Data records** (e.g., a specific user's profile, a department's reports) / **数据记录**（例如某个用户的资料、某个部门的报表）
- **System functions** (e.g., export, import, admin panel) / **系统功能**（例如导出、导入、管理后台）

### Operation / 操作
An action performed on a resource. Common operations:

对资源执行的动作。常见操作包括：
- `query` / `read` — view or retrieve / 查看或检索
- `create` — add new / 新增
- `update` — modify existing / 修改已有数据
- `delete` — remove / 删除
- `export` — extract data / 导出数据
- `approve` / `reject` — workflow actions / 审批/驳回等流程动作

### Data Scope / 数据范围
The subset of data that a role is allowed to access. Data scope is orthogonal to operation permission — a role may have `query` permission but only on data within its scope.

某个角色被允许访问的数据子集。数据范围与操作权限是正交的——一个角色可能拥有 `query`（查询）权限，但仅限于其范围内的数据。

Common data scope patterns:

常见的数据范围模式：
- **All data** — no filtering (typically admin) / **全部数据**——不做过滤（通常为管理员）
- **Department scope** — data belonging to the user's department / **部门范围**——属于用户所在部门的数据
- **Organization scope** — data belonging to the user's organization / **组织范围**——属于用户所在组织的数据
- **Self scope** — only the user's own data / **本人范围**——仅用户本人的数据
- **Custom scope** — arbitrary business rules / **自定义范围**——任意业务规则

## Permission Model Types / 权限模型类型

### Role-Based Access Control (RBAC) / 基于角色的访问控制（RBAC）
Permissions are assigned to roles, and users are assigned to roles.

权限被分配给角色，用户则被分配给角色。

```
User → Role → Permission → Resource + Operation
```

**Characteristics:** / **特征：**
- Simple to understand and manage / 易于理解和管理
- Works well for organizations with clear role hierarchies / 适用于角色层级清晰的组织
- Most common model in enterprise applications / 是企业应用中最常见的模型

### Attribute-Based Access Control (ABAC) / 基于属性的访问控制（ABAC）
Permissions are evaluated based on attributes of the user, resource, and environment.

权限依据用户、资源和环境的属性进行动态评估。

```
Access = f(User.attributes, Resource.attributes, Environment.attributes)
```

**Characteristics:** / **特征：**
- More flexible than RBAC / 比 RBAC 更灵活
- Can express complex policies (time-of-day, location, data classification) / 能够表达复杂策略（时段、位置、数据密级等）
- Harder to audit and test / 更难审计和测试

### Policy-Based Access Control / 基于策略的访问控制
Permissions are defined through policies that combine multiple conditions.

权限通过组合多个条件的策略来定义。

```
Policy: IF user.department == resource.department AND user.level >= 3 THEN allow
```

**Characteristics:** / **特征：**
- Most expressive model / 表达能力最强的模型
- Often used in combination with RBAC / 常与 RBAC 结合使用
- Policies can be difficult to maintain at scale / 在大规模场景下策略可能难以维护

## Permission Granularity / 权限粒度

### Coarse-Grained / 粗粒度
Permissions at the module or page level:

在模块或页面级别的权限：
```
can_access_user_module: true
can_access_order_module: false
```

### Fine-Grained / 细粒度
Permissions at the individual operation level:

在单个操作级别的权限：
```
user.query: true
user.create: true
user.update: false
user.delete: false
```

### Data-Level / 数据级
Permissions filtered by data attributes:

按数据属性进行过滤的权限：
```
user.query: true
data_scope: department
```

## Common Vulnerability Patterns / 常见漏洞模式

### 1. Missing Permission Check / 权限校验缺失
An API endpoint exists without any permission verification.

某个 API 端点存在，却没有任何权限校验。

### 2. Inconsistent Enforcement / 校验不一致
Permission is checked on some endpoints but not others for the same resource.

对同一资源，某些端点做了权限校验，另一些却没有。

### 3. Frontend-Only Protection / 仅前端保护
Permission is enforced only in the UI, not at the API level.

权限仅在界面层强制执行，而未在 API 层实施。

### 4. Broken Data Scope / 数据范围失效
API returns data outside the user's authorized scope.

API 返回了超出用户授权范围的数据。

### 5. IDOR (Insecure Direct Object Reference) / 越权访问（不安全的直接对象引用）
User can access another user's resource by changing an ID parameter.

用户通过修改 ID 参数即可访问其他用户的资源。

### 6. Mass Assignment / 批量赋值
User can modify fields they should not have access to by including them in the request body.

用户通过在请求体中带上本无权访问的字段，即可修改这些字段。

### 7. Batch Bypass / 批量操作绕过
Single-item permission check is bypassed through batch/bulk operations.

单条数据的权限校验通过批量/大批量操作被绕过。

### 8. Role Manipulation / 角色篡改
User can change their effective role through request parameters.

用户可以通过请求参数改变自身实际生效的角色。

## Why Test Permissions? / 为什么要测试权限？

Permission vulnerabilities are among the most critical security issues because they:

权限漏洞是最严重的安全问题之一，原因在于它们会：
- Expose sensitive data to unauthorized users / 将敏感数据暴露给未授权用户
- Allow unauthorized modifications or deletions / 允许未经授权的修改或删除
- Can lead to complete system compromise through privilege escalation / 可能通过权限提升导致整个系统被完全攻陷
- Are often invisible to functional testing (the system "works" but is insecure) / 往往无法被功能测试发现（系统“能正常运行”，却并不安全）
- Are commonly introduced during development and rarely caught by standard test suites / 常在开发过程中被引入，且很少被标准测试套件捕获
