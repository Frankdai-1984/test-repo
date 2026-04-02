#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跑圈热点监控脚本
监控平台：微博、知乎、跑圈媒体、抖音、小红书
输出格式：Markdown 摘要 + JSON 原始数据
"""

import os
import json
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup

def fetch_weibo_hot():
    """抓取微博热搜（需 Cookie）"""
    topics = []
    try:
        cookie = os.environ.get('WEIBO_COOKIE', '')
        if not cookie:
            print("[微博] 未配置 Cookie，跳过")
            return topics
        
        headers = {
            'Cookie': cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 微博热搜 API
        url = 'https://weibo.com/ajax/side/hotSearch'
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            realtime = data.get('data', {}).get('realtime', [])
            
            for item in realtime[:20]:  # 取前20条
                word = item.get('word', '')
                if any(k in word for k in ['跑', '马拉松', '越野', '铁三', '健身', '配速', '完赛']):
                    topics.append({
                        'title': word,
                        'heat': item.get('raw_hot', 'N/A'),
                        'source': '微博热搜',
                        'url': f"https://s.weibo.com/weibo?q={word}",
                        'category': '🔴 新热点',
                        'timestamp': datetime.now().isoformat()
                    })
        
        print(f"[微博] 抓取到 {len(topics)} 条跑圈相关热点")
    except Exception as e:
        print(f"[微博] 抓取失败: {e}")
    
    return topics

def fetch_zhihu_hot():
    """抓取知乎热榜（需 Token）"""
    topics = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        url = 'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total'
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('data', [])
            
            for item in items:
                title = item.get('target', {}).get('title', '')
                if any(k in title for k in ['跑', '马拉松', '越野', '铁三', '健身', '配速', '完赛']):
                    topics.append({
                        'title': title,
                        'heat': item.get('target', {}).get('metrics', 'N/A'),
                        'source': '知乎热榜',
                        'url': item.get('target', {}).get('url', ''),
                        'category': '🔴 新热点',
                        'timestamp': datetime.now().isoformat()
                    })
        
        print(f"[知乎] 抓取到 {len(topics)} 条跑圈相关热点")
    except Exception as e:
        print(f"[知乎] 抓取失败: {e}")
    
    return topics

def fetch_douyin_hot():
    """抓取抖音热点（需 Cookie）"""
    topics = []
    try:
        cookie = os.environ.get('DOUYIN_COOKIE', '')
        if not cookie:
            print("[抖音] 未配置 Cookie，跳过")
            return topics
        
        headers = {
            'Cookie': cookie,
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15',
            'Referer': 'https://www.douyin.com/'
        }
        
        # 抖音热点榜
        url = 'https://www.douyin.com/aweme/v1/web/hot/search/list/'
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('data', {}).get('word_list', [])
            
            for item in items[:20]:
                word = item.get('word', '')
                if any(k in word for k in ['跑', '马拉松', '越野', '铁三', '健身', '配速', '完赛', '训练']):
                    topics.append({
                        'title': word,
                        'heat': item.get('hot_value', 'N/A'),
                        'source': '抖音热点',
                        'url': f"https://www.douyin.com/search/{word}",
                        'category': '🔴 新热点',
                        'timestamp': datetime.now().isoformat()
                    })
        
        print(f"[抖音] 抓取到 {len(topics)} 条跑圈相关热点")
    except Exception as e:
        print(f"[抖音] 抓取失败: {e}")
    
    return topics

def fetch_xiaohongshu_hot():
    """抓取小红书热点（需 Cookie）"""
    topics = []
    try:
        cookie = os.environ.get('XIAOHONGSHU_COOKIE', '')
        if not cookie:
            print("[小红书] 未配置 Cookie，跳过")
            return topics
        
        headers = {
            'Cookie': cookie,
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15',
            'X-Sign': 'X',  # 需要动态生成，此处为占位
            'Referer': 'https://www.xiaohongshu.com/'
        }
        
        # 小红书搜索建议/热点
        keywords = ['马拉松', '跑步', '越野跑', '铁人三项', '晨跑', '夜跑']
        
        for kw in keywords:
            try:
                url = f'https://www.xiaohongshu.com/api/sns/web/v1/search/notes?keyword={kw}'
                resp = requests.get(url, headers=headers, timeout=10)
                
                if resp.status_code == 200:
                    data = resp.json()
                    notes = data.get('data', {}).get('items', [])
                    
                    for note in notes[:3]:  # 每个关键词取前3条
                        title = note.get('note_card', {}).get('display_title', '')
                        if title:
                            topics.append({
                                'title': title[:50],  # 截断过长标题
                                'heat': note.get('note_card', {}).get('interact_info', {}).get('liked_count', 'N/A'),
                                'source': '小红书',
                                'url': f"https://www.xiaohongshu.com/search_result?keyword={kw}",
                                'category': '🔴 新热点',
                                'timestamp': datetime.now().isoformat()
                            })
            except:
                continue
        
        # 去重
        seen = set()
        unique_topics = []
        for t in topics:
            if t['title'] not in seen:
                seen.add(t['title'])
                unique_topics.append(t)
        
        print(f"[小红书] 抓取到 {len(unique_topics)} 条跑圈相关热点")
        return unique_topics
        
    except Exception as e:
        print(f"[小红书] 抓取失败: {e}")
    
    return topics

def fetch_runhub_news():
    """抓取跑圈垂直媒体（无需认证）"""
    topics = []
    try:
        # 示例：跑野大爆炸 RSS
        import feedparser
        
        feeds = [
            'https://www.runhub.cn/feed',  # 示例地址
        ]
        
        for feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]:
                    topics.append({
                        'title': entry.get('title', ''),
                        'heat': 'N/A',
                        'source': '跑圈媒体',
                        'url': entry.get('link', ''),
                        'category': '🟡 发酵热点',
                        'timestamp': datetime.now().isoformat()
                    })
            except:
                continue
        
        print(f"[跑圈媒体] 抓取到 {len(topics)} 条新闻")
    except Exception as e:
        print(f"[跑圈媒体] 抓取失败: {e}")
    
    return topics

def generate_report(topics):
    """生成 Markdown 报告"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 按来源分类统计
    source_count = {}
    for t in topics:
        src = t.get('source', '未知')
        source_count[src] = source_count.get(src, 0) + 1
    
    report = f"""# 跑圈热点日报 - {date_str}

## 监控概览
- 生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}
- 数据来源：微博、知乎、抖音、小红书、跑圈媒体
- 总计热点：{len(topics)} 条

## 来源统计
"""
    for src, count in source_count.items():
        report += f"- {src}：{count} 条\n"
    
    report += "\n## 热点列表\n\n"
    
    # 按类别分组
    categories = {'🔴 新热点': [], '🟡 发酵热点': [], '🔵 扩展领域': []}
    for topic in topics:
        cat = topic.get('category', '🔴 新热点')
        if cat in categories:
            categories[cat].append(topic)
    
    for cat, items in categories.items():
        if items:
            report += f"### {cat}\n\n"
            for topic in items:
                report += f"**{topic.get('title', '未知')}**\n"
                report += f"- 热度：{topic.get('heat', 'N/A')}\n"
                report += f"- 来源：{topic.get('source', 'N/A')}\n"
                report += f"- 链接：{topic.get('url', 'N/A')}\n\n"
    
    return report

