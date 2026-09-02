# Demo: Employee Management API / 示例：员工管理API

> A completely fictional API used to demonstrate the Permission Automation Testing Skill.
> **This is not a real system. All names, data, and endpoints are fabricated.**
>
> 一个完全虚构的 API，用于演示「权限自动化测试技能」（Permission Automation Testing Skill）。
> **这不是真实系统。所有名称、数据与接口端点均为虚构。**

## Overview / 概述

The Employee Management API is a simple REST API for managing employee records. It has three roles with different permission levels and data scopes.

员工管理API 是一个用于管理员工档案的简单 REST API。它包含三种角色，各自拥有不同的权限级别与数据范围。

## Fictional API Endpoints / 虚构的 API 接口

| Method / 方法 | Path / 路径 | Description / 描述 |
|---|---|---|
| POST | `/api/auth/login` | Authenticate and obtain a JWT token<br>身份认证并获取 JWT 令牌 |
| GET | `/api/employees` | List employees<br>查询员工列表 |
| GET | `/api/employees/{id}` | Get a specific employee<br>查询指定员工 |
| POST | `/api/employees` | Create a new employee<br>新建员工 |
| PUT | `/api/employees/{id}` | Update an employee<br>更新员工信息 |
| DELETE | `/api/employees/{id}` | Delete an employee<br>删除员工 |
| POST | `/api/employees/batch` | Batch query employees by IDs<br>按员工ID批量查询 |
| GET | `/api/departments/{id}/employees` | List employees in a department<br>查询指定部门下的员工列表 |

## Roles / 角色

| Role / 角色 | Level / 级别 | Description / 描述 |
|---|---|---|
| `admin` | Highest / 最高 | Full access to all employees and all operations<br>管理员，可访问全部员工数据并执行所有操作 |
| `manager` | Medium / 中等 | Can query, create, update employees in own department; cannot delete<br>部门经理，可查询、新建、更新本部门员工，不可删除 |
| `employee` | Lowest / 最低 | Can only view and update own record<br>普通员工，仅可查看和更新本人档案 |

## Permission Matrix / 权限矩阵

| Permission / 权限 | admin<br>管理员 | manager<br>部门经理 | employee<br>普通员工 |
|---|---|---|---|
| `employee.query` | Yes / 有 | Yes (dept scope) / 有（限本部门） | No / 无 |
| `employee.create` | Yes / 有 | Yes (dept scope) / 有（限本部门） | No / 无 |
| `employee.update` | Yes / 有 | Yes (dept scope) / 有（限本部门） | No / 无 |
| `employee.delete` | Yes / 有 | No / 无 | No / 无 |
| `employee.self.query` | Yes / 有 | Yes / 有 | Yes / 有 |
| `employee.self.update` | Yes / 有 | Yes / 有 | Yes / 有 |

## Data Scope / 数据范围

| Role / 角色 | Scope / 范围 | Meaning / 含义 |
|---|---|---|
| `admin` | All / 全部 | Can access all employee records<br>可访问所有员工档案 |
| `manager` | Department / 部门 | Can only access employees in the same department<br>仅可访问同一部门的员工 |
| `employee` | Self / 本人 | Can only access their own record<br>仅可访问本人档案 |

## Fictional Test Users / 虚构的测试用户

| Username / 用户名 | Password / 密码 | Role / 角色 | Department / 部门 | Employee ID / 员工ID |
|---|---|---|---|---|
| `admin_user` | `admin123` | admin / 管理员 | — | — |
| `manager_dept_a` | `manager123` | manager / 部门经理 | Engineering (dept-1) / 工程部（dept-1） | 100 |
| `manager_dept_b` | `manager456` | manager / 部门经理 | Marketing (dept-2) / 市场部（dept-2） | 200 |
| `emp_alice` | `alice123` | employee / 普通员工 | Engineering (dept-1) / 工程部（dept-1） | 101 |
| `emp_bob` | `bob123` | employee / 普通员工 | Engineering (dept-1) / 工程部（dept-1） | 102 |
| `emp_charlie` | `charlie123` | employee / 普通员工 | Marketing (dept-2) / 市场部（dept-2） | 201 |

## Test Scenarios Covered / 覆盖的测试场景

### Authentication / 身份认证

- No token → 401
  未携带令牌 → 401
- Invalid token → 401
  令牌无效 → 401
- Expired token → 401
  令牌已过期 → 401

### Vertical Privilege Escalation / 垂直越权

- `manager` → DELETE /employees/{id} → 403 (admin-only)
  部门经理调用 DELETE /employees/{id} → 403（仅限管理员）
- `employee` → POST /employees → 403 (no create permission)
  普通员工调用 POST /employees → 403（无新建权限）
- `employee` → DELETE /employees/{id} → 403 (no delete permission)
  普通员工调用 DELETE /employees/{id} → 403（无删除权限）

### Horizontal Privilege Escalation / 水平越权

- `emp_alice` → GET /employees/102 (Bob's record) → 403
  `emp_alice` 调用 GET /employees/102（Bob 的档案）→ 403
- `emp_alice` → PUT /employees/102 → 403
  `emp_alice` 调用 PUT /employees/102 → 403

### Data Permission / 数据权限

- `manager_dept_a` → GET /employees/201 (Marketing employee) → 403
  `manager_dept_a` 调用 GET /employees/201（市场部员工）→ 403
- `manager_dept_a` → GET /departments/dept-2/employees → 403
  `manager_dept_a` 调用 GET /departments/dept-2/employees → 403

### Parameter Tampering / 参数篡改

- `employee` sends `PUT /employees/{self_id}` with `departmentId: dept-2` → ignored or 403
  普通员工提交 `PUT /employees/{self_id}` 并携带 `departmentId: dept-2` → 参数被忽略或返回 403
- `employee` sends `POST /employees` with `role: admin` → ignored or 403
  普通员工提交 `POST /employees` 并携带 `role: admin` → 参数被忽略或返回 403

### Batch Authorization / 批量接口鉴权

- `employee` sends `POST /employees/batch` with `[self_id, other_id]` → only self data returned
  普通员工提交 `POST /employees/batch`，请求体为 `[本人ID, 他人ID]` → 仅返回本人数据

## How to Use / 使用方法

1. Copy `users.yaml`, `permissions.yaml`, and `permission_matrix.yaml` as reference
   将 `users.yaml`、`permissions.yaml` 与 `permission_matrix.yaml` 复制出来作为参考模板
2. Adapt them to your actual project's users, roles, and permissions
   根据你实际项目的用户、角色与权限对模板进行改写
3. Use `tests/test_permission.py` as a reference for test code structure
   以 `tests/test_permission.py` 作为测试代码结构的参考
4. The AI agent should generate similar tests based on your project's configuration
   AI 智能体应基于你项目的配置生成同类的权限测试用例

## Important / 重要说明

This demo is **completely fictional**. It does not connect to any real system. It exists solely to demonstrate how the Permission Automation Testing Skill works.

本示例**完全虚构**，不会连接任何真实系统，仅用于演示「权限自动化测试技能」的工作方式。
