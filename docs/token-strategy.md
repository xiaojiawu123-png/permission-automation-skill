# Token Strategy / 令牌策略

## Overview / 概述

Token management is a critical part of permission testing. Tests need valid credentials for multiple roles, tokens must be reused efficiently, and the mechanism for obtaining tokens varies by project.

令牌管理是权限测试中的关键环节。测试需要多个角色的有效凭证，令牌必须被高效复用，而获取令牌的机制又因项目而异。

This document defines the abstract token management strategy that the skill follows, regardless of the target project's specific authentication protocol.

本文定义了本技能所遵循的抽象令牌管理策略，与目标项目具体的认证协议无关。

## Abstract Token Flow / 抽象令牌流程

```
┌──────────┐     ┌──────────────────┐     ┌──────────┐
│  User    │────>│  Authentication  │────>│  Token   │
│ Identity │     │  Mechanism       │     │ Artifact │
└──────────┘     └──────────────────┘     └────┬─────┘
                                                │
                    ┌──────────────────┐        │
                    │  Request         │<───────┘
                    │  Injection       │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Permission      │
                    │  Test Execution  │
                    └──────────────────┘
```

## Discovery Process / 发现流程

The AI must discover the target project's token mechanism before generating any test code. The discovery follows this priority:

在生成任何测试代码之前，AI 必须先弄清目标项目的令牌机制。发现过程遵循以下优先级：

### Priority 1: Existing Token Infrastructure / 优先级 1：已有的令牌基础设施
Check if the project already has:

检查项目是否已具备：
- Login functions or auth utilities / 登录函数或认证工具类
- Token management classes or modules / 令牌管理类或模块
- Test fixtures that handle authentication / 处理认证的测试夹具
- Environment variables with test credentials / 存放测试凭证的环境变量

If found, **reuse them**.

如果找到，就**复用它们**。

### Priority 2: Login API / 优先级 2：登录 API
Search for authentication endpoints:

查找认证端点：
- `POST /login`, `POST /auth`, `POST /oauth/token`
- Login controllers or handlers / 登录控制器或处理器
- Auth middleware configuration / 认证中间件配置

If found, use the login API to obtain tokens for each role.

如果找到，就使用登录 API 为每个角色获取令牌。

### Priority 3: Configuration-Based Tokens / 优先级 3：基于配置的令牌
Check if tokens are provided through:

检查令牌是否通过以下方式提供：
- Environment variables / 环境变量
- Configuration files / 配置文件
- Test fixture data / 测试夹具数据

If found, load tokens from configuration.

如果找到，就从配置中加载令牌。

### Priority 4: Manual Token Generation / 优先级 4：手动生成令牌
If no automated method exists, document the manual process and ask the user to provide tokens for each role.

如果不存在任何自动化方式，则记录手动流程，并请用户为每个角色提供令牌。

## Token Lifecycle / 令牌生命周期

### Acquisition / 获取
```
For each role in the test suite:              对于测试套件中的每个角色：
    1. Authenticate as a user with that role      1. 以拥有该角色的用户身份进行认证
    2. Extract the token from the response        2. 从响应中提取令牌
    3. Store the token in a role-keyed cache      3. 将令牌存入以角色为键的缓存中
```

### Caching / 缓存
```
Token Cache:
    admin:    { token: "...", expires_at: ..., header: "..." }
    manager:  { token: "...", expires_at: ..., header: "..." }
    employee: { token: "...", expires_at: ..., header: "..." }
```

Tokens are cached for the duration of the test session. This avoids redundant login calls and keeps tests fast.

令牌会在整个测试会话期间被缓存。这样可以避免重复的登录调用，保持测试快速运行。

### Refresh / 刷新
Before each request, check if the cached token is still valid:

在每次请求之前，检查缓存的令牌是否仍然有效：
- If the token has an expiration time, check it / 如果令牌带有过期时间，就检查它
- If a request returns 401, attempt to refresh the token / 如果某次请求返回 401，则尝试刷新令牌
- If refresh fails, re-authenticate from scratch / 如果刷新失败，则从头重新认证

