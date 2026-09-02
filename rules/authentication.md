# Authentication Testing Rules / 认证测试规则

## Purpose / 目的

Define what to test for authentication security and how to classify findings.

定义认证安全测试的内容以及如何对发现的问题进行分类。

## Scope / 范围

Authentication testing verifies that the system correctly:
- Requires authentication for protected resources
- Validates token/credential authenticity
- Rejects expired, malformed, or revoked credentials
- Does not leak authentication details in error messages

认证测试验证系统能够正确地：
- 对受保护资源强制要求身份认证
- 校验令牌/凭证的真实性
- 拒绝已过期、格式错误或已吊销的凭证
- 不在错误消息中泄露认证细节

## Test Rules / 测试规则

### AUTH-001: Missing Authentication / AUTH-001：缺失身份认证

**Rule:** Every protected API must reject requests without any authentication credential.

**规则：** 每个受保护的 API 都必须拒绝不带任何认证凭证的请求。

**Test:**
1. Identify all protected APIs
2. For each API, send a request with no token, no cookie, no credential
3. Expected: 401 or 403 response

**测试方法：**
1. 识别所有受保护的 API
2. 对每个 API，发送不带令牌、不带 Cookie、不带任何凭证的请求
3. 预期结果：返回 401 或 403 响应

**Violation:** API returns 200 or returns data without authentication.

**违规判定：** API 在未认证的情况下返回 200 或直接返回数据。

**Severity:** Critical

**严重程度：** 严重（Critical）

---

### AUTH-002: Malformed Token / AUTH-002：格式错误的令牌

**Rule:** The system must reject requests with invalid token format.

**规则：** 系统必须拒绝令牌格式无效的请求。

**Test:**
1. Send requests with various malformed tokens:
   - Empty string
   - Random characters
   - Truncated valid token
   - Token with modified signature (for JWT)
   - Token from a different algorithm (e.g., `alg: none` for JWT)
2. Expected: 401 response for all

**测试方法：**
1. 使用各种格式错误的令牌发送请求：
   - 空字符串
   - 随机字符
   - 截断的有效令牌
   - 签名被篡改的令牌（针对 JWT）
   - 使用不同算法的令牌（例如 JWT 的 `alg: none`）
2. 预期结果：所有请求均返回 401 响应

**Violation:** System accepts a malformed token or returns 500 (information leak).

**违规判定：** 系统接受了格式错误的令牌，或返回 500 错误（信息泄露）。

**Severity:** Critical (if accepted), Medium (if 500 error)

**严重程度：** 严重（Critical，若令牌被接受）；中等（Medium，若返回 500 错误）

---

### AUTH-003: Expired Token / AUTH-003：过期令牌

**Rule:** The system must reject expired tokens.

**规则：** 系统必须拒绝已过期的令牌。

**Test:**
1. Obtain a token
2. Wait for it to expire, or use a pre-expired token
3. Send a request with the expired token
4. Expected: 401 response

**测试方法：**
1. 获取一个令牌
2. 等待其过期，或使用预先准备好的过期令牌
3. 使用过期令牌发送请求
4. 预期结果：返回 401 响应

**Violation:** System accepts an expired token.

**违规判定：** 系统接受了过期令牌。

**Severity:** High

**严重程度：** 高危（High）

---

### AUTH-004: Revoked Token / AUTH-004：已吊销令牌

**Rule:** The system must reject tokens for deactivated or locked users.

**规则：** 系统必须拒绝已停用或已锁定用户的令牌。

**Test:**
1. Obtain a token for a user
2. Deactivate or lock the user account (or use a pre-deactivated test account)
3. Send a request with the token
4. Expected: 401 response

**测试方法：**
1. 获取某个用户的令牌
2. 停用或锁定该用户账户（或使用预先停用的测试账户）
3. 使用该令牌发送请求
4. 预期结果：返回 401 响应

**Violation:** System accepts a token for a deactivated user.

**违规判定：** 系统接受了已停用用户的令牌。

**Severity:** High

**严重程度：** 高危（High）

---

### AUTH-005: Token Scope / AUTH-005：令牌作用域

**Rule:** Tokens must be scoped to the correct environment and system.

**规则：** 令牌必须限定在正确的环境和系统范围内有效。

**Test:**
1. Obtain a token from environment A (e.g., staging)
2. Use it to access environment B (e.g., production)
3. Expected: 401 response

**测试方法：**
1. 从环境 A（如预发布环境）获取一个令牌
2. 使用该令牌访问环境 B（如生产环境）
3. 预期结果：返回 401 响应

**Violation:** Token from one environment works in another.

**违规判定：** 某一环境的令牌在另一环境中仍然有效。

**Severity:** High

**严重程度：** 高危（High）

---

### AUTH-006: Error Message Information Leak / AUTH-006：错误消息信息泄露

**Rule:** Authentication error responses must not reveal internal details.

**规则：** 认证错误响应不得泄露内部实现细节。

**Test:**
1. Send requests with various invalid tokens
2. Examine error messages for:
   - Stack traces
   - Internal system names
   - Token structure details
   - Database or service names
3. Expected: Generic error message ("Invalid credentials" or "Unauthorized")

**测试方法：**
1. 使用各种无效令牌发送请求
2. 检查错误消息中是否包含：
   - 堆栈跟踪信息
   - 内部系统名称
   - 令牌结构细节
   - 数据库或服务名称
3. 预期结果：返回通用错误消息（如 "Invalid credentials" 或 "Unauthorized"）

**Violation:** Error message reveals internal implementation details.

**违规判定：** 错误消息暴露了内部实现细节。

**Severity:** Low

**严重程度：** 低危（Low）

---

## Classification Guide / 分类指南

| Response Code / 响应码 | Interpretation / 判定说明 |
|---|---|
| 401 | Correctly rejected (test passes) / 已正确拒绝（测试通过） |
| 403 | Authenticated but not authorized (may indicate token was accepted without proper validation) / 已认证但未授权（可能表明令牌未经充分校验即被接受） |
| 200 | Authentication bypass (Critical vulnerability) / 认证绕过（严重漏洞） |
| 500 | Server error (potential information leak) / 服务器错误（可能存在信息泄露） |
| 302 redirect / 302 重定向 | May redirect to login page; check if API still processes the request / 可能重定向到登录页；需检查 API 是否仍处理了该请求 |
