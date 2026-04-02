#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跑圈热点监控脚本 V2.0
监控平台：微博、知乎、抖音、小红书、百度、跑圈媒体
输出格式：Markdown 摘要 + JSON 原始数据
优化：增加关键词覆盖、增强反爬、多源聚合
"""

import os
import json
import re
import time
import requests
from datetime import datetime
from urllib.parse import quote

# 跑步相关关键词（已大幅扩充）
RUNNING_KEYWORDS = [
    '跑', '马拉松', '越野', '铁三', '铁人三项', '健身',
    '配速', '完赛', '跑步', '晨跑', '夜跑', '训练',
    '全马', '半马', '42公里', '21公里', '5公里', '10公里',
    '跑鞋', '碳板', '心率', '步频', 'PB', '破三', '破四',
    '中签', '报名', '赛事', '奖牌', '兔子', '关门',
    '受伤', '膝盖', '跟腱', '髂胫束', '撞墙',
    '基普乔格', '大迫杰', '何杰', '张德顺', '夏雨雨'
]

def contains_running_keyword(text):
    """检查文本是否包含跑步关键词"""
    if not text:
        return False
    return any(kw in text for kw in RUNNING_KEYWORDS)

def fetch_weibo_hot():
    """抓取微博热搜（需 Cookie）"""
    topics = []
    try:
        cookie = os.environ.get('WEIBO_COOKIE', '')
        if not cookie:
            print("[微博] 未配置 Cookie，尝试无 Cookie 模式")
            # 无 Cookie 模式：尝试公开接口
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            url = 'https://weibo.com/ajax/side/hotSearch'
            resp = requests.get(url, headers=headers, timeout=10)
        else:
            headers = {
                'Cookie': cookie,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            url = 'https://weibo.com/ajax/side/hotSearch'
            resp = requests.get(url, headers=headers, timeout=10)
        
        print(f"[微博] HTTP 状态: {resp.status_code}")
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                realtime = data.get('data', {}).get('realtime', [])
                print(f"[微博] 获取到 {len(realtime)} 条热搜")
                
                for item in realtime[:30]:  # 取前30条
                    word = item.get('word', '')
                    if contains_running_keyword(word):
                        topics.append({
                            'title': word,
                            'heat': item.get('raw_hot', item.get('hot', 'N/A')),
                            'source': '微博热搜',
                            'url': f"https://s.weibo.com/weibo?q={quote(word)}",
                            'category': '🔴 新热点',
                            'timestamp': datetime.now().isoformat()
                        })
            except Exception as e:
                print(f"[微博] JSON解析失败: {e}")
        else:
            print(f"[微博] 请求失败: {resp.status_code}")
            
        print(f"[微博] 匹配到 {len(topics)} 条跑圈相关热点")
    except Exception as e:
        print(f"[微博] 抓取失败: {e}")
    
    return topics

def fetch_zhihu_hot():
    """抓取知乎热榜（增强版）"""
    topics = []
    try:
        # 尝试多个接口
        urls = [
            'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total',
            'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/everyone',
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.zhihu.com/hot'
        }
        
        for url in urls:
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                print(f"[知乎] {url.split('/')[-1]} 状态: {resp.status_code}")
                
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get('data', [])
                    print(f"[知乎] 获取到 {len(items)} 条热榜")
                    
                    for item in items:
                        target = item.get('target', {})
                        title = target.get('title', '') or target.get('question', {}).get('title', '')
                        
                        if contains_running_keyword(title):
                            topics.append({
                                'title': title[:100],
                                'heat': target.get('metrics', target.get('answer_count', 'N/A')),
                                'source': '知乎热榜',
                                'url': target.get('url', f"https://zhihu.com/question/{target.get('id', '')}"),
                                'category': '🔴 新热点',
                                'timestamp': datetime.now().isoformat()
                            })
                    
                    if topics:  # 如果抓到了，就不继续尝试其他接口
                        break
                        
            except Exception as e:
                print(f"[知乎] 接口尝试失败: {e}")
                continue
        
        print(f"[知乎] 匹配到 {len(topics)} 条跑圈相关热点")
    except Exception as e:
        print(f"[知乎] 抓取失败: {e}")
    
    return topics

def fetch_baidu_hot():
    """抓取百度热搜（无需认证）"""
    topics = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 百度热搜 API
        url = 'https://top.baidu.com/api/board?platform=wise&tab=realtime'
        resp = requests.get(url, headers=headers, timeout=10)
        
        print(f"[百度] HTTP 状态: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('data', {}).get('cards', [{}])[0].get('content', [])
            print(f"[百度] 获取到 {len(items)} 条热搜")
            
            for item in items[:30]:
                title = item.get('word', '')
                if contains_running_keyword(title):
                    topics.append({
                        'title': title,
                        'heat': item.get('hotScore', 'N/A'),
                        'source': '百度热搜',
                        'url': item.get('url', f"https://www.baidu.com/s?wd={quote(title)}"),
                        'category': '🔴 新热点',
                        'timestamp': datetime.now().isoformat()
                    })
        
        print(f"[百度] 匹配到 {len(topics)} 条跑圈相关热点")
    except Exception as e:
        print(f"[百度] 抓取失败: {e}")
    
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
        
        url = 'https://www.douyin.com/aweme/v1/web/hot/search/list/'
        resp = requests.get(url, headers=headers, timeout=10)
        
        print(f"[抖音] HTTP 状态: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('data', {}).get('word_list', [])
            print(f"[抖音] 获取到 {len(items)} 条热点")
            
            for item in items[:30]:
                word = item.get('word', '')
                if contains_running_keyword(word):
                    topics.append({
                        'title': word,
                        'heat': item.get('hot_value', 'N/A'),
                        'source': '抖音热点',
                        'url': f"https://www.douyin.com/search/{quote(word)}",
                        'category': '🔴 新热点',
                        'timestamp': datetime.now().isoformat()
                    })
        
        print(f"[抖音] 匹配到 {len(topics)} 条跑圈相关热点")
    except Exception as e:
        print(f"[抖音] 抓取失败: {e}")
    
    return topics

def fetch_xiaohongshu_hot():
    """抓取小红书热点（简化版）"""
    topics = []
    try:
        cookie = os.environ.get('XIAOHONGSHU_COOKIE', '')
        if not cookie:
            print("[小红书] 未配置 Cookie，跳过")
            return topics
        
        # 小红书抓取较复杂，需要特定签名
        # 这里使用简化方案：直接返回空，等待后续优化
        print("[小红书] Cookie 已配置，但抓取需要额外签名验证，暂跳过")
        
    except Exception as e:
        print(f"[小红书] 抓取失败: {e}")
    
    return topics

def fetch_toutiao_hot():
    """抓取今日头条热点（无需认证）"""
    topics = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 头条热搜
        url = 'https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc'
        resp = requests.get(url, headers=headers, timeout=10)
        
        print(f"[头条] HTTP 状态: {resp.status_code}")
        
        if resp.status_code == 200:
            # 头条返回 HTML，需要解析
            # 简化处理：如果包含跑步关键词的标题在页面中
            html = resp.text
            # 这里简化处理，实际需要更复杂的解析
            pass
        
        print(f"[头条] 匹配到 {len(topics)} 条跑圈相关热点")
    except Exception as e:
        print(f"[头条] 抓取失败: {e}")
    
    return topics

def fetch_runhub_news():
    """抓取跑圈垂直媒体"""
    topics = []
    try:
        # 尝试抓取一些公开的跑步资讯网站
        sources = [
            {'name': '跑野大爆炸', 'url': 'https://www.runyeyo.com/', 'selector': 'article h2'},
            {'name': '爱燃烧', 'url': 'https://iranshao.com/', 'selector': '.article-title'},
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for source in sources:
            try:
                resp = requests.get(source['url'], headers=headers, timeout=10)
                if resp.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    titles = soup.select(source['selector'])
                    
                    for title_elem in titles[:5]:
                        title = title_elem.get_text(strip=True)
                        if contains_running_keyword(title) and len(title) > 5:
                            topics.append({
                                'title': title[:80],
                                'heat': 'N/A',
                                'source': source['name'],
                                'url': source['url'],
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
- 数据来源：微博、知乎、百度、抖音、跑圈媒体
- 总计热点：{len(topics)} 条

## 来源统计
"""
    for src, count in sorted(source_count.items(), key=lambda x: -x[1]):
        report += f"- {src}：{count} 条\n"
    
    report += "\n## 热点列表\n\n"
    
    if not topics:
        report += "*今日暂无跑圈相关热点*\n\n"
        report += "可能原因：\n"
        report += "- 今日确实没有跑圈热点\n"
        report += "- Cookie 配置需要更新\n"
        report += "- 某些平台反爬升级\n"
    else:
        for i, topic in enumerate(topics[:20], 1):  # 最多显示20条
            report += f"**{i}. {topic.get('title', '未知')}**\n"
            report += f"- 热度：{topic.get('heat', 'N/A')}\n"
            report += f"- 来源：{topic.get('source', 'N/A')}\n"
            report += f"- 链接：{topic.get('url', 'N/A')}\n\n"
    
    return report

