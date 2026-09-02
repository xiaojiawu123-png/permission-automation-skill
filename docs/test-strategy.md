# Test Strategy / 测试策略

## Testing Philosophy / 测试理念

Permission testing is fundamentally different from functional testing. Functional testing verifies that the system does what it should. Permission testing verifies that the system **prevents** what it should not allow.

权限测试与功能测试有着本质区别。功能测试验证系统“做了它应该做的事”，而权限测试验证系统“**阻止了它不应该允许的事**”。

Every permission test has two possible outcomes:

每一个权限测试都有两种可能的结果：
- **Expected deny:** The system correctly rejects an unauthorized action / **预期拒绝：** 系统正确地拒绝了未授权的操作
- **Unexpected allow:** The system incorrectly permits an unauthorized action (this is a vulnerability) / **意外放行：** 系统错误地允许了未授权的操作（这就是一个漏洞）

## Test Categories / 测试类别

### 1. Authentication Tests / 认证测试

Verify that the system correctly requires and validates authentication.

验证系统能够正确地要求并校验身份认证。

| Scenario<br>场景 | Request<br>请求 | Expected<br>预期结果 |
|---|---|---|
| No token<br>无令牌 | Request without any credential<br>不携带任何凭证发起请求 | 401 Unauthorized<br>401 未授权 |
| Malformed token<br>令牌格式错误 | Request with invalid token format<br>使用格式无效的令牌发起请求 | 401 Unauthorized<br>401 未授权 |
| Expired token<br>令牌已过期 | Request with expired credential<br>使用已过期的凭证发起请求 | 401 Unauthorized<br>401 未授权 |
| Revoked token<br>令牌已吊销 | Request with deactivated user's token<br>使用已被停用用户的令牌发起请求 | 401 Unauthorized<br>401 未授权 |
| Wrong environment<br>环境不匹配 | Token from different system/environment<br>使用来自其他系统/环境的令牌 | 401 Unauthorized<br>401 未授权 |

### 2. Role Permission Tests (Vertical) / 角色权限测试（纵向）

Verify that each role can only perform its authorized operations.

验证每个角色只能执行其被授权的操作。

For every role R and every API A:

对于每一个角色 R 和每一个 API A：
- If R has permission for A → expect 200 / 如果 R 对 A 有权限 → 预期返回 200
- If R lacks permission for A → expect 403 / 如果 R 对 A 无权限 → 预期返回 403

This produces a matrix of `roles x APIs` test cases.

由此可生成一个由“角色 × API”组成的测试用例矩阵。

### 3. API Permission Tests / API 权限测试

Verify that APIs enforce permissions regardless of how they are called.

验证无论以何种方式调用，API 都会强制执行权限校验。

Key scenarios:

关键场景：
- Direct API call bypassing frontend (no UI button = no protection?) / 绕过前端直接调用 API（没有界面按钮是否就意味着没有保护？）
- API call with correct permission code but wrong role / 使用正确的权限码但错误的角色调用 API
- API call after role change (permission was revoked) / 角色变更（权限已被收回）之后调用 API

### 4. Data Permission Tests / 数据权限测试

Verify that data scope filtering works correctly.

验证数据范围过滤能够正确工作。

| Scenario<br>场景 | Actor<br>操作者 | Action<br>操作 | Expected<br>预期结果 |
|---|---|---|---|
| In-scope access<br>范围内访问 | Dept A manager<br>A 部门经理 | View Dept A employee<br>查看 A 部门员工 | 200 |
| Out-of-scope access<br>范围外访问 | Dept A manager<br>A 部门经理 | View Dept B employee<br>查看 B 部门员工 | 403 or empty<br>403 或返回空 |
| Admin full access<br>管理员完全访问 | Admin<br>管理员 | View any employee<br>查看任意员工 | 200 |
| Self-only access<br>仅本人访问 | Employee<br>员工 | View own record<br>查看本人记录 | 200 |
| Cross-user access<br>跨用户访问 | Employee<br>员工 | View other's record<br>查看他人记录 | 403 |

