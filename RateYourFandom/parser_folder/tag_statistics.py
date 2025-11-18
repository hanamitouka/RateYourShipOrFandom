# tag_statistics.py
import os
import re
from collections import defaultdict, Counter

def _normalize_tag(tag):
    """标准化标签文本：去首尾空白，collapse 多个空格。保留原大小写（AO3 标签大小写有意义），
    但去除不可见字符。返回原始字符串（如果为空则返回 None）。"""
    if tag is None:
        return None
    text = re.sub(r'\s+', ' ', str(tag)).strip()
    return text if text else None

def analyze_characters_relationships_fandoms(works, download_info=None, filter_stats=None,
                                             count_once_per_work=True):
    """
    分析 AO3 作品列表中的 characters/relationships/fandoms。
    参数:
      - works: list of work dicts（由 works_extractor 提供）
      - download_info: 可选 dict，包含 'is_sampling' 和 'sampling_factor' 等
      - filter_stats: 可选 dict，用于后续对比（仅存回传，不在此函数自动使用）
      - count_once_per_work: 如果 True，则一个作品内重复出现的同一标签只计 1 次（通常需要）
    返回:
      dict with keys: characters, relationships, fandoms, works, download_info, filter_stats, yearly_stats
    """
    # 准备结构（Counter 比 defaultdict(int) 更直观）
    all_characters = Counter()
    all_relationships = Counter()
    all_fandoms = Counter()

    yearly_characters = defaultdict(Counter)
    yearly_relationships = defaultdict(Counter)
    yearly_fandoms = defaultdict(Counter)

    # 处理下载信息默认值
    if download_info is None:
        download_info = {
            'total_pages': 0,
            'total_works': 0,
            'downloaded_pages': 0,
            'sampling_mode': '完整分析',
            'sampling_factor': 1.0,
            'is_sampling': False
        }

    if filter_stats is None:
        filter_stats = {}

    is_sampling = bool(download_info.get('is_sampling', False))
    try:
        sampling_factor = float(download_info.get('sampling_factor', 1.0))
    except Exception:
        sampling_factor = 1.0

    print(f"开始分析角色、关系和fandom数据（作品数={len(works)}) ...")

    # 遍历作品
    for i, work in enumerate(works):
        year = work.get('year') or '未知'

        # optional: 有时 works 的标签可能是 None 或字符串，强制成 list
        characters = work.get('characters') or []
        relationships = work.get('relationships') or []
        fandoms = work.get('fandoms') or []

        # 标准化并去重（在单个作品内）以避免一篇作品多次列出同一标签时被重复计数
        def normalize_and_filter(tag_list):
            normalized = []
            for t in tag_list:
                nt = _normalize_tag(t)
                if nt:
                    normalized.append(nt)
            return normalized

        norm_chars = normalize_and_filter(characters)
        norm_rels = normalize_and_filter(relationships)
        norm_fans = normalize_and_filter(fandoms)

        if count_once_per_work:
            # 只在该作品内计数一次
            unique_chars = set(norm_chars)
            unique_rels = set(norm_rels)
            unique_fans = set(norm_fans)
        else:
            unique_chars = norm_chars
            unique_rels = norm_rels
            unique_fans = norm_fans

        # 增加计数
        for ch in unique_chars:
            all_characters[ch] += 1
            yearly_characters[year][ch] += 1

        for rel in unique_rels:
            all_relationships[rel] += 1
            yearly_relationships[year][rel] += 1

        for fan in unique_fans:
            all_fandoms[fan] += 1
            yearly_fandoms[year][fan] += 1

        # 进度打印（每100条）
        if (i + 1) % 100 == 0:
            print(f"已处理 {i + 1}/{len(works)} 个作品")

    # 如果抽样模式并且需要估算，则对计数做放大
    if is_sampling and sampling_factor and sampling_factor > 1.0:
        print(f"抽样模式：对统计数据应用抽样倍数 {sampling_factor:.2f}")

        def scale_counter(counter_obj, factor):
            return {k: int(v * factor) for k, v in counter_obj.items()}

        def scale_yearly(nested):
            out = {}
            for y, counter_obj in nested.items():
                out[y] = {k: int(v * sampling_factor) for k, v in counter_obj.items()}
            return out

        characters_dict = scale_counter(all_characters,sampling_factor)
        relationships_dict = scale_counter(all_relationships,sampling_factor)
        fandoms_dict = scale_counter(all_fandoms,sampling_factor)

        yearly_characters_dict = scale_yearly(yearly_characters)
        yearly_relationships_dict = scale_yearly(yearly_relationships)
        yearly_fandoms_dict = scale_yearly(yearly_fandoms)
    else:
        # 直接转换为普通 dict（保持年份下为普通 dict）
        characters_dict = dict(all_characters)
        relationships_dict = dict(all_relationships)
        fandoms_dict = dict(all_fandoms)

        yearly_characters_dict = {y: dict(c) for y, c in yearly_characters.items()}
        yearly_relationships_dict = {y: dict(c) for y, c in yearly_relationships.items()}
        yearly_fandoms_dict = {y: dict(c) for y, c in yearly_fandoms.items()}

    print("角色、关系和fandom分析完成：")
    print(f"  角色: {len(characters_dict)} 个不同角色")
    print(f"  关系: {len(relationships_dict)} 个不同关系")
    print(f"  同人圈: {len(fandoms_dict)} 个不同同人圈")

    return {
        'characters': characters_dict,
        'relationships': relationships_dict,
        'fandoms': fandoms_dict,
        'works': works,
        'download_info': download_info,
        'filter_stats': filter_stats,
        'yearly_stats': {
            'characters': yearly_characters_dict,
            'relationships': yearly_relationships_dict,
            'fandoms': yearly_fandoms_dict
        }
    }