def main():
    print("=" * 50)
    print("开始监控跑圈热点...")
    print("=" * 50)
    
    # 创建输出目录
    os.makedirs("hot-topics", exist_ok=True)
    
    # 抓取数据
    all_topics = []
    all_topics.extend(fetch_weibo_hot())
    all_topics.extend(fetch_zhihu_hot())
    all_topics.extend(fetch_douyin_hot())
    all_topics.extend(fetch_xiaohongshu_hot())
    all_topics.extend(fetch_runhub_news())
    
    # 去重（基于标题）
    seen = set()
    unique_topics = []
    for t in all_topics:
        title = t.get('title', '')
        if title and title not in seen:
            seen.add(title)
            unique_topics.append(t)
    
    # 生成报告
    date_str = datetime.now().strftime("%Y-%m-%d")
    report = generate_report(unique_topics)
    
    # 保存 Markdown
    md_path = f"hot-topics/{date_str}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    # 保存 JSON
    json_path = f"hot-topics/{date_str}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(unique_topics, f, ensure_ascii=False, indent=2)
    
    print("=" * 50)
    print(f"✅ 报告已生成：{md_path}")
    print(f"✅ 共发现 {len(unique_topics)} 条去重后的热点")
    print("=" * 50)
    
    # 飞书推送（如果配置了 webhook）
    feishu_webhook = os.environ.get('FEISHU_WEBHOOK', '')
    if feishu_webhook and unique_topics:
        try:
            summary = f"今日跑圈热点：共 {len(unique_topics)} 条\n"
            summary += "\n".join([f"• {t['title']}" for t in unique_topics[:5]])
            
            requests.post(feishu_webhook, json={
                "msg_type": "text",
                "content": {"text": summary}
            }, timeout=10)
            print("✅ 已推送至飞书")
        except Exception as e:
            print(f"⚠️ 飞书推送失败: {e}")

if __name__ == "__main__":
    main()