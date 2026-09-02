# Changelog / 变更日志

All notable changes to this project will be documented in this file.

本项目的所有重要变更将记录在此文件中。

---

## [1.0.0] - 2026-09-02

### Added / 新增

- Formal Skill specification with version, scope, inputs/outputs, and constraints / 正式的技能规范，包含版本、范围、输入/输出和约束
- `CHANGELOG.md` for version tracking / 版本跟踪变更日志
- User-indexed token management (`get_token(user="alice")`) / 按用户名索引的令牌管理
- `name` field requirement for all users in `users.yaml` / `users.yaml` 中所有用户的 `name` 字段要求
- `test_data` section in `users.yaml` for parameterized resource references / `users.yaml` 中的 `test_data` 部分用于参数化资源引用
- Clear separation between `permissions.yaml` (system permission model) and `permission_matrix.yaml` (test scenario matrix) / 明确分离 `permissions.yaml`（系统权限模型）和 `permission_matrix.yaml`（测试场景矩阵）

### Changed / 变更

- **SKILL.md** rewritten as formal Skill specification with v1.0.0 metadata / SKILL.md 重写为正式技能规范
- **README.md** rewritten as open-source project README with prerequisites / README.md 重写为开源项目 README
- **TokenManager** changed from role-indexed to user-indexed token acquisition / TokenManager 从按角色索引改为按用户名索引
- **PermissionTestClient** unified: uses `user` parameter instead of `role` / PermissionTestClient 统一：使用 `user` 参数替代 `role`
- **Bearer handling** fixed: no more double-prefix (`Bearer Bearer xxx`) / Bearer 处理修复：不再重复前缀
- **Demo test code** removed all hardcoded IDs — reads from YAML `test_data` / 示例测试代码移除所有硬编码 ID——从 YAML `test_data` 读取
- **Template and Demo** unified to same architecture, naming, and patterns / 模板和示例统一为相同架构、命名和模式
- Demo README clarified: fictional example, requires real target API to run / 示例 README 明确说明：虚构示例，需要真实目标 API 才能运行

### Fixed / 修复

- Bearer token double-prefix bug when using `token_override` / 使用 `token_override` 时的 Bearer 令牌双重前缀问题
- Role-indexed token manager couldn't distinguish multiple users with same role / 按角色索引的令牌管理器无法区分同一角色的多个用户
- Hardcoded employee IDs in demo test code / 示例测试代码中的硬编码员工 ID

---

## [0.1.0] - 2026-09-01

### Added / 新增

- Initial skill structure with 12-phase execution flow / 初始技能结构，12阶段执行流程
- Bilingual documentation (English + Chinese) / 双语文档（英文 + 中文）
- `docs/` directory with 5 strategy documents / `docs/` 目录，5个策略文档
- `rules/` directory with 6 testing rule files / `rules/` 目录，6个测试规则文件
- `templates/` directory with reference implementations / `templates/` 目录，参考实现
- `examples/demo-api/` with fictional Employee Management API example / `examples/demo-api/` 虚构员工管理 API 示例
- MIT License / MIT 许可证