def apply_sampling_to_tag_stats(tag_stats, sampling_factor):
    """
    对已经生成的 tag_stats 应用抽样补偿（按键放大计数）。
    该函数接受由 analyze_characters_relationships_fandoms 返回的数据结构（或类似结构）。
    """
    try:
        factor = float(sampling_factor)
    except Exception:
        factor = 1.0

    if factor <= 1.0:
        return tag_stats

    print(f"对标签统计应用抽样补偿因子: {factor}")

    def apply_factor(d):
        if isinstance(d, dict):
            return {k: int(v * factor) for k, v in d.items()}
        else:
            # 如果传入 Counter 或其他，尝试转换
            try:
                return {k: int(v * factor) for k, v in dict(d).items()}
            except Exception:
                return d

    def apply_factor_nested(nested):
        out = {}
        for y, sub in nested.items():
            out[y] = apply_factor(sub)
        return out

    # 安全获取键
    if 'characters' in tag_stats:
        tag_stats['characters'] = apply_factor(tag_stats['characters'])
    if 'relationships' in tag_stats:
        tag_stats['relationships'] = apply_factor(tag_stats['relationships'])
    if 'fandoms' in tag_stats:
        tag_stats['fandoms'] = apply_factor(tag_stats['fandoms'])

    yearly = tag_stats.get('yearly_stats', {})
    if 'characters' in yearly:
        yearly['characters'] = apply_factor_nested(yearly['characters'])
    if 'relationships' in yearly:
        yearly['relationships'] = apply_factor_nested(yearly['relationships'])
    if 'fandoms' in yearly:
        yearly['fandoms'] = apply_factor_nested(yearly['fandoms'])

    tag_stats['yearly_stats'] = yearly
    return tag_stats