### Cleanup / 清理
After the test session:

在测试会话结束之后：
- Clear cached tokens from memory / 从内存中清除缓存的令牌
- If tokens were created specifically for testing, invalidate them / 如果令牌是专为测试而创建的，则将其作废

## Token Transport / 令牌传输方式

Different projects use different mechanisms to pass tokens in requests:

不同项目使用不同的机制在请求中传递令牌：

| Transport<br>传输方式 | Example<br>示例 | Where to Check<br>适用场景 |
|---|---|---|
| Authorization Header<br>Authorization 请求头 | `Authorization: Bearer <token>` | Most common for JWT/OAuth<br>最常见于 JWT/OAuth |
| Custom Header<br>自定义请求头 | `X-Auth-Token: <token>` | Custom auth implementations<br>自定义认证实现 |
| Cookie<br>Cookie | `Cookie: session=<token>` | Session-based auth<br>基于会话的认证 |
| Query Parameter<br>查询参数 | `?token=<token>` | Less common, less secure<br>较少见，且安全性较低 |

The AI must discover which transport the project uses and generate test code accordingly.

AI 必须弄清项目使用的是哪种传输方式，并据此生成测试代码。

## Multi-Role Token Management / 多角色令牌管理

Permission testing requires tokens for multiple roles simultaneously. The token manager must:

权限测试需要同时持有多个角色的令牌。令牌管理器必须：

1. **Maintain separate tokens per role** — never mix tokens between roles / **为每个角色维护各自独立的令牌**——绝不在角色之间混用令牌
2. **Support role switching** — tests can specify which role's token to use / **支持角色切换**——测试可以指定使用哪个角色的令牌
3. **Handle token dependencies** — some tests may need to create data as one role, then access it as another / **处理令牌依赖关系**——某些测试可能需要先以一个角色创建数据，再以另一个角色访问它

### Role Token Pattern / 角色令牌模式
```
# Abstract representation / 抽象表示
role_tokens:
    admin:
        user: admin_user
        token: <acquired_at_runtime>
        transport: header
        header_name: Authorization
        header_prefix: Bearer

    manager:
        user: manager_user
        token: <acquired_at_runtime>
        transport: header
        header_name: Authorization
        header_prefix: Bearer

    employee:
        user: employee_user
        token: <acquired_at_runtime>
        transport: header
        header_name: Authorization
        header_prefix: Bearer
```

## Error Handling / 错误处理

| Scenario<br>场景 | Action<br>处理方式 |
|---|---|
| Login returns 401<br>登录返回 401 | Check credentials in users.yaml<br>检查 users.yaml 中的凭证 |
| Login returns 403<br>登录返回 403 | User account may be locked<br>用户账户可能已被锁定 |
| Login returns 500<br>登录返回 500 | Auth service may be down<br>认证服务可能已宕机 |
| Token returns 401 on use<br>使用令牌时返回 401 | Token may be expired; refresh<br>令牌可能已过期；进行刷新 |
| Token returns 403 on use<br>使用令牌时返回 403 | This may be the permission being tested<br>这可能正是被测的权限点 |
| Refresh fails<br>刷新失败 | Re-authenticate from scratch<br>从头重新认证 |
| All auth fails<br>所有认证均失败 | Stop tests; report authentication failure<br>停止测试；报告认证失败 |

## Security Considerations / 安全注意事项

1. **Never log tokens** — tokens are secrets; redact them from logs and reports / **绝不记录令牌**——令牌属于机密信息；应从日志和报告中将其脱敏
2. **Never hardcode tokens** — always obtain at runtime or load from secure config / **绝不硬编码令牌**——始终在运行时获取，或从安全的配置中加载
3. **Use test accounts** — never use production credentials for testing / **使用测试账户**——绝不用生产环境凭证进行测试
4. **Isolate test tokens** — tokens created for testing should not have access to production data / **隔离测试令牌**——为测试创建的令牌不应有权访问生产数据
5. **Clean up** — invalidate test tokens after the test session / **及时清理**——在测试会话结束后作废测试令牌
