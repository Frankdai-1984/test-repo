#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跑圈热点监控脚本 V3.0 - 可靠版
使用网页抓取 + 多源聚合，绕过API反爬
"""

import os
import json
import re
import time
import requests
from datetime import datetime
from urllib.parse import quote
from bs4 import BeautifulSoup

# 跑步相关关键词
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

def fetch_weibo_hot():
    """抓取微博热搜 - 使用网页版"""
    topics = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        # 微博热搜页面
        url = 'https://s.weibo.com/top/summary?cate=realtimehot'
        resp = requests.get(url, headers=headers, timeout=15)
        
        print(f"[微博] 状态: {resp.status_code}")
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # 热搜表格
            rows = soup.select('#pl_top_realtimehot tbody tr')
            print(f"[微博] 找到 {len(rows)} 行数据")
            
            for row in rows[1:]:  # 跳过表头
                try:
                    td = row.select_one('td:nth-child(2)')
                    if td:
                        a = td.select_one('a')
                        if a:
                            title = a.get_text(strip=True)
                            if contains_running_keyword(title):
                                topics.append({
                                    'title': title,
                                    'heat': 'N/A',
                                    'source': '微博热搜',
                                    'url': 'https://s.weibo.com' + a.get('href', ''),
                                    'category': '🔴 新热点',
                                    'timestamp': datetime.now().isoformat()
                                })
                except:
                    continue
        
        print(f"[微博] 匹配到 {len(topics)} 条跑圈热点")
    except Exception as e:
        print(f"[微博] 失败: {e}")
    
    return topics

def fetch_zhihu_hot():
    """抓取知乎热榜 - 使用网页版"""
    topics = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html'
        }
        
        url = 'https://www.zhihu.com/hot'
        resp = requests.get(url, headers=headers, timeout=15)
        
        print(f"[知乎] 状态: {resp.status_code}")
        
        if resp.status_code == 200:
            # 知乎热榜数据在 JSON 中
            # 尝试从页面中提取
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 寻找热榜标题
            hot_items = soup.select('.HotList-item, [data-za-detail-view-path-module="HotList"] .HotItem-content')
            
            if not hot_items:
                # 备用选择器
                hot_items = soup.find_all('div', class_=re.compile('HotItem|hot-item', re.I))
            
            print(f"[知乎] 找到 {len(hot_items)} 个热榜项")
            
            for item in hot_items[:50]:
                try:
                    title_elem = item.select_one('.HotItem-title, h2, .ContentItem-title')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        if contains_running_keyword(title):
                            link = item.select_one('a')
                            url = link.get('href', '') if link else ''
                            if url and not url.startswith('http'):
                                url = 'https://zhuanlan.zhihu.com' + url
                            
                            topics.append({
                                'title': title[:100],
                                'heat': 'N/A',
                                'source': '知乎热榜',
                                'url': url or 'https://zhihu.com/hot',
                                'category': '🔴 新热点',
                                'timestamp': datetime.now().isoformat()
                            })
                except:
                    continue
        
        print(f"[知乎] 匹配到 {len(topics)} 条跑圈热点")
    except Exception as e:
        print(f"[知乎] 失败: {e}")
    
    return topics

def fetch_baidu_hot():
    """抓取百度热搜 - 使用网页版"""
    topics = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html'
        }
        
        url = 'https://top.baidu.com/board?tab=realtime'
        resp = requests.get(url, headers=headers, timeout=15)
        
        print(f"[百度] 状态: {resp.status_code}")
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 百度热榜项
            items = soup.select('.category-wrap_iQLoo, .content_1YWBm')
            print(f"[百度] 找到 {len(items)} 个热榜项")
            
            for item in items[:30]:
                try:
                    title_elem = item.select_one('.c-single-text-ellipsis, .content-title')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        if contains_running_keyword(title):
                            link_elem = item.select_one('a[href]')
                            url = link_elem.get('href', '') if link_elem else ''
                            
                            topics.append({
                                'title': title,
                                'heat': 'N/A',
                                'source': '百度热搜',
                                'url': url or 'https://top.baidu.com',
                                'category': '🔴 新热点',
                                'timestamp': datetime.now().isoformat()
                            })
                except:
                    continue
        
        print(f"[百度] 匹配到 {len(topics)} 条跑圈热点")
    except Exception as e:
        print(f"[百度] 失败: {e}")
    
    return topics

def fetch_toutiao_hot():
    """抓取今日头条热点"""
    topics = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        # 头条热榜 JSON 接口
        url = 'https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc'
        resp = requests.get(url, headers=headers, timeout=15)
        
        print(f"[头条] 状态: {resp.status_code}")
        
        if resp.status_code == 200:
            # 从HTML中提取初始数据
            match = re.search(r'window\._SSR_HYDRATED_DATA\s*=\s*({.*?})<', resp.text)
            if match:
                data = json.loads(match.group(1))
                items = data.get('InitialState', {}).get('hotEvent', {}).get('data', [])
                
                print(f"[头条] 找到 {len(items)} 个热榜项")
                
                for item in items[:30]:
                    try:
                        title = item.get('Title', '')
                        if contains_running_keyword(title):
                            url = item.get('Url', '')
                            topics.append({
                                'title': title,
                                'heat': item.get('HotValue', 'N/A'),
                                'source': '今日头条',
                                'url': url or 'https://toutiao.com',
                                'category': '🔴 新热点',
                                'timestamp': datetime.now().isoformat()
                            })
                    except:
                        continue
        
        print(f"[头条] 匹配到 {len(topics)} 条跑圈热点")
    except Exception as e:
        print(f"[头条] 失败: {e}")
    
    return topics

def fetch_36kr_running():
    """抓取36氪等科技媒体的体育/跑步相关内容"""
    topics = []
    try:
        # 这里可以添加更多科技媒体的RSS或API
        pass
    except Exception as e:
        print(f"[36氪] 失败: {e}")
    
    return topics

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
- 数据来源：微博、知乎、百度、头条
- 总计热点：{len(topics)} 条

## 来源统计
"""
    for src, count in sorted(source_count.items(), key=lambda x: -x[1]):
        report += f"- {src}：{count} 条\n"
    
    report += "\n## 热点列表\n\n"
    
    if not topics:
        report += "*今日暂无跑圈相关热点*\n\n"
        report += "---\n\n"
        report += "**可能原因：**\n"
        report += "1. 今日确实没有跑圈热点\n"
        report += "2. 各平台反爬升级，抓取受限\n"
        report += "3. 建议：通过浏览器手动查看热点\n"
    else:
        for i, topic in enumerate(topics[:20], 1):
            report += f"**{i}. {topic.get('title', '未知')}**\n"
            report += f"- 热度：{topic.get('heat', 'N/A')}\n"
            report += f"- 来源：{topic.get('source', 'N/A')}\n"
            report += f"- 链接：{topic.get('url', 'N/A')}\n\n"
    
    return report

def main():
    print("=" * 60)
    print("🏃 跑圈热点监控 V3.0")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    os.makedirs("hot-topics", exist_ok=True)
    
    all_topics = []
    
    fetchers = [
        ("微博热搜", fetch_weibo_hot),
        ("知乎热榜", fetch_zhihu_hot),
        ("百度热搜", fetch_baidu_hot),
        ("今日头条", fetch_toutiao_hot),
    ]
    
    for name, fetcher in fetchers:
        print(f"\n📡 [{name}] 开始抓取...")
        try:
            topics = fetcher()
            all_topics.extend(topics)
            time.sleep(2)  # 防止请求过快
        except Exception as e:
            print(f"[{name}] 异常: {e}")
    
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
                summary = "🏃 今日跑圈监控\n\n暂无热点，建议手动查看"
            
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