# ----------------- CSV / 报表相关函数（保持原接口但更鲁棒） -----------------
def create_tag_analysis_csvs(analysis_data, output_folder):
    import os
    import pandas as pd

    os.makedirs(output_folder, exist_ok=True)

    download_info = analysis_data.get('download_info', {}) or {}
    sampling_mode = download_info.get('sampling_mode', '完整分析')
    is_sampling = bool(download_info.get('is_sampling', False))
    sampling_factor = download_info.get('sampling_factor', 1.0) or 1.0
    filter_stats = analysis_data.get('filter_stats', {}) or {}
    yearly_stats = analysis_data.get('yearly_stats', {})

    print(f"正在生成角色、关系和fandom的CSV文件到: {os.path.abspath(output_folder)}")
    print(f"分析模式: {sampling_mode}")
    if is_sampling:
        print(f"抽样倍数: {sampling_factor:.2f}")

    # 1. 角色统计CSV
    characters = analysis_data.get('characters', {}) or {}
    if characters:
        characters_list = []
        for char, count in sorted(characters.items(), key=lambda x: x[1], reverse=True):
            filter_count = filter_stats.get('characters', {}).get(char, '')
            data_source = '抽样估算' if is_sampling and not filter_count else '准确统计'
            characters_list.append({
                '角色名称': char,
                '统计次数': int(count),
                'filter准确次数': filter_count,
                '数据来源': data_source,
                '抽样倍数': float(sampling_factor) if is_sampling else 1.0
            })
        pd.DataFrame(characters_list).to_csv(os.path.join(output_folder, '角色统计.csv'),
                                             index=False, encoding='utf-8-sig')
        print(f"角色统计: {len(characters_list)} 条记录")

    # 2. 关系统计CSV
    relationships = analysis_data.get('relationships', {}) or {}
    if relationships:
        relationships_list = []
        for rel, count in sorted(relationships.items(), key=lambda x: x[1], reverse=True):
            filter_count = filter_stats.get('relationships', {}).get(rel, '')
            data_source = '抽样估算' if is_sampling and not filter_count else '准确统计'
            relationships_list.append({
                '关系名称': rel,
                '统计次数': int(count),
                'filter准确次数': filter_count,
                '数据来源': data_source,
                '抽样倍数': float(sampling_factor) if is_sampling else 1.0
            })
        pd.DataFrame(relationships_list).to_csv(os.path.join(output_folder, '关系统计.csv'),
                                                index=False, encoding='utf-8-sig')
        print(f"关系统计: {len(relationships_list)} 条记录")

    # 3. 同人圈统计CSV
    fandoms = analysis_data.get('fandoms', {}) or {}
    if fandoms:
        fandoms_list = []
        for fandom, count in sorted(fandoms.items(), key=lambda x: x[1], reverse=True):
            fandoms_list.append({
                '同人圈名称': fandom,
                '作品数量': int(count),
                '抽样倍数': float(sampling_factor) if is_sampling else 1.0
            })
        pd.DataFrame(fandoms_list).to_csv(os.path.join(output_folder, '同人圈统计.csv'),
                                          index=False, encoding='utf-8-sig')
        print(f"同人圈统计: {len(fandoms_list)} 条记录")

    # 4. 分年份统计
    create_tag_yearly_statistics(yearly_stats, output_folder, is_sampling, sampling_factor)

    # 5. 对比分析
    create_tag_comparison_report(analysis_data, output_folder)


