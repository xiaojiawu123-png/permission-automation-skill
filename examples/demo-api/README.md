# Demo: Employee Management API

> A completely fictional API used to demonstrate the Permission Automation Testing Skill.
> **This is not a real system. All names, data, and endpoints are fabricated.**

## Overview

The Employee Management API is a simple REST API for managing employee records. It has three roles with different permission levels and data scopes.

## Fictional API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/login` | Authenticate and obtain a JWT token |
| GET | `/api/employees` | List employees |
| GET | `/api/employees/{id}` | Get a specific employee |
| POST | `/api/employees` | Create a new employee |
| PUT | `/api/employees/{id}` | Update an employee |
| DELETE | `/api/employees/{id}` | Delete an employee |
| POST | `/api/employees/batch` | Batch query employees by IDs |
| GET | `/api/departments/{id}/employees` | List employees in a department |

## Roles

| Role | Level | Description |
|---|---|---|
| `admin` | Highest | Full access to all employees and all operations |
| `manager` | Medium | Can query, create, update employees in own department; cannot delete |
| `employee` | Lowest | Can only view and update own record |

## Permission Matrix

| Permission | admin | manager | employee |
|---|---|---|---|
| `employee.query` | Yes | Yes (dept scope) | No |
| `employee.create` | Yes | Yes (dept scope) | No |
| `employee.update` | Yes | Yes (dept scope) | No |
| `employee.delete` | Yes | No | No |
| `employee.self.query` | Yes | Yes | Yes |
| `employee.self.update` | Yes | Yes | Yes |

## Data Scope

| Role | Scope | Meaning |
|---|---|---|
| `admin` | All | Can access all employee records |
| `manager` | Department | Can only access employees in the same department |
| `employee` | Self | Can only access their own record |

## Fictional Test Users

| Username | Password | Role | Department | Employee ID |
|---|---|---|---|---|
| `admin_user` | `admin123` | admin | — | — |
| `manager_dept_a` | `manager123` | manager | Engineering (dept-1) | 100 |
| `manager_dept_b` | `manager456` | manager | Marketing (dept-2) | 200 |
| `emp_alice` | `alice123` | employee | Engineering (dept-1) | 101 |
| `emp_bob` | `bob123` | employee | Engineering (dept-1) | 102 |
| `emp_charlie` | `charlie123` | employee | Marketing (dept-2) | 201 |

## Test Scenarios Covered

### Authentication
- No token → 401
- Invalid token → 401
- Expired token → 401

### Vertical Privilege Escalation
- `manager` → DELETE /employees/{id} → 403 (admin-only)
- `employee` → POST /employees → 403 (no create permission)
- `employee` → DELETE /employees/{id} → 403 (no delete permission)

### Horizontal Privilege Escalation
- `emp_alice` → GET /employees/102 (Bob's record) → 403
- `emp_alice` → PUT /employees/102 → 403

### Data Permission
- `manager_dept_a` → GET /employees/201 (Marketing employee) → 403
- `manager_dept_a` → GET /departments/dept-2/employees → 403

### Parameter Tampering
- `employee` sends `PUT /employees/{self_id}` with `departmentId: dept-2` → ignored or 403
- `employee` sends `POST /employees` with `role: admin` → ignored or 403

### Batch Authorization
- `employee` sends `POST /employees/batch` with `[self_id, other_id]` → only self data returned

## How to Use

1. Copy `users.yaml`, `permissions.yaml`, and `permission_matrix.yaml` as reference
2. Adapt them to your actual project's users, roles, and permissions
3. Use `tests/test_permission.py` as a reference for test code structure
4. The AI agent should generate similar tests based on your project's configuration

## Important

This demo is **completely fictional**. It does not connect to any real system. It exists solely to demonstrate how the Permission Automation Testing Skill works.
