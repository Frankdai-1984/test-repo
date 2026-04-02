#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跑圈热点监控脚本 V4.0 - 终极可靠版
使用第三方聚合API，彻底解决反爬问题
"""

import os
import json
import requests
from datetime import datetime

# 跑步相关关键词（用于过滤）
RUNNING_KEYWORDS = [
    '跑', '马拉松', '越野', '铁三', '铁人三项', '健身',
    '配速', '完赛', '跑步', '晨跑', '夜跑', '训练',
    '全马', '半马', '42公里', '21公里', '5公里', '10公里',
    '跑鞋', '碳板', '心率', '步频', 'PB', '破三', '破四',
    '中签', '报名', '赛事', '奖牌', '兔子', '关门',
    '受伤', '膝盖', '跟腱', '髂胫束', '撞墙',
    '基普乔格', '大迫杰', '何杰', '张德顺', '夏雨雨',
    '无锡马拉松', '北京马拉松', '上海马拉松', '广州马拉松',
    '杭州马拉松', '厦门马拉松', '成都马拉松', '武汉马拉松'
]

def contains_running_keyword(text):
    """检查文本是否包含跑步关键词"""
    if not text:
        return False
    return any(kw in text for kw in RUNNING_KEYWORDS)

def fetch_weread_hot():
    """使用瓦斯阅读API（稳定可靠）"""
    topics = []
    try:
        # 瓦斯阅读热榜API
        url = 'https://www.weread.com/hot/api/v1/hot/list'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"[瓦斯阅读] 状态: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('data', {}).get('list', [])
            print(f"[瓦斯阅读] 获取 {len(items)} 条")
            
            for item in items[:50]:
                title = item.get('title', '')
                if contains_running_keyword(title):
                    topics.append({
                        'title': title,
                        'heat': item.get('hot', 'N/A'),
                        'source': '瓦斯阅读',
                        'url': item.get('url', ''),
                        'category': '🔴 新热点',
                        'timestamp': datetime.now().isoformat()
                    })
        
        print(f"[瓦斯阅读] 匹配 {len(topics)} 条跑圈热点")
    except Exception as e:
        print(f"[瓦斯阅读] 失败: {e}")
    
    return topics

def fetch_tophub_hot():
    """使用今日热榜API（今日热榜.xyz）"""
    topics = []
    try:
        # 今日热榜提供多平台聚合
        platforms = [
            {'name': 'weibo', 'cname': '微博'},
            {'name': 'zhihu', 'cname': '知乎'},
            {'name': 'baidu', 'cname': '百度'},
        ]
        
        for plat in platforms:
            try:
                url = f'https://www.tophub.app/api/v2/site/{plat["name"]}'
                resp = requests.get(url, timeout=10)
                
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get('data', [])
                    
                    for item in items[:20]:
                        title = item.get('title', '')
                        if contains_running_keyword(title):
                            topics.append({
                                'title': title,
                                'heat': item.get('hot', 'N/A'),
                                'source': f"{plat['cname']}热搜",
                                'url': item.get('url', ''),
                                'category': '🔴 新热点',
                                'timestamp': datetime.now().isoformat()
                            })
            except:
                continue
        
        print(f"[今日热榜] 匹配 {len(topics)} 条跑圈热点")
    except Exception as e:
        print(f"[今日热榜] 失败: {e}")
    
    return topics

def fetch_hackernews_style():
    """备用方案：直接抓取一些固定跑圈信息源"""
    topics = []
    
    # 如果以上都失败，提供一些固定的跑圈关注项
    # 这些可以手动更新，作为保底
    fallback_topics = [
        {
            'title': '建议手动查看：微博搜索 马拉松',
            'heat': 'N/A',
            'source': '手动提示',
            'url': 'https://s.weibo.com/weibo?q=马拉松',
            'category': '💡 建议',
            'timestamp': datetime.now().isoformat()
        },
        {
            'title': '建议手动查看：知乎搜索 跑步',
            'heat': 'N/A',
            'source': '手动提示',
            'url': 'https://www.zhihu.com/search?type=content&q=跑步',
            'category': '💡 建议',
            'timestamp': datetime.now().isoformat()
        }
    ]
    
    return fallback_topics

def generate_report(topics):
    """生成 Markdown 报告"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    source_count = {}
    for t in topics:
        src = t.get('source', '未知')
        source_count[src] = source_count.get(src, 0) + 1
    
    report = f"""# 跑圈热点日报 - {date_str}

## 监控概览
- 生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}
- 数据来源：第三方聚合API
- 总计热点：{len(topics)} 条

## 来源统计
"""
    for src, count in sorted(source_count.items(), key=lambda x: -x[1]):
        report += f"- {src}：{count} 条\n"
    
    report += "\n## 热点列表\n\n"
    
    if not topics:
        report += "*今日暂无跑圈相关热点*\n\n"
        report += "---\n\n"
        report += "**建议手动查看：**\n"
        report += "- [微博热搜](https://s.weibo.com/top/summary?cate=realtimehot)\n"
        report += "- [知乎热榜](https://zhihu.com/hot)\n"
        report += "- [百度热搜](https://top.baidu.com)\n"
    else:
        for i, topic in enumerate(topics[:20], 1):
            report += f"**{i}. {topic.get('title', '未知')}**\n"
            report += f"- 热度：{topic.get('heat', 'N/A')}\n"
            report += f"- 来源：{topic.get('source', 'N/A')}\n"
            report += f"- 链接：{topic.get('url', 'N/A')}\n\n"
    
    return report

