# Data Permission Testing Rules / 数据权限测试规则

## Purpose / 目的

Define what to test for data-level access control and how to classify findings.

定义数据级访问控制的测试内容以及如何对发现的问题进行分类。

## Scope / 范围

Data permission testing verifies that users can only access data within their authorized scope, even when they have permission to use the API.

数据权限测试验证用户只能访问其授权范围内的数据，即使用户拥有使用该 API 的权限也是如此。

## Data Scope Types / 数据范围类型

| Scope / 范围 | Description / 描述 | Example / 示例 |
|---|---|---|
| **All** / 全部 | No data filtering / 不进行数据过滤 | Admin sees all records / 管理员可查看所有记录 |
| **Department** / 部门 | Data within the user's department / 用户所在部门内的数据 | Manager sees only their department's employees / 经理只能查看本部门的员工 |
| **Organization** / 组织 | Data within the user's organization / 用户所在组织内的数据 | Org admin sees only their org's data / 组织管理员只能查看本组织的数据 |
| **Self** / 本人 | Only the user's own data / 仅用户本人的数据 | Employee sees only their own record / 员工只能查看自己的记录 |
| **Custom** / 自定义 | Arbitrary business rules / 任意业务规则 | Team lead sees their team + adjacent teams / 团队负责人可查看本团队及相邻团队的数据 |

## Test Rules / 测试规则

### DATA-001: In-Scope Access (Positive) / DATA-001：范围内访问（正向验证）

**Rule:** Users must be able to access data within their authorized scope.

**规则：** 用户必须能够访问其授权范围内的数据。

**Test:**
1. For each role and its data scope:
   - Identify data records within scope
   - Send a request to access those records
   - Expected: 200 OK with data returned

**测试方法：**
1. 针对每个角色及其数据范围：
   - 识别范围内的数据记录
   - 发送请求以访问这些记录
   - 预期结果：返回 200 OK 并携带数据

**Violation:** User cannot access data within their scope (misconfiguration).

**违规判定：** 用户无法访问其范围内的数据（配置错误）。

**Severity:** Medium (functional issue)

**严重程度：** 中等（Medium，属于功能性问题）

---

### DATA-002: Out-of-Scope Access (Negative) / DATA-002：范围外访问（反向验证）

**Rule:** Users must NOT be able to access data outside their authorized scope.

**规则：** 用户绝不能访问其授权范围之外的数据。

**Test:**
1. For each role and its data scope:
   - Identify data records OUTSIDE scope
   - Send a request to access those records
   - Expected: 403 Forbidden, or 200 with empty/filtered result

**测试方法：**
1. 针对每个角色及其数据范围：
   - 识别范围外的数据记录
   - 发送请求以访问这些记录
   - 预期结果：返回 403 Forbidden，或返回 200 但结果为空/已被过滤

**Violation:** User can access data outside their scope.

**违规判定：** 用户可以访问其范围之外的数据。

**Severity:** High (data leakage)

**严重程度：** 高危（High，数据泄露）

---

### DATA-003: Cross-Department Access / DATA-003：跨部门访问

**Rule:** Users with department scope must not access other departments' data.

**规则：** 数据范围为“部门”的用户不得访问其他部门的数据。

**Test:**
1. Identify users in different departments with the same role
2. User from Department A attempts to access Department B's data
3. Expected: 403 or empty result

**测试方法：**
1. 识别不同部门中具有相同角色的用户
2. 部门 A 的用户尝试访问部门 B 的数据
3. 预期结果：返回 403 或空结果

**Violation:** Cross-department data access.

**违规判定：** 存在跨部门数据访问。

**Severity:** High

**严重程度：** 高危（High）

---

### DATA-004: Cross-Organization Access / DATA-004：跨组织访问

**Rule:** Users with organization scope must not access other organizations' data.

**规则：** 数据范围为“组织”的用户不得访问其他组织的数据。

**Test:**
1. Identify users in different organizations with the same role
2. User from Organization A attempts to access Organization B's data
3. Expected: 403 or empty result

**测试方法：**
1. 识别不同组织中具有相同角色的用户
2. 组织 A 的用户尝试访问组织 B 的数据
3. 预期结果：返回 403 或空结果

**Violation:** Cross-organization data access (multi-tenancy breach).

**违规判定：** 存在跨组织数据访问（多租户隔离被突破）。

**Severity:** Critical

**严重程度：** 严重（Critical）

---

### DATA-005: Self-Scope Enforcement / DATA-005：本人范围强制执行

