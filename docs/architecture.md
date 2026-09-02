# Architecture

## Overview

The Permission Automation Testing Skill is structured as a **methodology layer** that sits above any specific technology stack. It defines what to test, how to think about permissions, and how to guide an AI agent through the full testing lifecycle. It does not prescribe how to implement any of it.

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

## Design Principles

### 1. Methodology Over Implementation

The skill defines **what** to do and **why**, not **how** in terms of specific libraries or frameworks. The AI agent discovers the target project's technology stack and adapts accordingly.

### 2. Data-Driven Testing

All test data (users, roles, permissions, matrices) lives in external YAML configuration files. Test code reads these files at runtime. Nothing is hardcoded.

### 3. Reuse-First Integration

Before creating any utility (HTTP client, auth helper, test fixture), the AI must check if the target project already has one. Existing infrastructure is always reused.

### 4. Non-Interference

The skill never modifies business logic, existing tests, API definitions, or permission configurations. It only adds new test files and configuration.

### 5. Decoupling

The skill definition (SKILL.md, docs/, rules/) is completely independent from any example or demo. Examples demonstrate the skill but are not referenced by the skill itself.

## Component Responsibilities

### SKILL.md
The master document. Defines the 12-phase execution flow, core concepts, and invocation interface. This is the entry point for any AI agent using the skill.

### docs/
Architectural and strategic documentation that provides deeper context for each aspect of the skill:
- `architecture.md` — this file
- `permission-model.md` — permission model theory
- `test-strategy.md` — testing strategy and coverage
- `token-strategy.md` — token management approach
- `configuration.md` — configuration file reference

### rules/
Detailed rules for each permission testing category. Each rule file defines what to test, what constitutes a vulnerability, and how to classify findings:
- `authentication.md` — authentication testing rules
- `role.md` — role-based permission rules
- `menu.md` — menu/UI permission rules
- `api.md` — API-level permission rules
- `data.md` — data-level permission rules
- `privilege-escalation.md` — privilege escalation detection rules

### templates/
Starter files that users copy and customize for their project:
- `users.yaml` — user account template
- `permissions.yaml` — permission definition template
- `permission_matrix.yaml` — permission matrix template
- `permission_test.py` — reference test implementation (Python/pytest)

### examples/demo-api/
A complete fictional example that demonstrates the skill in action. Uses a made-up "Employee Management API" with three roles.

## Layered Architecture

```
Layer 4: Examples           (concrete, project-specific)
Layer 3: Templates          (adaptable starting points)
Layer 2: Rules              (category-specific testing rules)
Layer 1: Methodology        (SKILL.md - universal execution flow)
Layer 0: Target Project     (discovered at runtime)
```

Each layer builds on the one below it. The methodology layer is universal. The rules layer is category-specific but technology-agnostic. Templates provide concrete starting points. Examples show end-to-end usage.

## Adaptation Flow

```
1. AI reads SKILL.md
2. AI reads relevant docs/ and rules/
3. AI scans target project (Layer 0)
4. AI identifies technology stack
5. AI selects appropriate templates
6. AI adapts templates to target project
7. AI generates test data files
8. AI generates test code
9. AI executes and reports
```

## Extensibility Points

| Extension Point | How to Extend |
|---|---|
| New permission model | Add rules in `rules/`, extend Phase 4 |
| New test category | Add rules, extend Phase 8 |
| New technology stack | Add templates in `templates/` |
| New report format | Extend Phase 12 output structure |
| CI/CD integration | Generated tests run in any pipeline |
