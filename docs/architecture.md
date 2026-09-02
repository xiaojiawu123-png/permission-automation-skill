# Architecture / 架构

## Overview / 概述

The Permission Automation Testing Skill is structured as a **methodology layer** that sits above any specific technology stack. It defines what to test, how to think about permissions, and how to guide an AI agent through the full testing lifecycle. It does not prescribe how to implement any of it.

权限自动化测试技能被设计为一个位于任何具体技术栈之上的**方法论层**。它定义了应当测试什么、如何思考权限问题，以及如何引导 AI 智能体走完完整的测试生命周期。它并不规定任何具体的实现方式。

```
┌─────────────────────────────────────────────────┐
│                  SKILL.md                        │
│        (Execution Flow: Phase 1-12)             │
├─────────────────────────────────────────────────┤
│                                                   │
│  docs/          Rules & theory behind each phase │
│  rules/         Detailed rules per category      │
│  templates/     Reusable config & code templates │
│  examples/      Concrete demonstration           │
│                                                   │
├─────────────────────────────────────────────────┤
│              Target Project                      │
│   (discovered & adapted to at runtime)           │
└─────────────────────────────────────────────────┘
```

## Design Principles / 设计原则

### 1. Methodology Over Implementation / 方法论优先于实现

The skill defines **what** to do and **why**, not **how** in terms of specific libraries or frameworks. The AI agent discovers the target project's technology stack and adapts accordingly.

本技能定义的是**做什么**以及**为什么这么做**，而不是在具体库或框架层面**怎么做**。AI 智能体会自行发现目标项目的技术栈，并据此做出适配。

### 2. Data-Driven Testing / 数据驱动测试

All test data (users, roles, permissions, matrices) lives in external YAML configuration files. Test code reads these files at runtime. Nothing is hardcoded.

所有测试数据（用户、角色、权限、权限矩阵）都存放在外部的 YAML 配置文件中。测试代码在运行时读取这些文件，不做任何硬编码。

### 3. Reuse-First Integration / 复用优先的集成

Before creating any utility (HTTP client, auth helper, test fixture), the AI must check if the target project already has one. Existing infrastructure is always reused.

在创建任何工具（HTTP 客户端、认证辅助模块、测试夹具）之前，AI 必须先检查目标项目是否已具备相应能力。已有的基础设施始终优先复用。

### 4. Non-Interference / 非侵入性

The skill never modifies business logic, existing tests, API definitions, or permission configurations. It only adds new test files and configuration.

本技能绝不会修改业务逻辑、既有测试、API 定义或权限配置，只会新增测试文件和配置文件。

### 5. Decoupling / 解耦

The skill definition (SKILL.md, docs/, rules/) is completely independent from any example or demo. Examples demonstrate the skill but are not referenced by the skill itself.

技能定义（SKILL.md、docs/、rules/）与任何示例或演示完全独立。示例用于演示本技能，但技能自身并不引用这些示例。

## Component Responsibilities / 组件职责

### SKILL.md
The master document. Defines the 12-phase execution flow, core concepts, and invocation interface. This is the entry point for any AI agent using the skill.

主文档。定义了 12 个阶段的执行流程、核心概念以及调用接口。它是任何使用本技能的 AI 智能体的入口。

### docs/
Architectural and strategic documentation that provides deeper context for each aspect of the skill:

架构与策略层面的文档，为技能的各个方面提供更深入的背景说明：
- `architecture.md` — this file / 即本文件
- `permission-model.md` — permission model theory / 权限模型理论
- `test-strategy.md` — testing strategy and coverage / 测试策略与覆盖范围
- `token-strategy.md` — token management approach / 令牌管理方法
- `configuration.md` — configuration file reference / 配置文件参考

### rules/
Detailed rules for each permission testing category. Each rule file defines what to test, what constitutes a vulnerability, and how to classify findings:

针对每个权限测试类别的详细规则。每个规则文件都定义了测试什么、什么构成漏洞，以及如何对发现的问题进行分级：
- `authentication.md` — authentication testing rules / 认证测试规则
- `role.md` — role-based permission rules / 基于角色的权限规则
- `menu.md` — menu/UI permission rules / 菜单/界面权限规则
- `api.md` — API-level permission rules / API 层权限规则
- `data.md` — data-level permission rules / 数据层权限规则
- `privilege-escalation.md` — privilege escalation detection rules / 权限提升检测规则

### templates/
Starter files that users copy and customize for their project:

供用户复制并根据自身项目定制的起始文件：
- `users.yaml` — user account template / 用户账户模板
- `permissions.yaml` — permission definition template / 权限定义模板
- `permission_matrix.yaml` — permission matrix template / 权限矩阵模板
- `permission_test.py` — reference test implementation (Python/pytest) / 参考测试实现（Python/pytest）

### examples/demo-api/
A complete fictional example that demonstrates the skill in action. Uses a made-up "Employee Management API" with three roles.

一个完整的虚构示例，用于演示本技能的实际运用。它使用一个虚构的“员工管理 API”，包含三种角色。

## Layered Architecture / 分层架构

```
Layer 4: Examples           (concrete, project-specific)
第 4 层：示例              （具体的、项目相关的）
Layer 3: Templates          (adaptable starting points)
第 3 层：模板              （可适配的起点）
Layer 2: Rules              (category-specific testing rules)
第 2 层：规则              （按类别划分的测试规则）
Layer 1: Methodology        (SKILL.md - universal execution flow)
第 1 层：方法论            （SKILL.md——通用执行流程）
Layer 0: Target Project     (discovered at runtime)
第 0 层：目标项目          （在运行时被发现）
```

Each layer builds on the one below it. The methodology layer is universal. The rules layer is category-specific but technology-agnostic. Templates provide concrete starting points. Examples show end-to-end usage.

每一层都建立在其下一层之上。方法论层是通用的；规则层按类别划分，但与具体技术无关；模板提供了具体的起点；示例则展示了端到端的完整用法。

## Adaptation Flow / 适配流程

```
1. AI reads SKILL.md                        AI 读取 SKILL.md
2. AI reads relevant docs/ and rules/       AI 读取相关的 docs/ 和 rules/
3. AI scans target project (Layer 0)        AI 扫描目标项目（第 0 层）
4. AI identifies technology stack           AI 识别技术栈
5. AI selects appropriate templates         AI 选择合适的模板
6. AI adapts templates to target project    AI 使模板适配目标项目
7. AI generates test data files             AI 生成测试数据文件
8. AI generates test code                   AI 生成测试代码
9. AI executes and reports                  AI 执行测试并生成报告
```

## Extensibility Points / 可扩展点

| Extension Point<br>扩展点 | How to Extend<br>扩展方式 |
|---|---|
| New permission model<br>新的权限模型 | Add rules in `rules/`, extend Phase 4<br>在 `rules/` 中新增规则，扩展第 4 阶段 |
| New test category<br>新的测试类别 | Add rules, extend Phase 8<br>新增规则，扩展第 8 阶段 |
| New technology stack<br>新的技术栈 | Add templates in `templates/`<br>在 `templates/` 中新增模板 |
| New report format<br>新的报告格式 | Extend Phase 12 output structure<br>扩展第 12 阶段的输出结构 |
| CI/CD integration<br>CI/CD 集成 | Generated tests run in any pipeline<br>生成的测试可在任意流水线中运行 |
