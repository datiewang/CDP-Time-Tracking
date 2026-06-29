# Microsoft Entra ID (Azure AD) アプリケーション登録手順書

Microsoft Graph API を使用して Outlook の予定表データを取得するために、Microsoft Azure ポータルでアプリケーションの登録を行う必要があります。登録が完了すると、`client_id` (アプリケーション ID) と `tenant_id` (ディレクトリ ID) が取得できます。

以下に詳細な登録手順を説明します。

---

## ステップ 1: Azure ポータルでの新規登録

1. 組織の Microsoft 365 管理者アカウントまたは作業用アカウントを使用して、[Azure Portal](https://portal.azure.com/) にログインします。
2. 上部の検索バーに **Microsoft Entra ID**（旧称 Azure Active Directory）と入力し、サービスを選択します。
3. 左側のメニューから **アプリの登録** (App registrations) をクリックします。
4. 上部の **+ 新規登録** (New registration) ボタンをクリックします。

---

## ステップ 2: 登録情報の入力

「アプリケーションの登録」ページで、以下の通り設定します：

1. **名前**：分かりやすい名前を入力します（例: `OutlookCalendarTimeTracker`）。
2. **サポートされているアカウントの種類**：
   * **推奨**：`この組織ディレクトリのみに含まれるアカウント (特定組織のみ - シングル テナント)` (Accounts in this organizational directory only) を選択します。
3. **リダイレクト URI (オプション)**：
   * ドロップダウンで **パブリック クライアント/ネイティブ (モバイルとデスクトップ)** (Public client/native (mobile & desktop)) を選択します。
   * 右側のテキストボックスに `http://localhost` と入力します（**完全に一致させる必要があります**。Python スクリプトのログイン処理で使用されます）。
4. ページ下部の **登録** (Register) ボタンをクリックします。

---

## ステップ 3: `client_id` と `tenant_id` の取得

登録が完了すると、アプリケーションの「概要」 (Overview) ページに遷移します。このページから以下の値をコピーします：

* **アプリケーション (クライアント) ID** (Application (client) ID) —— これが `graph_config.json` に設定する **`client_id`** になります。
* **ディレクトリ (テナント) ID** (Directory (tenant) ID) —— これが `graph_config.json` に設定する **`tenant_id`** になります。

---

## ステップ 4: API のアクセス許可の設定（アプリケーション許可 - 選択肢 B）

登録したアプリケーションが、全ユーザーの予定表をバックグラウンドで自動的に読み取るための権限（アクセス許可）を設定します：

1. 左側のメニューから **API のアクセス許可** (API permissions) をクリックします。
2. **+ アクセス許可の追加** (Add a permission) ボタンをクリックします。
3. 表示されたペインで **Microsoft Graph** を選択します。
4. **アプリケーションの許可** (Application permissions) を選択します。
   * ※ 注意: ユーザーログインを伴わない全自動実行（選択肢 B）を行うため、**「アプリケーションの許可」**を選択してください。
5. 検索ボックスを使用して、以下のアクセス許可を検索し、チェックを入れます：
   * **`Calendars.Read`** (組織内のすべての予定表の読み取り)
6. 下部の **アクセス許可の追加** (Add permissions) ボタンをクリックして保存します。
7. **管理者の同意の付与（必須）**：
   * 「API のアクセス許可」ページにある **＜組織名＞ に管理者の同意を与えます** (Grant admin consent for <Organization>) を**必ず**クリックしてください。これを行わないと「アクセス拒否 (Access Denied)」になります。

---

## ステップ 5: クライアント シークレット (Client Secret) の生成

自動実行（Confidential Client）を行うため、アプリの認証用パスワード（クライアント シークレット）を作成します：

1. 左側のメニューから **証明書とシークレット** (Certificates & secrets) をクリックします。
2. **クライアント シークレット** タブが選択されていることを確認し、**+ 新しいクライアント シークレット** (New client secret) をクリックします。
3. **説明**（例: `PipelineSecret`）を入力し、有効期限を選択します。
4. **追加** (Add) ボタンをクリックします。
5. 作成完了後、一覧に表示される **値 (Value)** （※「シークレット ID」ではありません）を**すぐにコピーして手元に控えてください**。
   * ※ 注意: この「値」はページを離れたり更新したりすると二度と表示されなくなります。

---

## ステップ 6: 設定ファイルへの適用

取得した値を **[graph_config.json](graph_config.json)** に以下のように設定してください：

```json
{
  "client_id": "取得したアプリケーション (クライアント) ID",
  "tenant_id": "取得したディレクトリ (テナント) ID",
  "client_secret": "取得したクライアント シークレットの「値」",
  "auth_flow": "client_credentials",
  ...
}
```
