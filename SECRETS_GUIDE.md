# GitHub Secrets 配置指南

## 已配置的 Secrets

| Secret Name | 用途 | 状态 |
|-------------|------|------|
| WEIBO_COOKIE | 微博热搜抓取 | ⏳ 待填充 |
| ZHIHU_TOKEN | 知乎 API 访问 | ⏳ 待填充 |
| FEISHU_WEBHOOK | 飞书消息推送 | ⏳ 待填充 |

## 如何获取

### 1. 微博 Cookie
1. 登录 weibo.com
2. F12 → Application → Cookies → weibo.com
3. 复制 `SUB` 字段的值

### 2. 知乎 Token
1. 登录 zhihu.com
2. F12 → Network → 任意请求 → Headers
3. 找到 `Authorization: Bearer xxx`，复制 `xxx` 部分

### 3. 飞书 Webhook
1. 飞书群设置 → 添加机器人 → 自定义机器人
2. 复制 Webhook URL

## 添加到 GitHub
Settings → Secrets and variables → Actions → New repository secret

⚠️ 这些密钥具有私密性，请勿上传到代码仓库！