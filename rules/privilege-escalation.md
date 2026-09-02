# Privilege Escalation Testing Rules / 越权测试规则

## Purpose / 目的

Define what to test for privilege escalation vulnerabilities and how to classify findings.

定义越权漏洞的测试内容以及如何对发现的问题进行分类。

## Scope / 范围

Privilege escalation testing verifies that users cannot elevate their permissions beyond what their role allows, either vertically (to a higher role) or horizontally (to another user's resources).

越权测试验证用户无法将其权限提升到超出其角色允许的范围，无论是垂直方向（提升到更高级别角色）还是水平方向（访问其他用户的资源）。

## Vertical Privilege Escalation / 垂直越权

Vertical privilege escalation occurs when a lower-privilege user can perform actions reserved for higher-privilege roles.

垂直越权是指低权限用户能够执行仅保留给高权限角色的操作。

### VERT-001: Direct Operation Escalation / VERT-001：直接操作越权

**Rule:** Lower-privilege roles must not be able to perform higher-privilege operations.

**规则：** 低权限角色不得能够执行高权限操作。

**Test:**
1. Identify the role hierarchy (e.g., admin > manager > employee)
2. For each role boundary:
   - Identify operations available to the higher role but not the lower
   - Attempt each operation as a user with the lower role
   - Expected: 403 Forbidden

**测试方法：**
1. 识别角色层级（例如：管理员 > 经理 > 员工）
2. 针对每个角色边界：
   - 识别高级别角色可执行但低级别角色不可执行的操作
   - 以低级别角色的用户身份尝试执行每一项操作
   - 预期结果：返回 403 Forbidden

**Violation:** Lower role can perform higher role's operations.

**违规判定：** 低级别角色可以执行高级别角色的操作。

**Severity:** Critical

**严重程度：** 严重（Critical）

**Example:**
```
manager → DELETE /employees/{id} → should be denied (only admin can delete)
employee → POST /employees → should be denied (only admin/manager can create)
```

**示例：**
```
manager → DELETE /employees/{id} → 应被拒绝（仅管理员可删除）
employee → POST /employees → 应被拒绝（仅管理员/经理可创建）
```

---

### VERT-002: Role Parameter Injection / VERT-002：角色参数注入

**Rule:** Users must not be able to set or modify their own role through request parameters.

**规则：** 用户不得能够通过请求参数设置或修改自己的角色。

**Test:**
1. Identify APIs that accept user data (create user, update user, update profile)
2. Include role-related fields in the request body:
   - `role: "admin"`
   - `roleId: <admin_role_id>`
   - `permissions: ["admin.all"]`
   - `isAdmin: true`
3. Expected: Role fields are ignored, or request is rejected

**测试方法：**
1. 识别接受用户数据的 API（创建用户、更新用户、更新个人资料）
2. 在请求体中包含与角色相关的字段：
   - `role: "admin"`
   - `roleId: <admin_role_id>`
   - `permissions: ["admin.all"]`
   - `isAdmin: true`
3. 预期结果：角色相关字段被忽略，或请求被拒绝

**Violation:** User can set their own role to a higher-privilege role.

**违规判定：** 用户能够将自己的角色设置为更高权限的角色。

**Severity:** Critical

**严重程度：** 严重（Critical）

---

### VERT-003: Permission Parameter Injection / VERT-003：权限参数注入

**Rule:** Users must not be able to grant themselves permissions through request parameters.

**规则：** 用户不得能够通过请求参数为自己授予权限。

**Test:**
1. Identify APIs that accept permission-related data
2. Include permission fields in the request:
   - `permissions: ["user.delete"]`
   - `authorities: ["ROLE_ADMIN"]`
   - `scope: "all"`
3. Expected: Permission fields are ignored, or request is rejected

**测试方法：**
1. 识别接受权限相关数据的 API
2. 在请求中包含权限字段：
   - `permissions: ["user.delete"]`
   - `authorities: ["ROLE_ADMIN"]`
   - `scope: "all"`
3. 预期结果：权限相关字段被忽略，或请求被拒绝

**Violation:** User can grant themselves additional permissions.

**违规判定：** 用户能够为自己授予额外权限。

**Severity:** Critical

**严重程度：** 严重（Critical）

---

### VERT-004: Admin Function Access / VERT-004：管理员功能访问

**Rule:** Administrative functions must be restricted to admin roles only.

**规则：** 管理类功能必须仅限管理员角色访问。

**Test:**
1. Identify all admin functions (user management, system config, role assignment, etc.)
2. Attempt each function as every non-admin role
3. Expected: 403 Forbidden for all

**测试方法：**
1. 识别所有管理员功能（用户管理、系统配置、角色分配等）
2. 以每一个非管理员角色尝试访问每项功能
3. 预期结果：全部返回 403 Forbidden

**Violation:** Non-admin role can access admin functions.

**违规判定：** 非管理员角色可以访问管理员功能。

**Severity:** Critical

**严重程度：** 严重（Critical）

---

## Horizontal Privilege Escalation / 水平越权

Horizontal privilege escalation occurs when a user can access resources belonging to another user at the same privilege level.

水平越权是指用户能够访问同一权限级别下属于其他用户的资源。

### HORIZ-001: IDOR — Path Parameter / HORIZ-001：IDOR——路径参数

**Rule:** Users must not access other users' resources by changing ID path parameters.

**规则：** 用户不得通过修改 ID 路径参数来访问其他用户的资源。

**Test:**
1. User A has resource with ID-X
2. User B has resource with ID-Y
3. User B sends `GET /resources/ID-X`
4. Expected: 403 Forbidden

**测试方法：**
1. 用户 A 拥有 ID 为 ID-X 的资源
2. 用户 B 拥有 ID 为 ID-Y 的资源
3. 用户 B 发送 `GET /resources/ID-X`
4. 预期结果：返回 403 Forbidden

**Violation:** User B can access User A's resource by ID (IDOR vulnerability).

**违规判定：** 用户 B 可以通过 ID 访问用户 A 的资源（IDOR 漏洞）。

**Severity:** High

**严重程度：** 高危（High）

---

### HORIZ-002: IDOR — Query Parameter / HORIZ-002：IDOR——查询参数

**Rule:** Users must not access other users' resources by changing query parameters.

**规则：** 用户不得通过修改查询参数来访问其他用户的资源。

**Test:**
1. User B sends `GET /resources?ownerId=User-A-ID`
2. Or `GET /resources?userId=User-A-ID`
3. Expected: 403 or empty result

**测试方法：**
1. 用户 B 发送 `GET /resources?ownerId=User-A-ID`
2. 或发送 `GET /resources?userId=User-A-ID`
3. 预期结果：返回 403 或空结果

**Violation:** User can query another user's resources via query parameter.

**违规判定：** 用户可以通过查询参数查询其他用户的资源。

**Severity:** High

**严重程度：** 高危（High）

---

### HORIZ-003: IDOR — Request Body / HORIZ-003：IDOR——请求体

**Rule:** Users must not access or modify other users' resources by including their IDs in request body.

**规则：** 用户不得通过在请求体中包含其他用户的 ID 来访问或修改其资源。

**Test:**
1. User B sends `POST /resources` with body `{ "ownerId": "User-A-ID" }`
2. Or `PUT /resources` with body containing User A's resource ID
3. Expected: 403 or the ownerId field is ignored

**测试方法：**
1. 用户 B 发送 `POST /resources`，请求体为 `{ "ownerId": "User-A-ID" }`
2. 或发送 `PUT /resources`，请求体中包含用户 A 的资源 ID
3. 预期结果：返回 403，或 ownerId 字段被忽略

**Violation:** User can create resources owned by another user, or modify another user's resources.

**违规判定：** 用户可以创建归属于其他用户的资源，或修改其他用户的资源。

**Severity:** High

**严重程度：** 高危（High）

---

### HORIZ-004: Nested Resource Access / HORIZ-004：嵌套资源访问

**Rule:** Users must not access other users' nested resources.

**规则：** 用户不得访问其他用户的嵌套资源。

**Test:**
1. User A has nested resources at `/users/User-A-ID/resources`
2. User B sends `GET /users/User-A-ID/resources`
3. Expected: 403 Forbidden

**测试方法：**
1. 用户 A 在 `/users/User-A-ID/resources` 路径下拥有嵌套资源
2. 用户 B 发送 `GET /users/User-A-ID/resources`
3. 预期结果：返回 403 Forbidden

**Violation:** User can access another user's nested resources.

**违规判定：** 用户可以访问其他用户的嵌套资源。

**Severity:** High

**严重程度：** 高危（High）

---

### HORIZ-005: Sequential ID Enumeration / HORIZ-005：连续 ID 枚举

**Rule:** The system must prevent resource enumeration through sequential IDs.

**规则：** 系统必须防止通过连续 ID 进行资源枚举。

**Test:**
1. Identify a resource with sequential or predictable IDs
2. Attempt to access IDs not belonging to the current user
3. Expected: 403 for resources not owned by the user (even if they exist)

**测试方法：**
1. 识别使用连续或可预测 ID 的资源
2. 尝试访问不属于当前用户的 ID
3. 预期结果：对于不属于该用户的资源（即使资源确实存在），返回 403

**Violation:** User can enumerate and access resources by guessing IDs.

**违规判定：** 用户可以通过猜测 ID 来枚举并访问资源。

**Severity:** Medium (if IDs are predictable), High (if data is sensitive)

**严重程度：** 中等（Medium，若 ID 可预测）；高危（High，若数据较为敏感）

---

## Parameter Tampering / 参数篡改

### TAMPER-001: Identity Field Tampering / TAMPER-001：身份字段篡改

**Rule:** Modifying identity fields in requests must not grant unauthorized access.

**规则：** 修改请求中的身份字段不得导致未授权的访问。

**Fields to test:**
- `userId`, `ownerId`, `createdBy`, `updatedBy`
- `accountId`, `profileId`

**待测试字段：**
- `userId`、`ownerId`、`createdBy`、`updatedBy`
- `accountId`、`profileId`

**Test:**
1. Send a legitimate request with your own identity fields
2. Send the same request with another user's identity fields
3. Expected: Second request is denied or identity fields are ignored

**测试方法：**
1. 使用自己的身份字段发送一个合法请求
2. 使用其他用户的身份字段发送相同的请求
3. 预期结果：第二个请求被拒绝，或身份字段被忽略

**Violation:** Changing identity fields grants access to another user's data.

**违规判定：** 更改身份字段可以获取对其他用户数据的访问权限。

**Severity:** High

**严重程度：** 高危（High）

---

### TAMPER-002: Scope Field Tampering / TAMPER-002：范围字段篡改

**Rule:** Modifying scope fields in requests must not grant access outside authorized scope.

**规则：** 修改请求中的范围字段不得导致访问超出授权范围的数据。

**Fields to test:**
- `departmentId`, `organizationId`, `tenantId`
- `companyId`, `groupId`, `teamId`

**待测试字段：**
- `departmentId`、`organizationId`、`tenantId`
- `companyId`、`groupId`、`teamId`

**Test:**
1. Send a legitimate request with your own scope fields
2. Send the same request with a different scope field value
3. Expected: Second request is denied or scope fields are ignored

**测试方法：**
1. 使用自己的范围字段发送一个合法请求
2. 使用不同的范围字段值发送相同的请求
3. 预期结果：第二个请求被拒绝，或范围字段被忽略

**Violation:** Changing scope fields grants access to data outside authorized scope.

**违规判定：** 更改范围字段可以获取对授权范围之外数据的访问权限。

**Severity:** High

**严重程度：** 高危（High）

---

### TAMPER-003: Resource ID Tampering / TAMPER-003：资源 ID 篡改

**Rule:** Modifying resource identifiers must not grant access to unauthorized resources.

**规则：** 修改资源标识符不得导致对未授权资源的访问。

**Fields to test:**
- `resourceId`, `entityId`, `recordId`
- `fileId`, `documentId`, `orderId`

**待测试字段：**
- `resourceId`、`entityId`、`recordId`
- `fileId`、`documentId`、`orderId`

**Test:**
1. Send a legitimate request with an authorized resource ID
2. Send the same request with an unauthorized resource ID
3. Expected: Second request is denied

**测试方法：**
1. 使用已授权的资源 ID 发送一个合法请求
2. 使用未授权的资源 ID 发送相同的请求
3. 预期结果：第二个请求被拒绝

**Violation:** Changing resource IDs grants access to unauthorized resources.

**违规判定：** 更改资源 ID 可以获取对未授权资源的访问权限。

**Severity:** High

**严重程度：** 高危（High）

---

## Batch Authorization Bypass / 批量授权绕过

### BATCH-001: Mixed Authorization Batch / BATCH-001：混合授权批量操作

**Rule:** Batch operations must check authorization for each item individually.

**规则：** 批量操作必须对每一条记录单独进行授权检查。

**Test:**
1. Create a batch request containing:
   - IDs the user is authorized to access
   - IDs the user is NOT authorized to access
2. Send the batch request
3. Verify that the response only contains authorized items

**测试方法：**
1. 构造一个批量请求，包含：
   - 用户有权访问的 ID
   - 用户无权访问的 ID
2. 发送该批量请求
3. 验证响应中仅包含已授权的记录

**Violation:** Batch response includes data from unauthorized IDs.

**违规判定：** 批量响应中包含了未授权 ID 对应的数据。

**Severity:** High

**严重程度：** 高危（High）

---

### BATCH-002: Batch Scope Bypass / BATCH-002：批量范围绕过

**Rule:** Batch operations must respect data scope for each item.

**规则：** 批量操作必须对每一条记录遵守数据范围限制。

**Test:**
1. User has department scope (Department A)
2. Send batch request with IDs from both Department A and Department B
3. Expected: Only Department A data is returned

**测试方法：**
1. 用户的数据范围为部门级（部门 A）
2. 发送同时包含部门 A 和部门 B 的 ID 的批量请求
3. 预期结果：仅返回部门 A 的数据

**Violation:** Batch operation returns data from outside the user's scope.

**违规判定：** 批量操作返回了超出用户数据范围的数据。

**Severity:** High

**严重程度：** 高危（High）

---

## Severity Summary / 严重程度汇总

| Category / 类别 | Typical Severity / 典型严重程度 |
|---|---|
| Vertical escalation (direct) / 垂直越权（直接） | Critical / 严重 |
| Role/permission injection / 角色/权限注入 | Critical / 严重 |
| IDOR (path parameter) / IDOR（路径参数） | High / 高危 |
| IDOR (query/body) / IDOR（查询参数/请求体） | High / 高危 |
| Parameter tampering (identity) / 参数篡改（身份字段） | High / 高危 |
| Parameter tampering (scope) / 参数篡改（范围字段） | High / 高危 |
| Batch authorization bypass / 批量授权绕过 | High / 高危 |
| Sequential ID enumeration / 连续 ID 枚举 | Medium to High / 中等至高危 |