### 5. Horizontal Privilege Escalation Tests / 水平越权测试

Verify that users cannot access other users' resources by manipulating identifiers.

验证用户无法通过操纵标识符来访问其他用户的资源。

Pattern:

模式：
```
User A has resource ID-X                          用户 A 拥有资源 ID-X
User B has resource ID-Y                          用户 B 拥有资源 ID-Y
User B requests resource ID-X → should be denied  用户 B 请求资源 ID-X → 应被拒绝
```

Test variations:

测试变体：
- Path parameter: `GET /resources/{id}` with another user's ID / 路径参数：使用他人的 ID 调用 `GET /resources/{id}`
- Query parameter: `GET /resources?ownerId=other-user` / 查询参数：`GET /resources?ownerId=other-user`
- Body parameter: `POST /resources` with `ownerId` set to another user / 请求体参数：`POST /resources`，并将 `ownerId` 设为他人
- Nested resource: `GET /users/{userId}/resources` with another user's ID / 嵌套资源：使用他人的 ID 调用 `GET /users/{userId}/resources`

### 6. Vertical Privilege Escalation Tests / 垂直越权测试

Verify that lower-privilege roles cannot perform higher-privilege operations.

验证低权限角色无法执行高权限操作。

Pattern:

模式：
```
Role "user" cannot DELETE /resources/{id}                              "user" 角色不能执行 DELETE /resources/{id}
Attacker with "user" role sends DELETE /resources/{id} → should be denied   拥有 "user" 角色的攻击者发送 DELETE /resources/{id} → 应被拒绝
```

Test variations:

测试变体：
- Direct operation: lower role calls higher role's API / 直接操作：低权限角色调用高权限角色的 API
- Role parameter injection: include `role=admin` in request body / 角色参数注入：在请求体中带上 `role=admin`
- Permission parameter injection: include `permission=delete` in request / 权限参数注入：在请求中带上 `permission=delete`
- Hierarchy bypass: attempt operations from intermediate roles / 层级绕过：尝试以中间角色执行操作

### 7. Parameter Tampering Tests / 参数篡改测试

Verify that modifying identity/scope parameters does not bypass permissions.

验证修改身份/范围类参数不会绕过权限校验。

Parameters to test:

需要测试的参数：
- `userId`, `ownerId`, `createdBy` — ownership fields / 归属类字段
- `departmentId`, `organizationId`, `tenantId` — scope fields / 范围类字段
- `roleId`, `role`, `permissions` — role/permission fields / 角色/权限类字段
- `resourceId`, `entityId`, `recordId` — resource identifiers / 资源标识符

For each parameter:

对于每一个参数：
1. Send request with legitimate value → expect 200 / 使用合法值发送请求 → 预期返回 200
2. Send request with another user's value → expect 403 or ignore / 使用他人的值发送请求 → 预期返回 403 或忽略该值
3. Send request with elevated role value → expect 403 or ignore / 使用被提升的角色值发送请求 → 预期返回 403 或忽略该值

### 8. Batch Authorization Tests / 批量操作授权测试

Verify that batch operations enforce per-item permission checks.

验证批量操作会对每一条数据逐一执行权限校验。

Pattern:

模式：
```json
{
  "ids": [authorized-id-1, unauthorized-id-2, authorized-id-3]
}
```

Expected behaviors:

预期行为：
- **Strict:** Reject entire request if any ID is unauthorized / **严格模式：** 只要有任何一个 ID 未获授权，就拒绝整个请求
- **Partial:** Return results only for authorized IDs / **部分模式：** 仅返回已授权 ID 的结果
- **Vulnerable:** Return results for all IDs including unauthorized / **存在漏洞：** 返回所有 ID 的结果，包括未授权的

The test must verify that unauthorized IDs do not appear in the response.

测试必须验证未授权的 ID 不会出现在响应中。

