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

## ステップ 4: API のアクセス許可の設定

登録したアプリケーションが予定表を読み取るための権限（アクセス許可）を設定します：

1. 左側のメニューから **API のアクセス許可** (API permissions) をクリックします。
2. **+ アクセス許可の追加** (Add a permission) ボタンをクリックします。
3. 表示されたペインで **Microsoft Graph** を選択します。
4. **委任されたアクセス許可** (Delegated permissions) を選択します。
5. 検索ボックスを使用して、以下の 2 つのアクセス許可を検索し、チェックを入れます：
   * **`Calendars.Read`** (サインインユーザーの予定表の読み取り)
   * **`Calendars.Read.Shared`** (他ユーザーから共有された予定表の読み取り)
6. 下部の **アクセス許可の追加** (Add permissions) ボタンをクリックして保存します。

### 管理者の同意（推奨）
* あなたが管理者アカウントを使用している場合、「API のアクセス許可」ページにある **＜組織名＞ に管理者の同意を与えます** (Grant admin consent for <Organization>) をクリックすることをお勧めします。
* これにより、ユーザーがスクリプトを初回実行する際に、アクセスの同意確認画面（ポップアップ）が表示されなくなり、スムーズに実行できるようになります。
