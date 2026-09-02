# Role Permission Testing Rules / 角色权限测试规则

## Purpose / 目的

Define what to test for role-based access control and how to classify findings.

定义基于角色的访问控制（RBAC）测试内容以及如何对发现的问题进行分类。

## Scope / 范围

Role permission testing verifies that each role can only perform its authorized operations and is correctly denied for unauthorized operations.

角色权限测试验证每个角色只能执行其被授权的操作，并且对于未授权的操作会被正确拒绝。

## Test Rules / 测试规则

### ROLE-001: Positive Permission (Allow) / ROLE-001：正向权限验证（允许）

**Rule:** If a role has a permission, requests from that role must succeed.

**规则：** 如果某角色拥有某项权限，则该角色发出的请求必须成功。

**Test:**
1. For each role R and each permission P assigned to R
2. Identify the API(s) that correspond to P
3. Send a request as a user with role R to each API
4. Expected: 200 (or appropriate success code)

**测试方法：**
1. 针对每个角色 R 以及分配给 R 的每项权限 P
2. 识别与权限 P 对应的 API
3. 以具有角色 R 的用户身份向每个 API 发送请求
4. 预期结果：返回 200（或相应的成功状态码）

**Violation:** Authorized request is denied (false positive — permission misconfiguration).

**违规判定：** 已授权的请求被拒绝（误报——权限配置错误）。

**Severity:** Medium (functional issue, not security issue)

**严重程度：** 中等（Medium，属于功能性问题，而非安全问题）

---

### ROLE-002: Negative Permission (Deny) / ROLE-002：反向权限验证（拒绝）

**Rule:** If a role does NOT have a permission, requests from that role must be denied.

**规则：** 如果某角色没有某项权限，则该角色发出的请求必须被拒绝。

**Test:**
1. For each role R and each permission P NOT assigned to R
2. Identify the API(s) that correspond to P
3. Send a request as a user with role R to each API
4. Expected: 403 Forbidden

**测试方法：**
1. 针对每个角色 R 以及未分配给 R 的每项权限 P
2. 识别与权限 P 对应的 API
3. 以具有角色 R 的用户身份向每个 API 发送请求
4. 预期结果：返回 403 Forbidden

**Violation:** Unauthorized request succeeds (privilege escalation).

**违规判定：** 未授权的请求执行成功（权限提升）。

**Severity:** High to Critical (depending on the operation)

**严重程度：** 高危至严重（High to Critical，取决于具体操作）

---

### ROLE-003: Role Hierarchy Boundaries / ROLE-003：角色层级边界

**Rule:** If roles are hierarchical, verify that boundary permissions are correctly enforced.

**规则：** 如果角色存在层级关系，需验证各层级边界的权限得到正确执行。

**Test:**
1. Identify role hierarchy (e.g., admin > manager > employee)
2. For each boundary between adjacent roles:
   - Test that the higher role can do things the lower role cannot
   - Test that the lower role cannot do things only the higher role should
3. Expected: Clear permission boundary at each level

**测试方法：**
1. 识别角色层级结构（例如：管理员 > 经理 > 员工）
2. 针对相邻角色之间的每个边界：
   - 测试较高级别角色可以执行较低级别角色无法执行的操作
   - 测试较低级别角色无法执行仅应由较高级别角色执行的操作
3. 预期结果：每个层级都有清晰的权限边界

**Violation:** Lower role can perform higher role's operations, or higher role is unexpectedly restricted.

**违规判定：** 低级别角色可以执行高级别角色的操作，或高级别角色被意外限制。

**Severity:** High

**严重程度：** 高危（High）

---

### ROLE-004: Multi-Role Users / ROLE-004：多角色用户

**Rule:** If a user has multiple roles, the effective permissions should be the union (or as defined by policy).

**规则：** 如果用户拥有多个角色，其有效权限应为各角色权限的并集（或按策略定义的方式计算）。

**Test:**
1. Identify users with multiple roles
2. Verify that the user can access all resources from all assigned roles
3. Verify that the user cannot access resources from unassigned roles
4. Expected: Permission matches the union of all role permissions

**测试方法：**
1. 识别拥有多个角色的用户
2. 验证该用户可以访问其所有已分配角色对应的全部资源
3. 验证该用户无法访问未分配角色对应的资源
4. 预期结果：权限与所有角色权限的并集一致

**Violation:** User gets permissions from roles they don't have, or is denied permissions they should have.

**违规判定：** 用户获得了其并不拥有的角色的权限，或其本应拥有的权限被拒绝。

**Severity:** Medium

**严重程度：** 中等（Medium）

---

### ROLE-005: Role Change Propagation / ROLE-005：角色变更传播

**Rule:** When a user's role changes, their effective permissions must update immediately.

**规则：** 当用户的角色发生变更时，其有效权限必须立即更新。

**Test:**
1. Authenticate as a user with role R1
2. Have an admin change the user's role to R2
3. Use the original token to make requests
4. Expected: Requests allowed by R2 but not R1 should fail until re-authentication, OR the system should reflect the change immediately (depending on design)

**测试方法：**
1. 以具有角色 R1 的用户身份进行认证
2. 由管理员将该用户的角色变更为 R2
3. 使用原有令牌继续发送请求
4. 预期结果：R2 允许但 R1 不允许的请求，在重新认证之前应当失败；或者系统应当立即反映变更结果（取决于系统设计）

**Violation:** User retains permissions from a removed role.

**违规判定：** 用户仍保留已被移除角色的权限。

**Severity:** High

**严重程度：** 高危（High）

---

## Test Matrix Construction / 测试矩阵构建

For N roles and M APIs, the role permission test matrix has N x M entries:

对于 N 个角色和 M 个 API，角色权限测试矩阵共有 N x M 个条目：

```
              API-1    API-2    API-3   ...  API-M
role-1       allow    deny     allow        deny
role-2       deny     allow    deny         allow
...
role-N       deny     deny     allow        deny
```

Every cell in this matrix must have at least one test case.

该矩阵中的每一个单元格都必须至少对应一个测试用例。

## Classification Guide / 分类指南

| Finding / 发现的问题 | Classification / 分类 |
|---|---|
| Role can access unauthorized API / 角色可以访问未授权的 API | Vertical Privilege Escalation / 垂直越权 |
| Role denied authorized API / 角色被拒绝访问已授权的 API | Permission Misconfiguration / 权限配置错误 |
| Hierarchy boundary not enforced / 层级边界未强制执行 | Role Hierarchy Violation / 角色层级违规 |
| Role change not reflected / 角色变更未生效 | Stale Permission / 权限未及时更新（陈旧权限） |
