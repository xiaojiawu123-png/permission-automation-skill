# Menu Permission Testing Rules

## Purpose

Define what to test for UI/menu-level access control and how to classify findings.

## Scope

Menu permission testing verifies that:
- Users only see menu items they are authorized to access
- Menu visibility matches API-level permissions
- Hidden menu items do not expose underlying APIs

## Test Rules

### MENU-001: Menu Visibility

**Rule:** Users must only see menu items corresponding to their permissions.

**Test:**
1. For each role, identify which menus should be visible
2. Query the menu/permission API for that role
3. Verify that only authorized menus are returned
4. Expected: Menu list matches role permissions exactly

**Violation:** Menu list includes items the role should not see.

**Severity:** Low (if API is still protected), High (if menu exposure indicates API exposure)

---

### MENU-002: Menu-API Consistency

**Rule:** If a menu item is hidden, the corresponding API must also be protected.

**Test:**
1. Identify menu items that should be hidden for a role
2. For each hidden menu item, identify the corresponding API
3. Call the API directly as a user with that role
4. Expected: 403 Forbidden

**Violation:** Menu is hidden but API is accessible (frontend-only protection).

**Severity:** Critical

---

### MENU-003: Direct URL Access

**Rule:** Users must not be able to access pages by direct URL if they lack the menu permission.

**Test:**
1. Identify page URLs for menus the role should not access
2. Navigate directly to the URL (or call the page's data API)
3. Expected: Redirect to authorized page, or 403, or empty content

**Violation:** User can access the page by direct URL despite lacking menu permission.

**Severity:** High

---

### MENU-004: Button/Action Visibility

**Rule:** Action buttons (create, edit, delete, export) must only be visible to roles with the corresponding permission.

**Test:**
1. For each role, query the permission API for button-level permissions
2. Verify that action buttons match the role's operation permissions
3. For hidden buttons, verify the corresponding API is also protected

**Violation:** Button is hidden but API is accessible, or button is visible without permission.

**Severity:** High (if API accessible), Medium (if button visible but API protected)

---

## Important Note

Menu permission testing often requires UI-level testing (browser automation). However, the API-level verification (MENU-002) can and should be done through API testing alone. The critical check is: **does hiding the menu actually protect the API?**

If the project has a menu/permission query API (e.g., `GET /user/menus` or `GET /user/permissions`), use it for automated testing. Otherwise, document the expected menu structure for manual verification.
