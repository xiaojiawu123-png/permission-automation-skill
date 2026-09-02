# Authentication Testing Rules

## Purpose

Define what to test for authentication security and how to classify findings.

## Scope

Authentication testing verifies that the system correctly:
- Requires authentication for protected resources
- Validates token/credential authenticity
- Rejects expired, malformed, or revoked credentials
- Does not leak authentication details in error messages

## Test Rules

### AUTH-001: Missing Authentication

**Rule:** Every protected API must reject requests without any authentication credential.

**Test:**
1. Identify all protected APIs
2. For each API, send a request with no token, no cookie, no credential
3. Expected: 401 or 403 response

**Violation:** API returns 200 or returns data without authentication.

**Severity:** Critical

---

### AUTH-002: Malformed Token

**Rule:** The system must reject requests with invalid token format.

**Test:**
1. Send requests with various malformed tokens:
   - Empty string
   - Random characters
   - Truncated valid token
   - Token with modified signature (for JWT)
   - Token from a different algorithm (e.g., `alg: none` for JWT)
2. Expected: 401 response for all

**Violation:** System accepts a malformed token or returns 500 (information leak).

**Severity:** Critical (if accepted), Medium (if 500 error)

---

### AUTH-003: Expired Token

**Rule:** The system must reject expired tokens.

**Test:**
1. Obtain a token
2. Wait for it to expire, or use a pre-expired token
3. Send a request with the expired token
4. Expected: 401 response

**Violation:** System accepts an expired token.

**Severity:** High

---

### AUTH-004: Revoked Token

**Rule:** The system must reject tokens for deactivated or locked users.

**Test:**
1. Obtain a token for a user
2. Deactivate or lock the user account (or use a pre-deactivated test account)
3. Send a request with the token
4. Expected: 401 response

**Violation:** System accepts a token for a deactivated user.

**Severity:** High

---

### AUTH-005: Token Scope

**Rule:** Tokens must be scoped to the correct environment and system.

**Test:**
1. Obtain a token from environment A (e.g., staging)
2. Use it to access environment B (e.g., production)
3. Expected: 401 response

**Violation:** Token from one environment works in another.

**Severity:** High

---

### AUTH-006: Error Message Information Leak

**Rule:** Authentication error responses must not reveal internal details.

**Test:**
1. Send requests with various invalid tokens
2. Examine error messages for:
   - Stack traces
   - Internal system names
   - Token structure details
   - Database or service names
3. Expected: Generic error message ("Invalid credentials" or "Unauthorized")

**Violation:** Error message reveals internal implementation details.

**Severity:** Low

---

## Classification Guide

| Response Code | Interpretation |
|---|---|
| 401 | Correctly rejected (test passes) |
| 403 | Authenticated but not authorized (may indicate token was accepted without proper validation) |
| 200 | Authentication bypass (Critical vulnerability) |
| 500 | Server error (potential information leak) |
| 302 redirect | May redirect to login page; check if API still processes the request |
