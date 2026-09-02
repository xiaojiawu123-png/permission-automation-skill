# Menu Permission Testing Rules / 菜单权限测试规则

## Purpose / 目的

Define what to test for UI/menu-level access control and how to classify findings.

定义 UI/菜单级访问控制的测试内容以及如何对发现的问题进行分类。

## Scope / 范围

Menu permission testing verifies that:
- Users only see menu items they are authorized to access
- Menu visibility matches API-level permissions
- Hidden menu items do not expose underlying APIs

菜单权限测试验证：
- 用户只能看到其有权访问的菜单项
- 菜单可见性与 API 级权限保持一致
- 隐藏的菜单项不会暴露其底层的 API

## Test Rules / 测试规则

### MENU-001: Menu Visibility / MENU-001：菜单可见性

**Rule:** Users must only see menu items corresponding to their permissions.

**规则：** 用户只能看到与其权限对应的菜单项。

**Test:**
1. For each role, identify which menus should be visible
2. Query the menu/permission API for that role
3. Verify that only authorized menus are returned
4. Expected: Menu list matches role permissions exactly

**测试方法：**
1. 针对每个角色，确定其应当可见的菜单
2. 查询该角色的菜单/权限 API
3. 验证返回的仅为已授权的菜单
4. 预期结果：菜单列表与角色权限完全一致

**Violation:** Menu list includes items the role should not see.

**违规判定：** 菜单列表中包含了该角色不应看到的菜单项。

**Severity:** Low (if API is still protected), High (if menu exposure indicates API exposure)

**严重程度：** 低危（Low，若 API 仍受保护）；高危（High，若菜单暴露意味着 API 也被暴露）

---

### MENU-002: Menu-API Consistency / MENU-002：菜单与 API 一致性

**Rule:** If a menu item is hidden, the corresponding API must also be protected.

**规则：** 如果某个菜单项被隐藏，则其对应的 API 也必须受到保护。

**Test:**
1. Identify menu items that should be hidden for a role
2. For each hidden menu item, identify the corresponding API
3. Call the API directly as a user with that role
4. Expected: 403 Forbidden

**测试方法：**
1. 确定对某个角色应当隐藏的菜单项
2. 针对每个隐藏的菜单项，识别其对应的 API
3. 以该角色的用户身份直接调用该 API
4. 预期结果：返回 403 Forbidden

**Violation:** Menu is hidden but API is accessible (frontend-only protection).

**违规判定：** 菜单已隐藏但 API 仍可访问（仅前端防护）。

**Severity:** Critical

**严重程度：** 严重（Critical）

---

### MENU-003: Direct URL Access / MENU-003：直接 URL 访问

**Rule:** Users must not be able to access pages by direct URL if they lack the menu permission.

**规则：** 如果用户缺少菜单权限，则不得通过直接访问 URL 的方式访问相应页面。

**Test:**
1. Identify page URLs for menus the role should not access
2. Navigate directly to the URL (or call the page's data API)
3. Expected: Redirect to authorized page, or 403, or empty content

**测试方法：**
1. 确定该角色不应访问的菜单对应的页面 URL
2. 直接导航到该 URL（或调用该页面的数据 API）
3. 预期结果：重定向到已授权页面，或返回 403，或返回空内容

**Violation:** User can access the page by direct URL despite lacking menu permission.

**违规判定：** 用户在缺少菜单权限的情况下仍可通过直接 URL 访问页面。

**Severity:** High

**严重程度：** 高危（High）

---

### MENU-004: Button/Action Visibility / MENU-004：按钮/操作可见性

**Rule:** Action buttons (create, edit, delete, export) must only be visible to roles with the corresponding permission.

**规则：** 操作按钮（新增、编辑、删除、导出）只能对拥有相应权限的角色可见。

**Test:**
1. For each role, query the permission API for button-level permissions
2. Verify that action buttons match the role's operation permissions
3. For hidden buttons, verify the corresponding API is also protected

**测试方法：**
1. 针对每个角色，查询权限 API 获取按钮级权限
2. 验证操作按钮与该角色的操作权限相匹配
3. 针对隐藏的按钮，验证其对应的 API 同样受到保护

**Violation:** Button is hidden but API is accessible, or button is visible without permission.

**违规判定：** 按钮已隐藏但 API 仍可访问，或按钮在无权限的情况下仍然可见。

**Severity:** High (if API accessible), Medium (if button visible but API protected)

**严重程度：** 高危（High，若 API 可访问）；中等（Medium，若按钮可见但 API 受保护）

---

## Important Note / 重要说明

Menu permission testing often requires UI-level testing (browser automation). However, the API-level verification (MENU-002) can and should be done through API testing alone. The critical check is: **does hiding the menu actually protect the API?**

菜单权限测试通常需要 UI 级测试（浏览器自动化）。但 API 级验证（MENU-002）可以且应当仅通过 API 测试来完成。关键的检查点是：**隐藏菜单是否真正保护了 API？**

If the project has a menu/permission query API (e.g., `GET /user/menus` or `GET /user/permissions`), use it for automated testing. Otherwise, document the expected menu structure for manual verification.

如果项目中存在菜单/权限查询 API（例如 `GET /user/menus` 或 `GET /user/permissions`），请使用它进行自动化测试。否则，请记录预期的菜单结构以便进行人工验证。