def create_tag_yearly_statistics(yearly_stats, output_folder, is_sampling=False, sampling_factor=1.0):
    import os
    import pandas as pd

    yearly_folder = os.path.join(output_folder, "分年份统计")
    os.makedirs(yearly_folder, exist_ok=True)

    print("生成分年份统计...")

    y_chars = yearly_stats.get('characters', {}) or {}
    if y_chars:
        rows = []
        for year, chars in sorted(y_chars.items(), key=lambda x: x[0]):
            for char, count in sorted(chars.items(), key=lambda x: x[1], reverse=True):
                rows.append({
                    '年份': year,
                    '角色名称': char,
                    '出现次数': int(count),
                    '抽样倍数': float(sampling_factor) if is_sampling else 1.0
                })
        pd.DataFrame(rows).to_csv(os.path.join(yearly_folder, '分年份角色统计.csv'),
                                 index=False, encoding='utf-8-sig')
        print(f"分年份角色统计: {len(rows)} 条记录")

    y_rels = yearly_stats.get('relationships', {}) or {}
    if y_rels:
        rows = []
        for year, rels in sorted(y_rels.items(), key=lambda x: x[0]):
            for rel, count in sorted(rels.items(), key=lambda x: x[1], reverse=True):
                rows.append({
                    '年份': year,
                    '关系名称': rel,
                    '出现次数': int(count),
                    '抽样倍数': float(sampling_factor) if is_sampling else 1.0
                })
        pd.DataFrame(rows).to_csv(os.path.join(yearly_folder, '分年份关系统计.csv'),
                                 index=False, encoding='utf-8-sig')
        print(f"分年份关系统计: {len(rows)} 条记录")

    y_fans = yearly_stats.get('fandoms', {}) or {}
    if y_fans:
        rows = []
        for year, fans in sorted(y_fans.items(), key=lambda x: x[0]):
            for fandom, count in sorted(fans.items(), key=lambda x: x[1], reverse=True):
                rows.append({
                    '年份': year,
                    '同人圈名称': fandom,
                    '出现次数': int(count),
                    '抽样倍数': float(sampling_factor) if is_sampling else 1.0
                })
        pd.DataFrame(rows).to_csv(os.path.join(yearly_folder, '分年份同人圈统计.csv'),
                                 index=False, encoding='utf-8-sig')
        print(f"分年份同人圈统计: {len(rows)} 条记录")

    # 年份作品数量估计：选择 characters/relationships/fandoms 中的最大总数作为该年作品数估计
    yearly_works_count = {}
    sources = [y_chars, y_rels, y_fans]
    for source in sources:
        for year, data in source.items():
            yearly_works_count.setdefault(year, 0)
            try:
                yearly_works_count[year] = max(yearly_works_count[year], sum(int(v) for v in data.values()))
            except Exception:
                # 若遇到异常（非数值），跳过该条目
                continue

    rows = []
    for year in sorted(yearly_works_count.keys()):
        rows.append({
            '年份': year,
            '作品数量': int(yearly_works_count[year]),
            '抽样倍数': float(sampling_factor) if is_sampling else 1.0
        })
    pd.DataFrame(rows).to_csv(os.path.join(yearly_folder, '分年份作品数量.csv'),
                             index=False, encoding='utf-8-sig')
    print(f"分年份作品数量: {len(rows)} 条记录")


def create_tag_comparison_report(analysis_data, output_folder):
    import os
    import pandas as pd

    filter_stats = analysis_data.get('filter_stats', {}) or {}
    download_info = analysis_data.get('download_info', {}) or {}
    is_sampling = bool(download_info.get('is_sampling', False))

    comparison_folder = os.path.join(output_folder, "对比分析")
    os.makedirs(comparison_folder, exist_ok=True)

    print("生成对比分析报告...")

    if filter_stats.get('characters') and analysis_data.get('characters'):
        rows = []
        for char, filter_count in sorted(filter_stats['characters'].items(), key=lambda x: x[1], reverse=True):
            sampling_count = int(analysis_data['characters'].get(char, 0))
            rows.append({
                '角色名称': char,
                'filter准确次数': int(filter_count),
                '抽样统计次数': sampling_count,
                '绝对差异': sampling_count - int(filter_count),
                '相对差异(%)': round((sampling_count - int(filter_count)) / int(filter_count) * 100, 2) if int(filter_count) > 0 else 0,
                '抽样模式': is_sampling
            })
        pd.DataFrame(rows).to_csv(os.path.join(comparison_folder, '角色对比分析.csv'),
                                 index=False, encoding='utf-8-sig')
        print(f"角色对比分析: {len(rows)} 条记录")

    if filter_stats.get('relationships') and analysis_data.get('relationships'):
        rows = []
        for rel, filter_count in sorted(filter_stats['relationships'].items(), key=lambda x: x[1], reverse=True):
            sampling_count = int(analysis_data['relationships'].get(rel, 0))
            rows.append({
                '关系名称': rel,
                'filter准确次数': int(filter_count),
                '抽样统计次数': sampling_count,
                '绝对差异': sampling_count - int(filter_count),
                '相对差异(%)': round((sampling_count - int(filter_count)) / int(filter_count) * 100, 2) if int(filter_count) > 0 else 0,
                '抽样模式': is_sampling
            })
        pd.DataFrame(rows).to_csv(os.path.join(comparison_folder, '关系对比分析.csv'),
                                 index=False, encoding='utf-8-sig')
        print(f"关系对比分析: {len(rows)} 条记录")

    # 对比总结
    create_tag_comparison_summary(analysis_data, comparison_folder)


