import os
import json
import re
from collections import defaultdict
from parser_folder.works_extractor import extract_works_data
from parser_folder.tag_statistics import analyze_characters_relationships_fandoms, apply_sampling_to_tag_stats

def analyze_folder(folder):
    """分析下载的页面数据，包含分年份统计和对比分析"""
    info_path = os.path.join(folder, "download_info.json")
    if os.path.exists(info_path):
        with open(info_path, "r", encoding="utf-8") as f:
            info = json.load(f)
    else:
        info = {
            "sampling_factor": 1.0,
            "is_sampling": False,
            "filter_stats": {}
        }

    sampling_factor = info.get("sampling_factor", 1.0)
    is_sampling = info.get("is_sampling", False)
    filter_stats = info.get("filter_stats", {})

    works = []
    
    # 其他统计数据结构
    all_ratings = defaultdict(int)
    all_warnings = defaultdict(int)
    all_categories = defaultdict(int)
    all_freeforms = defaultdict(int)
    
    # 分年份统计
    yearly_ratings = defaultdict(lambda: defaultdict(int))
    yearly_warnings = defaultdict(lambda: defaultdict(int))
    yearly_categories = defaultdict(lambda: defaultdict(int))
    yearly_freeforms = defaultdict(lambda: defaultdict(int))

    # 读取所有 HTML 文件
    html_files = []
    for f in os.listdir(folder):
        if f.endswith('.html') and f.startswith('page_'):
            match = re.match(r'page_(\d+)\.html', f)
            if match:
                html_files.append(f)
    
    print(f"找到 {len(html_files)} 个HTML文件进行分析")
    
    # 按页码排序
    html_files.sort(key=lambda x: int(re.search(r'page_(\d+)\.html', x).group(1)))
    
    for filename in html_files:
        file_path = os.path.join(folder, filename)
        print(f"分析文件: {filename}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
                works_from_file = extract_works_data(html_content, filename)
                works.extend(works_from_file)
                print(f"  从 {filename} 中提取到 {len(works_from_file)} 个作品")
        except Exception as e:
            print(f"处理文件 {filename} 时出错: {e}")
    
    print(f"总共提取到 {len(works)} 个作品")
    
    # 使用专门的函数统计角色、关系和fandom
    tag_stats = analyze_characters_relationships_fandoms(works, info, filter_stats)
    
    # 应用抽样补偿
    if is_sampling and sampling_factor > 1:
        tag_stats = apply_sampling_to_tag_stats(tag_stats, 1)
    
    # 统计其他信息
    for work in works:
        year = work.get('year', '未知')
        
        # 统计评级
        rating = work['rating']
        if rating and rating.strip():
            all_ratings[rating] += 1
            yearly_ratings[year][rating] += 1
        
        # 统计警告
        for warning in work['warnings']:
            if warning and warning.strip():
                all_warnings[warning] += 1
                yearly_warnings[year][warning] += 1
        
        # 统计分类
        for category in work['categories']:
            if category and category.strip():
                all_categories[category] += 1
                yearly_categories[year][category] += 1
                
        # 统计自由标签
        for freeform in work['freeforms']:
            if freeform and freeform.strip():
                all_freeforms[freeform] += 1
                yearly_freeforms[year][freeform] += 1

    # 对其他统计应用抽样补偿
    if is_sampling and sampling_factor > 1:
        def apply_sampling_factor(data_dict, factor):
            return {key: int(value * factor) for key, value in data_dict.items()}
        
        def apply_sampling_to_nested(nested_dict, factor):
            result = {}
            for year, data in nested_dict.items():
                result[year] = {key: int(value * factor) for key, value in data.items()}
            return result
        
        all_ratings = apply_sampling_factor(all_ratings, sampling_factor)
        all_warnings = apply_sampling_factor(all_warnings, sampling_factor)
        all_categories = apply_sampling_factor(all_categories, sampling_factor)
        all_freeforms = apply_sampling_factor(all_freeforms, sampling_factor)
        
        yearly_ratings = apply_sampling_to_nested(yearly_ratings, sampling_factor)
        yearly_warnings = apply_sampling_to_nested(yearly_warnings, sampling_factor)
        yearly_categories = apply_sampling_to_nested(yearly_categories, sampling_factor)
        yearly_freeforms = apply_sampling_to_nested(yearly_freeforms, sampling_factor)

    # 数值统计
    numeric_stats = defaultdict(list)
    for work in works:
        numeric_stats["words"].append(work['words'])
        numeric_stats["kudos"].append(work['kudos'])
        numeric_stats["comments"].append(work['comments'])
        numeric_stats["bookmarks"].append(work['bookmarks'])
        numeric_stats["hits"].append(work['hits'])

    # 构建返回数据结构
    stats = {
        'characters': tag_stats['characters'],
        'relationships': tag_stats['relationships'],
        'fandoms': tag_stats['fandoms'],
        'ratings': dict(all_ratings),
        'warnings': dict(all_warnings),
        'categories': dict(all_categories),
        'freeforms': dict(all_freeforms),
        'works': works,
        'numeric_stats': dict(numeric_stats),
        'download_info': info,
        'filter_stats': filter_stats,
        'yearly_stats': {
            'characters': tag_stats['yearly_stats']['characters'],
            'relationships': tag_stats['yearly_stats']['relationships'],
            'fandoms': tag_stats['yearly_stats']['fandoms'],
            'ratings': dict(yearly_ratings),
            'warnings': dict(yearly_warnings),
            'categories': dict(yearly_categories),
            'freeforms': dict(yearly_freeforms)
        }
    }

    print(f"统计摘要:")
    print(f"  角色: {len(stats['characters'])} 个不同角色")
    print(f"  关系: {len(stats['relationships'])} 个不同关系") 
    print(f"  Fandom: {len(stats['fandoms'])} 个不同Fandom")
    print(f"  自由标签: {len(stats['freeforms'])} 个不同自由标签")
    
    return stats