# CDP Time Tracking (CDP プロジェクト予定表工数集計・自動入力システム)

本プロジェクトは、**Microsoft Graph API** を使用して、Office 365 クラウドからチームメンバーの予定表データを自動的に取得し、特定のフィルタリングルール（CDP関連キーワード、日またぎ予定の除外、終日イベントの除外、キャンセル予定の控除）に基づいて工数を集計し、指定された Excel テンプレートに自動入力するシステムです。同時に、各メンバーの確認用詳細 Markdown レポートも生成します。

---

## 📂 プロジェクト構成

```text
├── run_graph_pipeline.py          # メイン実行スクリプト（認証、APIデータ取得、フィルタ処理、分析）
├── fill_template_from_output.py   # Excel 入力ロジック（集計結果を template.xlsx に反映）
├── export_all_person_md.py        # 個人用レポート出力ロジック（Markdown テーブルの生成）
├── template.xlsx                  # 入力用 Excel テンプレート（既存フォーマットと数式を維持）
├── graph_config.example.json      # 設定ファイルのテンプレート（コピーして graph_config.json に変更）
├── azure_registration_guide.md    # Microsoft Entra ID アプリケーション登録手順書
└── README.md                      # 本ドキュメント（本ファイル）
```

---

## 🛠️ 必要環境

* **Python バージョン**：Python 3.8 以上
* **必要な外部ライブラリ**：
  ```bash
  pip install msal requests openpyxl
  ```

---

## 🚀 クイックスタート

### ステップ 1: Azure でのアプリ登録
**[azure_registration_guide.md](azure_registration_guide.md)** の手順に従って、Microsoft Azure ポータルでアプリケーションの登録を行い、以下を取得してください：
1. アプリケーション（クライアント）ID (`client_id`)
2. ディレクトリ（テナント）ID (`tenant_id`)

### ステップ 2: 設定ファイルの作成と修正
1. 開発ディレクトリの `graph_config.example.json` をコピーし、**`graph_config.json`** にリネームします。
2. ファイルを開き、ステップ 1 で取得した認証情報を入力します：
   ```json
   {
     "client_id": "取得したクライアントID",
     "tenant_id": "取得したテナントID",
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

### ステップ 3: 集計スクリプトの実行
コンソールでメインスクリプトを実行します：
```bash
python run_graph_pipeline.py
```
* **初回実行時**：ブラウザが自動的に起動し、Microsoft 365 アカウントへのサインインとアクセス許可の同意が求められます。画面の指示に従って完了してください。
* **2回目以降の実行**：トークンがローカルの `token_cache.bin` に暗号化してキャッシュされるため、**サインイン不要で自動実行されます**。

---

## 📊 出力結果

実行が成功すると、`output/` フォルダ配下に現在のタイムスタンプ（例: `output/20260629_131646/`）でフォルダが作成され、以下のファイルが出力されます：
1. **`filled_template.xlsx`**：工数データが自動入力された Excel レポート。
2. **`cdp_time_by_person_month_graph.csv`**：月度工数集計表。
3. **`cdp_events_detail_graph.csv`**：フィルタリング済みの会議/予定詳細リスト。
4. **`person_md/`**：各 `/ONHM` メンバーの個人用 Markdown 明細テーブルが格納されるフォルダ。