def create_tag_comparison_summary(analysis_data, comparison_folder):
    import os
    import pandas as pd

    filter_stats = analysis_data.get('filter_stats', {}) or {}
    download_info = analysis_data.get('download_info', {}) or {}
    is_sampling = bool(download_info.get('is_sampling', False))

    summary_data = []

    if filter_stats.get('characters') and analysis_data.get('characters'):
        total_filter_chars = len(filter_stats['characters'])
        total_sampling_chars = len(analysis_data['characters'])
        matched_chars = set(filter_stats['characters'].keys()) & set(analysis_data['characters'].keys())
        match_rate = len(matched_chars) / total_filter_chars * 100 if total_filter_chars > 0 else 0
        summary_data.append({
            '对比项目': '角色统计',
            'filter总数': total_filter_chars,
            '抽样总数': total_sampling_chars,
            '匹配度(%)': round(match_rate, 2),
            '抽样模式': is_sampling
        })
        summary_data.append({'对比项目': '角色统计', '说明': 'filter提供准确统计，抽样提供完整标签列表'})

    if filter_stats.get('relationships') and analysis_data.get('relationships'):
        total_filter_rels = len(filter_stats['relationships'])
        total_sampling_rels = len(analysis_data['relationships'])
        matched_rels = set(filter_stats['relationships'].keys()) & set(analysis_data['relationships'].keys())
        match_rate = len(matched_rels) / total_filter_rels * 100 if total_filter_rels > 0 else 0
        summary_data.append({
            '对比项目': '关系统计',
            'filter总数': total_filter_rels,
            '抽样总数': total_sampling_rels,
            '匹配度(%)': round(match_rate, 2),
            '抽样模式': is_sampling
        })
        summary_data.append({'对比项目': '关系统计', '说明': 'filter提供准确统计，抽样提供完整标签列表'})

    if summary_data:
        os.makedirs(comparison_folder, exist_ok=True)
        pd.DataFrame(summary_data).to_csv(os.path.join(comparison_folder, '对比总结报告.csv'),
                                          index=False, encoding='utf-8-sig')
        print("对比总结报告已生成")


def get_top_tags_summary(tag_stats, top_n=10):
    summary = {}
    chars = tag_stats.get('characters', {}) or {}
    rels = tag_stats.get('relationships', {}) or {}
    fans = tag_stats.get('fandoms', {}) or {}

    if chars:
        top_characters = sorted(chars.items(), key=lambda x: x[1], reverse=True)[:top_n]
        summary['top_characters'] = dict(top_characters)
    if rels:
        top_relationships = sorted(rels.items(), key=lambda x: x[1], reverse=True)[:top_n]
        summary['top_relationships'] = dict(top_relationships)
    if fans:
        top_fandoms = sorted(fans.items(), key=lambda x: x[1], reverse=True)[:top_n]
        summary['top_fandoms'] = dict(top_fandoms)
    return summary


def print_tag_analysis_summary(analysis_data):
    characters = analysis_data.get('characters', {}) or {}
    relationships = analysis_data.get('relationships', {}) or {}
    fandoms = analysis_data.get('fandoms', {}) or {}

    print("\n" + "="*50)
    print("角色、关系和fandom分析摘要")
    print("="*50)

    print(f"角色统计: {len(characters)} 个不同角色")
    if characters:
        for char, count in sorted(characters.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {char}: {count} 次")

    print(f"关系统计: {len(relationships)} 个不同关系")
    if relationships:
        for rel, count in sorted(relationships.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {rel}: {count} 次")

    print(f"同人圈统计: {len(fandoms)} 个不同同人圈")
    if fandoms:
        for fandom, count in sorted(fandoms.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {fandom}: {count} 次")

    yearly_stats = analysis_data.get('yearly_stats', {}) or {}
    years_chars = list((yearly_stats.get('characters') or {}).keys())
    if years_chars:
        years = sorted(years_chars)
        print(f"时间跨度: {min(years)} - {max(years)}")
