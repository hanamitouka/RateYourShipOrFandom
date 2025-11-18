import os
import pandas as pd
from utils.file_utils import ensure_folder
import re

def write_csv(stats, folder):
    """将统计数据写入CSV文件，包含对比分析和分年份统计"""
    ensure_folder(folder)
    
    download_info = stats.get("download_info", {})
    filter_stats = stats.get("filter_stats", {})
    yearly_stats = stats.get("yearly_stats", {})
    is_sampling = download_info.get("is_sampling", False)
    sampling_factor = download_info.get("sampling_factor", 1.0)
    sampling_mode = download_info.get("sampling_mode", "完整分析")
    
    print(f"正在生成CSV文件到: {os.path.abspath(folder)}")
    print(f"分析模式: {sampling_mode}")
    if is_sampling:
        print(f"抽样倍数: {sampling_factor:.2f}")

    # 1. 角色统计CSV - 添加对比信息
    if stats['characters']:
        characters_list = []
        for char, count in sorted(stats['characters'].items(), key=lambda x: x[1], reverse=True):
            filter_count = filter_stats.get('characters', {}).get(char, '')
            data_source = '抽样估算' if is_sampling and not filter_count else '准确统计'
            estimated_count = count if is_sampling else count
            
            characters_list.append({
                '角色名称': char, 
                '统计次数': estimated_count,
                'filter准确次数': filter_count,
                '数据来源': data_source,
                '抽样倍数': sampling_factor if is_sampling else 1.0
            })
        
        characters_df = pd.DataFrame(characters_list)
        characters_df.to_csv(os.path.join(folder, '角色统计.csv'), index=False, encoding='utf-8-sig')
        print(f"角色统计: {len(characters_df)} 条记录")
    
    # 2. 关系统计CSV - 添加对比信息
    if stats['relationships']:
        relationships_list = []
        for rel, count in sorted(stats['relationships'].items(), key=lambda x: x[1], reverse=True):
            filter_count = filter_stats.get('relationships', {}).get(rel, '')
            data_source = '抽样估算' if is_sampling and not filter_count else '准确统计'
            estimated_count = count if is_sampling else count
            
            relationships_list.append({
                '关系名称': rel, 
                '统计次数': estimated_count,
                'filter准确次数': filter_count,
                '数据来源': data_source,
                '抽样倍数': sampling_factor if is_sampling else 1.0
            })
        
        relationships_df = pd.DataFrame(relationships_list)
        relationships_df.to_csv(os.path.join(folder, '关系统计.csv'), index=False, encoding='utf-8-sig')
        print(f"关系统计: {len(relationships_df)} 条记录")
    
    # 3. 评级分布CSV
    if stats['ratings']:
        ratings_list = []
        for rating, count in sorted(stats['ratings'].items(), key=lambda x: x[1], reverse=True):
            estimated_count = count if is_sampling else count
            ratings_list.append({
                '评级类型': rating, 
                '作品数量': estimated_count,
                '抽样倍数': sampling_factor if is_sampling else 1.0
            })
        
        ratings_df = pd.DataFrame(ratings_list)
        ratings_df.to_csv(os.path.join(folder, '评级分布.csv'), index=False, encoding='utf-8-sig')
        print(f"评级分布: {len(ratings_df)} 条记录")
    
    # 4. 警告标签统计CSV
    if stats['warnings']:
        warnings_list = []
        for warning, count in sorted(stats['warnings'].items(), key=lambda x: x[1], reverse=True):
            estimated_count = count if is_sampling else count
            warnings_list.append({
                '警告类型': warning, 
                '出现次数': estimated_count,
                '抽样倍数': sampling_factor if is_sampling else 1.0
            })
        
        warnings_df = pd.DataFrame(warnings_list)
        warnings_df.to_csv(os.path.join(folder, '警告标签统计.csv'), index=False, encoding='utf-8-sig')
        print(f"警告标签统计: {len(warnings_df)} 条记录")
    
    # 5. 分类统计CSV
    if stats['categories']:
        categories_list = []
        for category, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True):
            estimated_count = count if is_sampling else count
            categories_list.append({
                '分类类型': category, 
                '作品数量': estimated_count,
                '抽样倍数': sampling_factor if is_sampling else 1.0
            })
        
        categories_df = pd.DataFrame(categories_list)
        categories_df.to_csv(os.path.join(folder, '分类统计.csv'), index=False, encoding='utf-8-sig')
        print(f"分类统计: {len(categories_df)} 条记录")
    
    # 6. 同人圈统计CSV
    if stats['fandoms']:
        fandoms_list = []
        for fandom, count in sorted(stats['fandoms'].items(), key=lambda x: x[1], reverse=True):
            estimated_count = count if is_sampling else count
            fandoms_list.append({
                '同人圈名称': fandom, 
                '作品数量': estimated_count,
                '抽样倍数': sampling_factor if is_sampling else 1.0
            })
        
        fandoms_df = pd.DataFrame(fandoms_list)
        fandoms_df.to_csv(os.path.join(folder, '同人圈统计.csv'), index=False, encoding='utf-8-sig')
        print(f"同人圈统计: {len(fandoms_df)} 条记录")
    
    # 7. 自由标签统计CSV
    if stats['freeforms']:
        freeforms_list = []
        for freeform, count in sorted(stats['freeforms'].items(), key=lambda x: x[1], reverse=True):
            estimated_count = count if is_sampling else count
            freeforms_list.append({
                '自由标签': freeform, 
                '出现次数': estimated_count,
                '抽样倍数': sampling_factor if is_sampling else 1.0
            })
        
        freeforms_df = pd.DataFrame(freeforms_list)
        freeforms_df.to_csv(os.path.join(folder, '自由标签统计.csv'), index=False, encoding='utf-8-sig')
        print(f"自由标签统计: {len(freeforms_df)} 条记录")
    
    # 8. 详细作品信息CSV
    if stats['works']:
        works_list = []
        for work in stats['works']:
            works_list.append({
                '来源文件': work['source_file'],
                '标题': work['title'],
                '作者': work['author'],
                '年份': work['year'],
                '评级': work['rating'],
                '警告标签': '; '.join(work['warnings']),
                '分类': '; '.join(work['categories']),
                '角色': '; '.join(work['characters']),
                '关系': '; '.join(work['relationships']),
                '同人圈': '; '.join(work['fandoms']),
                '自由标签': '; '.join(work['freeforms']),
                '字数': work['words'],
                '章节': work['chapters'],
                '点赞数': work['kudos'],
                '点击量': work['hits'],
                '书签数': work['bookmarks'],
                '评论数': work['comments']
            })
        
        works_df = pd.DataFrame(works_list)
        works_df.to_csv(os.path.join(folder, '作品详细信息.csv'), index=False, encoding='utf-8-sig')
        print(f"作品详细信息: {len(works_df)} 条记录")
    
    # 9. 综合统计报告CSV
    if stats['works']:
        total_pages = download_info.get('total_pages', 0)
        downloaded_pages = download_info.get('downloaded_pages', 0)
        
        # 计算统计值，考虑抽样倍数
        total_chars = len(stats['characters'])
        total_rels = len(stats['relationships'])
        total_fandoms = len(stats['fandoms'])
        total_freeforms = len(stats['freeforms'])
        avg_chars_per_work = sum(len(work['characters']) for work in stats['works']) / len(stats['works']) if stats['works'] else 0
        avg_rels_per_work = sum(len(work['relationships']) for work in stats['works']) / len(stats['works']) if stats['works'] else 0
        avg_fandoms_per_work = sum(len(work['fandoms']) for work in stats['works']) / len(stats['works']) if stats['works'] else 0
        avg_freeforms_per_work = sum(len(work['freeforms']) for work in stats['works']) / len(stats['works']) if stats['works'] else 0
        avg_words = sum(work['words'] for work in stats['works']) / len(stats['works']) if stats['works'] else 0
        total_kudos = sum(work['kudos'] for work in stats['works'])
        total_hits = sum(work['hits'] for work in stats['works'])
        
        # 如果是抽样模式，对总量进行估算
        if is_sampling:
            total_kudos = int(total_kudos * sampling_factor)
            total_hits = int(total_hits * sampling_factor)
        
        summary_data = {
            '统计项目': [
                '分析模式',
                '总页数',
                '分析页数', 
                '分析作品数',
                '总角色数',
                '总关系数',
                '总同人圈数',
                '总自由标签数',
                '平均每作品角色数',
                '平均每作品关系数',
                '平均每作品同人圈数',
                '平均每作品自由标签数',
                '平均字数',
                '总点赞数',
                '总点击量',
                '抽样倍数'
            ],
            '数值': [
                sampling_mode,
                total_pages,
                downloaded_pages,
                len(stats['works']),
                total_chars,
                total_rels,
                total_fandoms,
                total_freeforms,
                round(avg_chars_per_work, 2),
                round(avg_rels_per_work, 2),
                round(avg_fandoms_per_work, 2),
                round(avg_freeforms_per_work, 2),
                round(avg_words, 2),
                total_kudos,
                total_hits,
                sampling_factor if is_sampling else '无'
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(os.path.join(folder, '综合统计报告.csv'), index=False, encoding='utf-8-sig')
        print("综合统计报告已生成")
    
    # 10. 分年份统计
    create_yearly_statistics(yearly_stats, folder, is_sampling, sampling_factor)
    
    # 11. 对比分析报告
    create_comparison_report(stats, folder)

def create_yearly_statistics(yearly_stats, output_folder, is_sampling=False, sampling_factor=1.0):
    """
    创建分年份统计CSV文件
    """
    yearly_folder = os.path.join(output_folder, "分年份统计")
    os.makedirs(yearly_folder, exist_ok=True)
    
    print("生成分年份统计...")
    
    # 分年份角色统计
    if yearly_stats['characters']:
        yearly_chars = []
        for year, characters in yearly_stats['characters'].items():
            for char, count in sorted(characters.items(), key=lambda x: x[1], reverse=True):
                yearly_chars.append({
                    '年份': year,
                    '角色名称': char,
                    '出现次数': count,
                    '抽样倍数': sampling_factor if is_sampling else 1.0
                })
        
        yearly_chars_df = pd.DataFrame(yearly_chars)
        yearly_chars_df.to_csv(os.path.join(yearly_folder, '分年份角色统计.csv'), index=False, encoding='utf-8-sig')
        print(f"分年份角色统计: {len(yearly_chars_df)} 条记录")
    
    # 分年份关系统计
    if yearly_stats['relationships']:
        yearly_rels = []
        for year, relationships in yearly_stats['relationships'].items():
            for rel, count in sorted(relationships.items(), key=lambda x: x[1], reverse=True):
                yearly_rels.append({
                    '年份': year,
                    '关系名称': rel,
                    '出现次数': count,
                    '抽样倍数': sampling_factor if is_sampling else 1.0
                })
        
        yearly_rels_df = pd.DataFrame(yearly_rels)
        yearly_rels_df.to_csv(os.path.join(yearly_folder, '分年份关系统计.csv'), index=False, encoding='utf-8-sig')
        print(f"分年份关系统计: {len(yearly_rels_df)} 条记录")
    
    # 分年份评级统计
    if yearly_stats['ratings']:
        yearly_ratings = []
        for year, ratings in yearly_stats['ratings'].items():
            for rating, count in sorted(ratings.items(), key=lambda x: x[1], reverse=True):
                yearly_ratings.append({
                    '年份': year,
                    '评级类型': rating,
                    '作品数量': count,
                    '抽样倍数': sampling_factor if is_sampling else 1.0
                })
        
        yearly_ratings_df = pd.DataFrame(yearly_ratings)
        yearly_ratings_df.to_csv(os.path.join(yearly_folder, '分年份评级统计.csv'), index=False, encoding='utf-8-sig')
        print(f"分年份评级统计: {len(yearly_ratings_df)} 条记录")
    
    # 分年份分类统计
    if yearly_stats['categories']:
        yearly_categories = []
        for year, categories in yearly_stats['categories'].items():
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                yearly_categories.append({
                    '年份': year,
                    '分类类型': category,
                    '作品数量': count,
                    '抽样倍数': sampling_factor if is_sampling else 1.0
                })
        
        yearly_categories_df = pd.DataFrame(yearly_categories)
        yearly_categories_df.to_csv(os.path.join(yearly_folder, '分年份分类统计.csv'), index=False, encoding='utf-8-sig')
        print(f"分年份分类统计: {len(yearly_categories_df)} 条记录")
    
    # 分年份同人圈统计
    if yearly_stats['fandoms']:
        yearly_fandoms = []
        for year, fandoms in yearly_stats['fandoms'].items():
            for fandom, count in sorted(fandoms.items(), key=lambda x: x[1], reverse=True):
                yearly_fandoms.append({
                    '年份': year,
                    '同人圈名称': fandom,
                    '出现次数': count,
                    '抽样倍数': sampling_factor if is_sampling else 1.0
                })
        
        yearly_fandoms_df = pd.DataFrame(yearly_fandoms)
        yearly_fandoms_df.to_csv(os.path.join(yearly_folder, '分年份同人圈统计.csv'), index=False, encoding='utf-8-sig')
        print(f"分年份同人圈统计: {len(yearly_fandoms_df)} 条记录")
    
    # 分年份自由标签统计
    if yearly_stats['freeforms']:
        yearly_freeforms = []
        for year, freeforms in yearly_stats['freeforms'].items():
            for freeform, count in sorted(freeforms.items(), key=lambda x: x[1], reverse=True):
                yearly_freeforms.append({
                    '年份': year,
                    '自由标签': freeform,
                    '出现次数': count,
                    '抽样倍数': sampling_factor if is_sampling else 1.0
                })
        
        yearly_freeforms_df = pd.DataFrame(yearly_freeforms)
        yearly_freeforms_df.to_csv(os.path.join(yearly_folder, '分年份自由标签统计.csv'), index=False, encoding='utf-8-sig')
        print(f"分年份自由标签统计: {len(yearly_freeforms_df)} 条记录")
    
    # 年份作品数量统计
    yearly_works_count = {}
    for year_data in [yearly_stats['characters'], yearly_stats['relationships'], yearly_stats['ratings']]:
        for year in year_data:
            if year not in yearly_works_count:
                yearly_works_count[year] = 0
            # 使用任意一个标签类型的最大值作为该年份的作品数估计
            yearly_works_count[year] = max(yearly_works_count[year], sum(year_data[year].values()))
    
    yearly_works_df = pd.DataFrame([
        {
            '年份': year, 
            '作品数量': count,
            '抽样倍数': sampling_factor if is_sampling else 1.0
        }
        for year, count in sorted(yearly_works_count.items(), key=lambda x: x[0])
    ])
    yearly_works_df.to_csv(os.path.join(yearly_folder, '分年份作品数量.csv'), index=False, encoding='utf-8-sig')
    print(f"分年份作品数量: {len(yearly_works_df)} 条记录")

def create_comparison_report(analysis_data, output_folder):
    """
    创建对比分析报告
    """
    filter_stats = analysis_data.get('filter_stats', {})
    download_info = analysis_data.get('download_info', {})
    is_sampling = download_info.get('is_sampling', False)
    
    comparison_folder = os.path.join(output_folder, "对比分析")
    os.makedirs(comparison_folder, exist_ok=True)
    
    print("生成对比分析报告...")
    
    # 角色对比分析
    if filter_stats.get('characters') and analysis_data.get('characters'):
        comparison_chars = []
        for char, filter_count in sorted(filter_stats['characters'].items(), key=lambda x: x[1], reverse=True):
            sampling_count = analysis_data['characters'].get(char, 0)
            comparison_chars.append({
                '角色名称': char,
                'filter准确次数': filter_count,
                '抽样统计次数': sampling_count,
                '绝对差异': sampling_count - filter_count,
                '相对差异(%)': round((sampling_count - filter_count) / filter_count * 100, 2) if filter_count > 0 else 0,
                '抽样模式': is_sampling
            })
        
        comparison_chars_df = pd.DataFrame(comparison_chars)
        comparison_chars_df.to_csv(os.path.join(comparison_folder, '角色对比分析.csv'), index=False, encoding='utf-8-sig')
        print(f"角色对比分析: {len(comparison_chars_df)} 条记录")
    
    # 关系对比分析
    if filter_stats.get('relationships') and analysis_data.get('relationships'):
        comparison_rels = []
        for rel, filter_count in sorted(filter_stats['relationships'].items(), key=lambda x: x[1], reverse=True):
            sampling_count = analysis_data['relationships'].get(rel, 0)
            comparison_rels.append({
                '关系名称': rel,
                'filter准确次数': filter_count,
                '抽样统计次数': sampling_count,
                '绝对差异': sampling_count - filter_count,
                '相对差异(%)': round((sampling_count - filter_count) / filter_count * 100, 2) if filter_count > 0 else 0,
                '抽样模式': is_sampling
            })
        
        comparison_rels_df = pd.DataFrame(comparison_rels)
        comparison_rels_df.to_csv(os.path.join(comparison_folder, '关系对比分析.csv'), index=False, encoding='utf-8-sig')
        print(f"关系对比分析: {len(comparison_rels_df)} 条记录")
    
    # 生成对比总结报告
    create_comparison_summary(analysis_data, comparison_folder)

def create_comparison_summary(analysis_data, comparison_folder):
    """
    创建对比总结报告
    """
    filter_stats = analysis_data.get('filter_stats', {})
    download_info = analysis_data.get('download_info', {})
    is_sampling = download_info.get('is_sampling', False)
    
    summary_data = []
    
    # 角色对比总结
    if filter_stats.get('characters') and analysis_data.get('characters'):
        total_filter_chars = len(filter_stats['characters'])
        total_sampling_chars = len(analysis_data['characters'])
        
        # 计算匹配度
        matched_chars = set(filter_stats['characters'].keys()) & set(analysis_data['characters'].keys())
        match_rate = len(matched_chars) / total_filter_chars * 100 if total_filter_chars > 0 else 0
        
        summary_data.extend([
            {'对比项目': '角色统计', 'filter总数': total_filter_chars, '抽样总数': total_sampling_chars, '匹配度(%)': round(match_rate, 2), '抽样模式': is_sampling},
            {'对比项目': '角色统计', '说明': 'filter提供准确统计，抽样提供完整标签列表'}
        ])
    
    # 关系对比总结
    if filter_stats.get('relationships') and analysis_data.get('relationships'):
        total_filter_rels = len(filter_stats['relationships'])
        total_sampling_rels = len(analysis_data['relationships'])
        
        matched_rels = set(filter_stats['relationships'].keys()) & set(analysis_data['relationships'].keys())
        match_rate = len(matched_rels) / total_filter_rels * 100 if total_filter_rels > 0 else 0
        
        summary_data.extend([
            {'对比项目': '关系统计', 'filter总数': total_filter_rels, '抽样总数': total_sampling_rels, '匹配度(%)': round(match_rate, 2), '抽样模式': is_sampling},
            {'对比项目': '关系统计', '说明': 'filter提供准确统计，抽样提供完整标签列表'}
        ])
    
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(os.path.join(comparison_folder, '对比总结报告.csv'), index=False, encoding='utf-8-sig')
        print("对比总结报告已生成")