**Rule:** Users with self scope must only access their own data.

**规则：** 数据范围为“本人”的用户只能访问自己的数据。

**Test:**
1. Identify two users with self scope (User A and User B)
2. User A attempts to access User B's data by:
   - Using User B's ID in path parameter
   - Using User B's ID in query parameter
   - Using User B's ID in request body
3. Expected: 403 or empty result for all

**测试方法：**
1. 识别两个数据范围为“本人”的用户（用户 A 和用户 B）
2. 用户 A 尝试通过以下方式访问用户 B 的数据：
   - 在路径参数中使用用户 B 的 ID
   - 在查询参数中使用用户 B 的 ID
   - 在请求体中使用用户 B 的 ID
3. 预期结果：以上方式均返回 403 或空结果

**Violation:** User can access another user's data despite self-scope restriction.

**违规判定：** 尽管存在“本人”范围限制，用户仍能访问其他用户的数据。

**Severity:** High

**严重程度：** 高危（High）

---

### DATA-006: Scope Filter Bypass / DATA-006：范围过滤绕过

**Rule:** Data scope filtering must not be bypassable through query manipulation.

**规则：** 数据范围过滤不得通过操纵查询参数的方式被绕过。

**Test:**
1. Identify APIs that filter data by scope
2. Attempt to bypass filtering by:
   - Adding explicit scope parameters (e.g., `?department=other_dept`)
   - Using search/filter parameters that ignore scope
   - Using sort/order parameters that leak data from other scopes
   - Using pagination to iterate beyond scope boundaries
3. Expected: Scope filtering persists regardless of query parameters

**测试方法：**
1. 识别按范围过滤数据的 API
2. 尝试通过以下方式绕过过滤：
   - 添加显式的范围参数（例如 `?department=other_dept`）
   - 使用忽略范围的搜索/过滤参数
   - 使用会泄露其他范围数据的排序参数
   - 使用分页参数迭代超出范围边界
3. 预期结果：无论查询参数如何变化，范围过滤始终生效

**Violation:** Scope filter can be bypassed.

**违规判定：** 范围过滤可以被绕过。

**Severity:** High

**严重程度：** 高危（High）

---

### DATA-007: Scope After Ownership Change / DATA-007：所有权变更后的范围

**Rule:** When data ownership changes, access must update accordingly.

**规则：** 当数据所有权发生变更时，访问权限必须随之更新。

**Test:**
1. User A owns Resource X
2. User B (same department) can access Resource X (within scope)
3. Resource X is transferred to User C (different department)
4. User B attempts to access Resource X again
5. Expected: Access denied (if scope is department-based and C is in different dept)

**测试方法：**
1. 用户 A 拥有资源 X
2. 用户 B（同一部门）可以访问资源 X（在范围内）
3. 资源 X 被转移给用户 C（不同部门）
4. 用户 B 再次尝试访问资源 X
5. 预期结果：访问被拒绝（若范围基于部门且用户 C 属于不同部门）

**Violation:** User retains access to data that has moved outside their scope.

**违规判定：** 用户仍可访问已转移至其范围之外的数据。

**Severity:** Medium

**严重程度：** 中等（Medium）

---

## Test Data Requirements / 测试数据要求

Data permission tests require carefully prepared test data:

数据权限测试需要精心准备的测试数据：

1. **Multiple departments** — at least 2 departments with data in each
2. **Multiple users per department** — at least 1 user per department per role
3. **Identifiable data** — data records must be clearly associated with a department/user
4. **Known relationships** — the test must know which data is in-scope and which is out-of-scope

1. **多个部门** —— 至少 2 个部门，每个部门都有数据
2. **每个部门多个用户** —— 每个部门每种角色至少有 1 个用户
3. **可识别的数据** —— 数据记录必须能明确关联到某个部门/用户
4. **已知的关联关系** —— 测试必须清楚哪些数据在范围内、哪些在范围外

## Classification Guide / 分类指南

| Finding / 发现的问题 | Classification / 分类 |
|---|---|
| Access to data outside scope / 访问范围外的数据 | Data Permission Violation / 数据权限违规 |
| Cross-department access / 跨部门访问 | Cross-Department Data Leakage / 跨部门数据泄露 |
| Cross-organization access / 跨组织访问 | Multi-Tenancy Breach / 多租户隔离突破 |
| Scope filter bypass / 范围过滤绕过 | Data Scope Bypass / 数据范围绕过 |
| Self-scope violation / 本人范围违规 | Horizontal Data Access Violation / 水平越权数据访问 |
