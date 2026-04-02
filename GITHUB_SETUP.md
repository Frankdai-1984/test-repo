# GitHub 完整配置指南 v2.0

## ✅ 已完成配置

### 1. SSH 免密码认证
- 密钥路径：`~/.ssh/id_ed25519`
- 状态：已验证，可正常推送/拉取

### 2. GitHub Actions 自动化
- 工作流文件：`.github/workflows/hot-topics-monitor.yml`
- 功能：每日早8点自动抓取跑圈热点
- 输出：保存到 `hot-topics/YYYYMMDD.md`
- 状态：✅ 已部署，⏳ 待配置 Secrets 后激活

### 3. 项目文档
- `PROJECT.md` - 看板工作流说明
- `SECRETS_GUIDE.md` - 密钥获取指南
- `scripts/hot_topics_monitor.py` - 监控脚本框架

---

## ⏳ 需手动完成的配置（5分钟）

### 步骤1：创建 Project 看板（2分钟）

1. 打开 https://github.com/Frankdai-1984/test-repo/projects
2. 点击绿色按钮 **"Link a project"** → **"New project"**
3. 选择 **"Board"**（看板视图）
4. Title 填写：**跑圈内容创作看板**
5. 点击 **"Create project"**

**创建列（Columns）：**
- 📥 选题池（未开始）
- 📝 写作中
- 🔍 审校中
- ✅ 已发布

### 步骤2：添加 Secrets（2分钟）

1. 打开 https://github.com/Frankdai-1984/test-repo/settings/secrets/actions
2. 点击 **"New repository secret"**
3. 逐个添加以下密钥：

| Secret Name | Value 示例 | 说明 |
|-------------|-----------|------|
| `WEIBO_COOKIE` | `SUB=_2A25xxx` | 微博登录 Cookie |
| `ZHIHU_TOKEN` | `Bearer xxx` | 知乎 API Token |
| `FEISHU_WEBHOOK` | `https://open.feishu.cn/xxx` | 飞书机器人地址 |

**当前可以先跳过**，后续需要自动化推送时再配置。

### 步骤3：手动触发测试（1分钟）

1. 打开 https://github.com/Frankdai-1984/test-repo/actions
2. 点击左侧 **"跑圈热点监控"**
3. 点击右侧 **"Run workflow"** → **"Run workflow"**
4. 等待 1-2 分钟，查看运行结果

---

## 🎯 完成后的 Workflow

```
每日早8点（自动）
    ↓
GitHub Actions 抓取热点
    ↓
生成报告 → 保存到仓库
    ↓
（可选）推送到飞书
    ↓
你在 Project 看板上拖动卡片
    ↓
写作 → 审校 → 发布
```

---

## 📁 仓库结构

```
test-repo/
├── .github/
│   └── workflows/
│       └── hot-topics-monitor.yml    # 自动化配置
├── hot-topics/                        # 热点日报归档
│   ├── 2026-04-02.md
│   └── 2026-04-02.json
├── scripts/
│   └── hot_topics_monitor.py         # 监控脚本
├── PROJECT.md                         # 项目说明
├── SECRETS_GUIDE.md                   # 密钥指南
└── README.md                          # 仓库首页
```

---

## 🔗 快速链接

- [仓库首页](https://github.com/Frankdai-1984/test-repo)
- [Actions 工作流](https://github.com/Frankdai-1984/test-repo/actions)
- [创建 Project](https://github.com/Frankdai-1984/test-repo/projects)
- [Secrets 设置](https://github.com/Frankdai-1984/test-repo/settings/secrets/actions)

---

*配置完成时间：2026-04-02*  
*下次维护：按需添加新的监控源或调整定时任务*