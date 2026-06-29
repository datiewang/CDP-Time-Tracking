# CDP Time Tracking (CDP プロジェクト予定表工数集計システム)

本プロジェクトは、**Microsoft Graph API** を使用して、Office 365 クラウドからチームメンバーの予定表データを自動的に取得し、特定のフィルタリングルール（CDP関連キーワード、日またぎ予定の除外、終日イベントの除外、キャンセル予定の控除）に基づいて工数を集計し、各メンバーの確認用詳細 Markdown レポートと CSV データを生成するシステムです。

---

## 📂 プロジェクト構成

```text
├── run_graph_pipeline.py          # メイン実行スクリプト（認証、APIデータ取得、フィルタ処理、分析）
├── export_all_person_md.py        # 個人用レポート出力ロジック（Markdown テーブルの生成）
├── graph_config.json              # アプリケーション設定ファイル（認証情報や対象アドレスが設定済み）
├── azure_registration_guide.md    # Microsoft Entra ID アプリケーション登録手順書（参照用）
└── README.md                      # 本ドキュメント（本ファイル）
```

---

## 🛠️ 必要環境

* **Python バージョン**：Python 3.8 以上
* **必要な外部ライブラリ**：
  ```bash
  pip install msal requests
  ```

---

## 🚀 クイックスタート

### ステップ 1: 設定ファイルの確認とシークレットの入力
本リポジトリには、社内共通の認証情報（`client_id` および `tenant_id`）、対象メールアドレスリスト、検索キーワード、および対象ユーザー判定用の末尾文字（`"name_suffix": "/ONHM"`）が設定済みの **`graph_config.json`** があらかじめ含まれています。

**【重要】セキュリティ保護のため、クライアント シークレット（パスワード）はリポジトリにアップロードされていません。** 
[azure_registration_guide.md](azure_registration_guide.md) の手順に従って Azure Portal でクライアント シークレットを**取得**し、`graph_config.json` の `"client_secret"` の項目に**手動で入力**してください。

必要に応じて、集計対象期間 (`"start_date"`, `"end_date"`)、集計対象メールアドレス (`"target_emails"`)、検索キーワード (`"keywords"`)、対象ユーザーの判定末尾文字 (`"name_suffix"`) などの項目を自由に修正可能です。

### ステップ 2: 集計スクリプトの実行
コンソールでメインスクリプトを実行します：
```bash
python run_graph_pipeline.py
```
* **初回実行時**：ブラウザが自動的に起動し、Microsoft 365 アカウントへのサインインとアクセス許可の同意が求められます。画面の指示に従って完了してください。
* **2回目以降の実行**：トークンがローカルの `token_cache.bin` に暗号化してキャッシュされるため、**サインイン不要で自動実行されます**。

---

## 📊 出力結果

実行が成功すると、`output/` フォルダ配下に現在のタイムスタンプ（例: `output/20260629_131646/`）でフォルダが作成され、以下のファイルが出力されます：
1. **`cdp_time_by_person_month_graph.csv`**：月度工数集計表。
2. **`cdp_events_detail_graph.csv`**：フィルタリング済みの会議/予定詳細リスト。
3. **`person_md/`**：各 `/ONHM` メンバーの個人用 Markdown 明細テーブルが格納されるフォルダ。