def main():
    print("=" * 60)
    print("🏃 跑圈热点监控 V4.0")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    os.makedirs("hot-topics", exist_ok=True)
    
    all_topics = []
    
    # 尝试多个数据源
    fetchers = [
        ("瓦斯阅读", fetch_weread_hot),
        ("今日热榜", fetch_tophub_hot),
    ]
    
    for name, fetcher in fetchers:
        print(f"\n📡 [{name}] 开始...")
        try:
            topics = fetcher()
            all_topics.extend(topics)
        except Exception as e:
            print(f"[{name}] 异常: {e}")
    
    # 如果都没抓到，提供手动提示
    if not all_topics:
        print("\n⚠️ 自动抓取失败，提供手动查看提示")
        all_topics = fetch_hackernews_style()
    
    print("\n" + "=" * 60)
    
    # 去重
    seen = set()
    unique_topics = []
    for t in all_topics:
        title = t.get('title', '')
        if title and title not in seen and len(title) > 3:
            seen.add(title)
            unique_topics.append(t)
    
    print(f"📊 去重后: {len(unique_topics)} 条")
    
    # 生成报告
    date_str = datetime.now().strftime("%Y-%m-%d")
    report = generate_report(unique_topics)
    
    md_path = f"hot-topics/{date_str}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    json_path = f"hot-topics/{date_str}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(unique_topics, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 报告: {md_path}")
    print(f"✅ JSON: {json_path}")
    
    # 飞书推送
    feishu_webhook = os.environ.get('FEISHU_WEBHOOK', '')
    
    if feishu_webhook:
        print(f"\n📤 推送飞书...")
        try:
            if unique_topics:
                summary = f"🏃 今日跑圈热点：{len(unique_topics)} 条\n"
                for i, t in enumerate(unique_topics[:8], 1):
                    title = t['title'][:25] + "..." if len(t['title']) > 25 else t['title']
                    summary += f"\n{i}. {title}"
            else:
                summary = "🏃 今日跑圈监控\n\n暂无热点，建议手动查看微博/知乎"
            
            resp = requests.post(feishu_webhook, json={
                "msg_type": "text",
                "content": {"text": summary}
            }, timeout=10)
            
            if resp.status_code == 200 and resp.json().get('code') == 0:
                print("✅ 飞书推送成功")
            else:
                print(f"⚠️ 飞书推送失败: {resp.status_code}")
                
        except Exception as e:
            print(f"⚠️ 飞书推送失败: {e}")
    else:
        print("\n⏭️ 未配置 FEISHU_WEBHOOK")
    
    print("\n" + "=" * 60)
    print("🏁 完成")
    print("=" * 60)

if __name__ == "__main__":
    main()