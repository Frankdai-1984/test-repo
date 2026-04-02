# GitHub Secrets 配置指南 v2.0

## 已配置的 Secrets

| Secret Name | 用途 | 状态 | 优先级 |
|-------------|------|------|--------|
| `WEIBO_COOKIE` | 微博热搜抓取 | ⏳ 待填充 | P1 |
| `ZHIHU_TOKEN` | 知乎 API 访问 | ⏳ 待填充 | P1 |
| `DOUYIN_COOKIE` | 抖音热点抓取 | ⏳ 待填充 | P2 |
| `XIAOHONGSHU_COOKIE` | 小红书热点抓取 | ⏳ 待填充 | P2 |
| `FEISHU_WEBHOOK` | 飞书消息推送 | ⏳ 待填充 | P3 |

---

## 如何获取

### 1. 微博 Cookie（P1 推荐配置）

**步骤**：
1. 登录 https://weibo.com
2. 按 F12 打开开发者工具 → Application/应用 → Cookies → https://weibo.com
3. 找到 `SUB` 字段，复制其值（以 `_2A` 开头的一长串字符）
4. Secret 值格式：`SUB=_2A25xxxxx;`（保留 `SUB=` 前缀）

**验证**：
```bash
curl -H 'Cookie: SUB=你的Cookie' https://weibo.com/ajax/side/hotSearch
```

---

### 2. 知乎 Token（P1 推荐配置）

**步骤**：
1. 登录 https://zhihu.com
2. 按 F12 → Network/网络 → 刷新页面
3. 任意请求 → Headers → 找到 `Authorization: Bearer xxx`
4. 复制 `Bearer` 后面的部分

**替代方案**（Token 失效快）：
知乎热榜不需要登录即可访问，脚本已配置为免 Token 模式。

---

### 3. 抖音 Cookie（P2 可选）

**步骤**：
1. 登录 https://douyin.com
2. 按 F12 → Application → Cookies → https://douyin.com
3. 复制以下关键字段（用 `;` 连接）：
   - `sessionid`
   - `sid_guard`
   - `ttwid`
   - `msToken`

**Secret 值格式**：
```
sessionid=xxx; sid_guard=xxx; ttwid=xxx; msToken=xxx
```

**注意**：
- 抖音反爬严格，Cookie 有效期短（约1-7天）
- 建议配合手动触发使用

---

### 4. 小红书 Cookie（P2 可选）

**步骤**：
1. 登录 https://xiaohongshu.com
2. 按 F12 → Application → Cookies
3. 复制 `web_session` 或 `xhsTracker` 字段

**Secret 值格式**：
```
web_session=xxx; xhsTracker=xxx
```

**注意**：
- 小红书需要 `X-Sign` 签名，当前脚本为简化版
- 复杂抓取建议使用官方 API 或第三方服务

---

### 5. 飞书 Webhook（P3 可选）

**步骤**：
1. 打开飞书群 → 设置 → 群机器人 → 添加机器人
2. 选择「自定义机器人」
3. 复制 Webhook 地址（以 `https://open.feishu.cn/open-apis/bot/v2/hook/` 开头）

**Secret 值**：完整的 Webhook URL

---

## 添加到 GitHub

**路径**：
https://github.com/Frankdai-1984/test-repo/settings/secrets/actions

**步骤**：
1. 点击 "New repository secret"
2. Name 填入上表中的 Secret Name（严格区分大小写）
3. Secret 填入获取的值
4. 点击 "Add secret"

---

## 配置优先级建议

### 最小可用配置（P1）
至少配置 `WEIBO_COOKIE`，即可抓取微博热搜。

### 完整配置（P1+P2+P3）
全部配置后，可获得：
- 微博 + 知乎：基础热点监控
- 抖音 + 小红书：社交媒体趋势
- 飞书：每日推送摘要到手机

---

## 故障排查

### 抓取失败，日志显示 "未配置 Cookie"
→ 检查 Secrets 名称是否完全匹配（区分大小写）

### Cookie 失效快
→ 抖音/小红书 Cookie 有效期短，建议每周更新一次

### 飞书推送失败
→ 检查 Webhook URL 是否完整，是否被删除/重置

---

## 安全提醒

⚠️ **Cookie 等同于账号密码**，请勿：
- 上传到代码仓库
- 发送给他人
- 在公开场合展示

GitHub Secrets 已加密存储，仅 Actions 运行时可用，安全可靠。