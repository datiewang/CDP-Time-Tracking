# CDP Time Tracking (CDP 项目日历工数统计与自动填报系统)

本项目是一个基于 **Microsoft Graph API** 的日历工数自动拉取与填报系统。能够自动从 Office 365 云端批量获取团队成员的日历日程，根据规则（CDP关键词、跨天判定、终日排除、取消日程扣除）计算工数，并自动将每个人的月度工数填入指定的 Excel 报表模板中，同时为每位开发人员生成明细对账单。

---

## 📂 项目结构

```text
├── run_graph_pipeline.py          # 主运行程序（处理登录、API拉取、数据清洗及分析）
├── fill_template_from_output.py   # Excel 填报逻辑（将汇总工数填入 template.xlsx）
├── export_all_person_md.py        # 个人明细导出逻辑（为每个人生成 Markdown 表格）
├── template.xlsx                  # 填报模板表格（保留原始样式和公式）
├── graph_config.example.json      # 配置文件模板（请复制并重命名为 graph_config.json）
├── azure_registration_guide.md    # 微软 Azure (Entra ID) 应用注册指南
└── README.md                      # 本说明文档
```

---

## 🛠️ 环境要求

* **Python 版本**：Python 3.8 或更高版本
* **所需第三方库**：
  ```bash
  pip install msal requests openpyxl
  ```

---

## 🚀 快速开始

### 第一步：在 Azure 注册应用
请参考 **[azure_registration_guide.md](azure_registration_guide.md)** 指南，在 Microsoft Azure 门户注册一个公共客户端应用，并获得：
1. 应用程序（客户端）ID (`client_id`)
2. 目录（租户）ID (`tenant_id`)

### 第二步：修改配置文件
1. 将根目录下的 `graph_config.example.json` 复制并重命名为 **`graph_config.json`**：
2. 打开并填入您在第一步获取到的凭据：
   ```json
   {
     "client_id": "您的客户端ID",
     "tenant_id": "您的租户ID",
     "start_date": "2025-09-01T00:00:00Z",
     "end_date": "2026-04-01T00:00:00Z",
     "target_emails": [
       "Ryutaro.SUZUKI@okura-nikko.co.jp",
       "..."
     ],
     "timezone": "Tokyo Standard Time",
     "auth_flow": "interactive"
   }
   ```

### 第三步：运行分析程序
在控制台中运行主脚本：
```bash
python run_graph_pipeline.py
```
* **首次运行**：系统会自动拉起浏览器，要求您登录您的 Office 365 账号并进行授权。
* **后续运行**：授权凭证将自动加密保存在本地的 `token_cache.bin` 中，免去重复登录的麻烦。

---

## 📊 输出结果

程序运行成功后，会在 `output/` 文件夹下按当前时间戳生成对应子目录（如 `output/20260629_131646/`），产出以下内容：
1. **`filled_template.xlsx`**：自动填报完成的工数 Excel 报表。
2. **`cdp_time_by_person_month_graph.csv`**：月度工数汇总表。
3. **`cdp_events_detail_graph.csv`**：所有会议日程清洗后的详细清单。
4. **`person_md/`**：包含每位 `/ONHM` 成员独立的 Markdown 会议对账明细表，方便个人核对。
