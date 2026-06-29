# CDP Time Tracking Azure アプリ管理・シークレット保守手順書

本プロジェクトは、すでに組織の Microsoft Entra ID (Azure AD) に登録済みの専用アプリケーションを使用して、Microsoft Graph API 経由で Outlook 予定表データを取得します。

全社（同じテナント内）で共通のアプリアクセス許可が取得されているため、**新規のアプリ登録作業は不要です**。本ドキュメントでは、既存アプリの管理、シークレットの手動設定、および有効期限切れに伴う更新手順について説明します。

---

## 1. 登録済みアプリケーション情報

* **アプリケーション (クライアント) ID** (`client_id`)  
  `8b54a005-e2c7-45a8-be9d-43a69ee567a2`
* **ディレクトリ (テナント) ID** (`tenant_id`)  
  `c054587c-162f-4d87-a936-3f2018a4fdaf`
* **設定済みの API アクセス許可**  
  `Calendars.Read` (アプリケーションの許可 - 組織内のすべての予定表の読み取り、管理者同意済み)

---

## 2. クライアント シークレットの手動設定

セキュリティおよび情報漏洩防止のため、認証用の **クライアント シークレット (Client Secret) は Git サーバーにアップロードされていません**。

新しくリポジトリをクローンまたは解圧して利用する際は、管理者から取得したシークレット、もしくは自身で再発行したシークレットの **「値 (Value)」** を、ローカル環境の **`graph_config.json`** に手動で追記する必要があります。

```json
{
  "client_id": "8b54a005-e2c7-45a8-be9d-43a69ee567a2",
  "tenant_id": "c054587c-162f-4d87-a936-3f2018a4fdaf",
  "client_secret": "【ここに手動でクライアントシークレットの「値」を入力】",
  "auth_flow": "client_credentials",
  ...
}
```

> [!WARNING]
> シークレットが記入された `graph_config.json` は機密情報です。決して公共の GitHub などの公開リポジトリにコミット・プッシュしないでください。社内メンバーへ共有する際は、Teams や社内共有フォルダなどの安全な経路を使用してください。

---

## 3. シークレットの有効期限と更新手順

Microsoft のセキュリティ仕様上、クライアント シークレットには**有効期限（最長 2 年）**があります。期限が切れるとスクリプト実行時に認証エラーが発生するため、定期的な再発行と更新が必要です。

### 🔄 更新手順

1. 管理者アカウントで、以下の登録アプリ直通リンクから Azure ポータルに直接アクセスします：
   * 👉 [CDP Time Tracking 登録アプリ管理ページ (Azure Portal)](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/~/Overview/appId/8b54a005-e2c7-45a8-be9d-43a69ee567a2/objectId/766c73d8-923f-4ab1-8f8e-58ee57c4e176/isMSAApp~/false/defaultBlade/Overview/appSignInAudience/AzureADMyOrg/servicePrincipalCreated~/true)
2. 左側のメニューから **「証明書とシークレット」** (Certificates & secrets) を選択します。
3. **「クライアント シークレット」** タブにある期限切れの古いシークレットを削除（ゴミ箱アイコン）します。
4. **`+ 新しいクライアント シークレット`** (New client secret) ボタンをクリックし、説明と有効期限（推奨：24ヶ月）を設定して **「追加」** をクリックします。
5. 追加直後に表示されるシークレットの **「値」** (Value、長い文字列) を**その場でコピー**して手元に保存します。
   * ※ 注意: ページを離れたりリロードすると、値は二度と表示されなくなります。
6. コピーした新しい値を、ローカルの `graph_config.json` の `"client_secret"` 部分に貼り付けます。
7. 更新した `graph_config.json` を、社内の実行担当メンバーに安全な社内チャネル等で共有します。
