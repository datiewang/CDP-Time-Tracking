# Microsoft Entra ID (Azure AD) 应用注册指南

为了使用 Microsoft Graph API 抓取您的 Outlook 日历日程，您需要在 Microsoft Azure 门户中注册一个应用程序。注册完成后，您将获得 `client_id` (应用程序ID) 和 `tenant_id` (目录ID)。

以下是详细的操作步骤：

---

## 第一步：登录 Azure 门户并新建注册

1. 使用您的工作邮箱或微软管理员账号登录 [Azure Portal (微软云门户)](https://portal.azure.com/)。
2. 在顶部搜索栏输入 **Microsoft Entra ID**（原名 Azure Active Directory）并点击进入。
3. 在左侧菜单栏中，找到并点击 **应用注册** (App registrations)。
4. 点击顶部的 **+ 新注册** (New registration) 按钮。

---

## 第二步：填写注册表单

在“注册应用程序”页面中，按照以下设置填写：

1. **名称**：起一个好记的名字，例如 `OutlookCalendarTimeTracker`。
2. **支持的账户类型**：
   * **推荐选择**：`仅此组织目录中的账户 (仅特定租户 - 单租户)` (Accounts in this organizational directory only) —— 适用于仅在贵公司内部邮箱账号之间使用。
3. **重定向 URI（可选）**：
   * 在下拉菜单中选择 **公共客户端/本机(移动和桌面)** (Public client/native (mobile & desktop))。
   * 在右侧文本框中输入：`http://localhost` （**必须精确匹配**，Python 脚本在本地运行登录时需要用到此地址）。
4. 点击页面底部的 **注册** (Register) 按钮。

---

## 第三步：获取 `client_id` 和 `tenant_id`

注册成功后，页面会自动跳转到该应用的“概述” (Overview) 页面。在此页面中：

* 复制 **应用程序(客户端) ID** (Application (client) ID) —— 这就是您需要填入 `graph_config.json` 的 **`client_id`**。
* 复制 **目录(租户) ID** (Directory (tenant) ID) —— 这就是您需要填入 `graph_config.json` 的 **`tenant_id`**。

---

## 第四步：配置 API 权限

注册完后，必须为应用配置读取日历的权限，否则接口会报错（Access Denied）：

1. 在左侧菜单栏中，点击 **API 权限** (API permissions)。
2. 点击 **+ 添加权限** (Add a permission) 按钮。
3. 在弹出的侧边栏中选择 **Microsoft Graph**。
4. 选择 **委托的权限** (Delegated permissions)。
5. 在搜索框中搜索并勾选以下两项权限：
   * **`Calendars.Read`** (读取用户本人的日历)
   * **`Calendars.Read.Shared`** (读取他人共享给您的日历)
6. 点击底部的 **添加权限** (Add permissions) 按钮。

### 管理员同意（可选但推荐）
* 如果您是公司的 Office 365 / Entra ID 管理员，可以直接点击“API 权限”页面上的 **代表 <您的公司名称> 授予管理员同意** (Grant admin consent for <Company>)。
* 授予同意后，运行脚本时用户就**不会**再看到“请求权限”的同意确认弹窗，体验更加顺畅。
