# API Permission Testing Rules / API 权限测试规则

## Purpose / 目的

Define what to test for API-level access control and how to classify findings.

定义 API 级访问控制的测试内容以及如何对发现的问题进行分类。

## Scope / 范围

API permission testing verifies that every API endpoint correctly enforces permission checks regardless of how the request is made.

API 权限测试验证无论请求以何种方式发起，每个 API 端点都能正确执行权限检查。

## Test Rules / 测试规则

### API-001: Protected API Requires Authentication / API-001：受保护 API 需要身份认证

**Rule:** Every non-public API must require authentication.

**规则：** 每个非公开 API 都必须要求身份认证。

**Test:**
1. Identify all APIs that should be protected
2. For each API, send a request without any authentication
3. Expected: 401 Unauthorized

**测试方法：**
1. 识别所有应当受保护的 API
2. 对每个 API，发送不带任何认证信息的请求
3. 预期结果：返回 401 Unauthorized

**Violation:** API returns data or performs action without authentication.

**违规判定：** API 在未认证的情况下返回数据或执行操作。

**Severity:** Critical

**严重程度：** 严重（Critical）

---

### API-002: Permission Check on Each API / API-002：每个 API 的权限检查

**Rule:** Each API must verify that the authenticated user has the required permission.

**规则：** 每个 API 都必须验证已认证用户是否具备所需的权限。

**Test:**
1. For each API, identify the required permission
2. For each role that does NOT have the required permission:
   - Send a request as a user with that role
   - Expected: 403 Forbidden
3. For each role that HAS the required permission:
   - Send a request as a user with that role
   - Expected: 200 OK

**测试方法：**
1. 针对每个 API，确定其所需权限
2. 针对每个不具备所需权限的角色：
   - 以该角色的用户身份发送请求
   - 预期结果：返回 403 Forbidden
3. 针对每个具备所需权限的角色：
   - 以该角色的用户身份发送请求
   - 预期结果：返回 200 OK

**Violation:** API does not check permission, or checks inconsistently.

**违规判定：** API 未进行权限检查，或权限检查不一致。

**Severity:** High to Critical

**严重程度：** 高危至严重（High to Critical）

---

### API-003: Frontend Bypass / API-003：前端绕过

**Rule:** APIs must enforce permissions even when the frontend does not expose the action.

**规则：** 即使前端未暴露某项操作，API 也必须强制执行权限校验。

**Test:**
1. Identify operations that are hidden in the frontend for certain roles
2. Call the corresponding API directly as a user with that role
3. Expected: 403 Forbidden

**测试方法：**
1. 识别对某些角色在前端被隐藏的操作
2. 以该角色的用户身份直接调用对应的 API
3. 预期结果：返回 403 Forbidden

**Violation:** API succeeds despite frontend hiding the action (frontend-only protection).

**违规判定：** 尽管前端隐藏了该操作，API 调用仍然成功（仅前端防护）。

**Severity:** Critical

**严重程度：** 严重（Critical）

---

### API-004: HTTP Method Enforcement / API-004：HTTP 方法强制执行

**Rule:** Permission checks must apply to all HTTP methods, not just GET.

**规则：** 权限检查必须适用于所有 HTTP 方法，而不仅仅是 GET。

**Test:**
1. For each API, test all relevant HTTP methods (GET, POST, PUT, PATCH, DELETE)
2. Verify permission check on each method
3. Expected: All methods enforce permissions

**测试方法：**
1. 针对每个 API，测试所有相关的 HTTP 方法（GET、POST、PUT、PATCH、DELETE）
2. 验证每种方法上的权限检查
3. 预期结果：所有方法均强制执行权限校验

**Violation:** Some methods (especially DELETE, PUT) skip permission checks.

**违规判定：** 某些方法（尤其是 DELETE、PUT）跳过了权限检查。

**Severity:** High

**严重程度：** 高危（High）

---

### API-005: Consistent Enforcement Across Similar Endpoints / API-005：相似端点的一致性执行

**Rule:** Similar APIs for the same resource must have consistent permission checks.

**规则：** 针对同一资源的相似 API 必须具有一致的权限检查。

**Test:**
1. Group APIs by resource
2. Compare permission enforcement across APIs in the same group
3. Look for inconsistencies (e.g., GET /users requires permission but GET /users/search does not)

**测试方法：**
1. 按资源对 API 进行分组
2. 比较同一分组内各 API 的权限执行情况
3. 查找不一致之处（例如：GET /users 需要权限，但 GET /users/search 却不需要）

**Violation:** Inconsistent permission enforcement across similar endpoints.

**违规判定：** 相似端点之间的权限执行不一致。

**Severity:** Medium

**严重程度：** 中等（Medium）

---

### API-006: Bulk/Batch Endpoint Permission / API-006：批量端点权限

**Rule:** Bulk/batch endpoints must enforce the same permissions as single-item endpoints.

**规则：** 批量端点必须执行与单条记录端点相同的权限校验。

**Test:**
1. Identify batch endpoints (e.g., `POST /users/batch`, `DELETE /users?ids=1,2,3`)
2. Test that the batch endpoint requires the same permission as the single-item endpoint
3. Test that each item in the batch is individually authorized

**测试方法：**
1. 识别批量端点（例如 `POST /users/batch`、`DELETE /users?ids=1,2,3`）
2. 测试批量端点是否要求与单条记录端点相同的权限
3. 测试批次中的每一条记录是否都单独经过授权校验

**Violation:** Batch endpoint bypasses per-item permission checks.

**违规判定：** 批量端点绕过了逐条记录的权限检查。

**Severity:** High

**严重程度：** 高危（High）

---

### API-007: API Version Permission Parity / API-007：API 版本权限对等

**Rule:** All versions of an API must enforce the same permissions.

**规则：** 同一 API 的所有版本都必须执行相同的权限校验。

**Test:**
1. If the API has multiple versions (v1, v2, etc.), test each version
2. Verify that permission checks are consistent across versions

**测试方法：**
1. 如果 API 存在多个版本（v1、v2 等），则逐一测试每个版本
2. 验证各版本之间的权限检查保持一致

**Violation:** Older or newer API version has weaker permission checks.

**违规判定：** 较旧或较新的 API 版本存在较弱的权限检查。

**Severity:** High

**严重程度：** 高危（High）

---

## API Discovery Checklist / API 发现清单

When discovering APIs to test, check:

在发现待测试的 API 时，请检查：

- [ ] Route registration files / 路由注册文件
- [ ] Controller/handler annotations / 控制器/处理器注解
- [ ] OpenAPI/Swagger specifications / OpenAPI/Swagger 规范文档
- [ ] API gateway configuration / API 网关配置
- [ ] Middleware chains / 中间件链
- [ ] GraphQL schema (if applicable) / GraphQL Schema（如适用）
- [ ] gRPC service definitions (if applicable) / gRPC 服务定义（如适用）

Every discovered API must appear in the permission matrix.

每一个被发现的 API 都必须出现在权限矩阵中。