def main():
    print("=" * 60)
    print("🏃 跑圈热点监控启动")
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 创建输出目录
    os.makedirs("hot-topics", exist_ok=True)
    
    # 抓取数据
    all_topics = []
    
    fetchers = [
        ("微博", fetch_weibo_hot),
        ("知乎", fetch_zhihu_hot),
        ("百度", fetch_baidu_hot),
        ("抖音", fetch_douyin_hot),
        ("小红书", fetch_xiaohongshu_hot),
        ("头条", fetch_toutiao_hot),
        ("跑圈媒体", fetch_runhub_news),
    ]
    
    for name, fetcher in fetchers:
        print(f"\n📡 正在抓取 [{name}]...")
        try:
            topics = fetcher()
            all_topics.extend(topics)
            time.sleep(1)  #  polite delay
        except Exception as e:
            print(f"[{name}] 异常: {e}")
    
    print("\n" + "=" * 60)
    
    # 去重（基于标题）
    seen = set()
    unique_topics = []
    for t in all_topics:
        title = t.get('title', '')
        if title and title not in seen:
            seen.add(title)
            unique_topics.append(t)
    
    print(f"📊 去重后: {len(unique_topics)} 条")
    
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
    
    print(f"✅ 报告已保存: {md_path}")
    print(f"✅ JSON 已保存: {json_path}")
    
    # 飞书推送
    feishu_webhook = os.environ.get('FEISHU_WEBHOOK', '')
    
    if feishu_webhook:
        print(f"\n📤 正在推送飞书...")
        try:
            if unique_topics:
                summary = f"🏃 今日跑圈热点：共 {len(unique_topics)} 条\n\n"
                summary += "\n".join([f"{i+1}. {t['title'][:30]}..." if len(t['title']) > 30 else f"{i+1}. {t['title']}" 
                                     for i, t in enumerate(unique_topics[:8])])
            else:
                summary = "🏃 今日跑圈热点监控\n\n暂无新的跑圈热点\n\n建议：检查 Cookie 配置或稍后再试"
            
            resp = requests.post(feishu_webhook, json={
                "msg_type": "text",
                "content": {"text": summary}
            }, timeout=10)
            
            if resp.status_code == 200:
                result = resp.json()
                if result.get('code') == 0:
                    print("✅ 飞书推送成功")
                else:
                    print(f"⚠️ 飞书返回错误: {result}")
            else:
                print(f"⚠️ 飞书 HTTP 错误: {resp.status_code}")
                
        except Exception as e:
            print(f"⚠️ 飞书推送失败: {e}")
    else:
        print("\n⏭️ 未配置 FEISHU_WEBHOOK，跳过推送")
    
    print("\n" + "=" * 60)
    print("🏁 监控完成")
    print("=" * 60)

if __name__ == "__main__":
    main()