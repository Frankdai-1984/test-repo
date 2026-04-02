# 完整 Workflow 演示

## 每日工作流（自动化+人工）

### 08:00 自动触发
GitHub Actions 运行 `hot-topics-monitor.yml`
- 抓取微博/知乎/跑圈媒体热点
- 生成 `hot-topics/2026-04-03.md`
- 推送至仓库

### 09:00 人工决策（5分钟）
1. 打开 GitHub Project 看板
2. 查看昨日热点报告
3. 判断选题价值 → 拖动到"选题池"或丢弃

### 10:00 开始写作（2-3小时）
1. 从"选题池"拖动卡片到"写作中"
2. 本地写作 `draft_v1.md`
3. 提交到仓库备份

### 14:00 审校循环（1小时）
1. 拖动到"审校中"
2. 8维度检测
3. 不达标 → 修改 → 重新检测
4. 达标 → 拖动到"已发布"

### 16:00 发布
推送至公众号，在看板记录数据

---

## 看板使用指南

### 创建新选题卡片
1. Project 看板 → 📥 选题池
2. "Add item" → 输入热点标题
3. 添加描述：
   ```
   来源: 微博热搜
   日期: 2026-04-03
   概念: 【体制的反转】
   价值: ⭐⭐⭐⭐⭐
   ```
4. 保存

### 状态流转
- 📥 选题池 → 📝 写作中：确定要写
- 📝 写作中 → 🔍 审校中：初稿完成
- 🔍 审校中 → ✅ 已发布：通过检测并推送

### 标签使用
- 🔴 新热点（24h内）
- 🟡 发酵热点（2-5天）
- 🔵 扩展领域（越野/铁三/健身）
- ⭐ 高商业价值
- 📝 待资料搜集

---

## 快速命令

```bash
# 拉取最新热点
cd /root/test-repo
git pull origin main
cat hot-topics/$(date +%Y-%m-%d).md

# 创建新文章
git checkout -b article-$(date +%m%d)
# 写作...
git add .
git commit -m "Draft: 文章标题"
git push origin article-$(date +%m%d)

# 合并到主分支
git checkout main
git merge article-$(date +%m%d)
git push origin main
```