## Coverage Model / 覆盖模型

### Minimum Coverage Requirements / 最低覆盖要求

Every permission test suite must cover:

每一套权限测试都必须覆盖：

1. **All roles** — every role in the system has test cases / **所有角色**——系统中的每个角色都有对应的测试用例
2. **All APIs** — every protected API has positive and negative tests / **所有 API**——每个受保护的 API 都有正向和反向测试
3. **All boundaries** — every permission boundary is tested from both sides / **所有边界**——每个权限边界都从允许和拒绝两侧进行测试
4. **All data scopes** — every data scope rule has in-scope and out-of-scope tests / **所有数据范围**——每条数据范围规则都有范围内和范围外的测试
5. **All escalation vectors** — every IDOR, parameter tampering, and batch bypass vector / **所有越权途径**——每一种 IDOR、参数篡改和批量绕过途径

### Coverage Matrix / 覆盖矩阵

```
                    Auth  Role  API  Data  Horiz  Vert  Tamper  Batch
admin                -     +    +    +     -      -     +       +
manager              -     +    +    +     -      -     +       +
employee             -     +    +    +     +      +     +       +
unauthenticated      +     -    -    -     -      -     -       -
```

`+` = must have test cases / 必须包含测试用例
`-` = not applicable / 不适用

## Test Design Principles / 测试设计原则

### 1. One Assertion Per Concern / 每个关注点只用一个断言
Each test case verifies one specific permission boundary. Do not combine multiple assertions in a single test.

每个测试用例只验证一个特定的权限边界。不要在单个测试中组合多个断言。

### 2. Clear Naming / 命名清晰
Test names must describe:

测试名称必须能够描述：
- Who is acting (role) / 谁在操作（角色）
- What they are doing (operation) / 在做什么（操作）
- What the expected outcome is (allow/deny) / 预期结果是什么（允许/拒绝）

Example: `test_manager_cannot_delete_employee_returns_403`

示例：`test_manager_cannot_delete_employee_returns_403`（含义为“经理无法删除员工，返回 403”）

### 3. Independent Tests / 测试相互独立
Each test must be independently executable. No test should depend on the state left by a previous test.

每个测试都必须能够独立执行。任何测试都不应依赖于前一个测试所遗留的状态。

### 4. Deterministic / 结果确定性
Tests must produce the same result every time. Avoid dependencies on timing, random data, or external state changes.

测试每次运行都必须产生相同的结果。避免依赖时序、随机数据或外部状态变化。

### 5. Fast Feedback / 快速反馈
Token caching and connection reuse keep the test suite fast. Permission tests should complete in seconds, not minutes.

通过令牌缓存和连接复用来保持测试套件的快速运行。权限测试应在数秒内完成，而不是数分钟。

## Severity Classification / 严重性分级

| Severity<br>严重级别 | Description<br>描述 | Example<br>示例 |
|---|---|---|
| **Critical**<br>**致命** | Complete authorization bypass<br>完全绕过授权 | Unauthenticated access to admin API<br>未经认证即可访问管理员 API |
| **High**<br>**高危** | Privilege escalation<br>权限提升 | Lower role can perform admin operations<br>低权限角色可执行管理员操作 |
| **High**<br>**高危** | Data leakage<br>数据泄露 | Cross-tenant data access<br>跨租户数据访问 |
| **Medium**<br>**中危** | Partial authorization bypass<br>部分绕过授权 | Batch operation returns unauthorized data<br>批量操作返回未授权数据 |
| **Medium**<br>**中危** | IDOR<br>越权访问 | User can view another user's resource by ID<br>用户可通过 ID 查看他人资源 |
| **Low**<br>**低危** | Inconsistent enforcement<br>校验不一致 | Same resource, different endpoints, different checks<br>同一资源在不同端点校验不一致 |
| **Low**<br>**低危** | Information disclosure<br>信息泄露 | Error message reveals permission structure<br>错误消息暴露权限结构 |
