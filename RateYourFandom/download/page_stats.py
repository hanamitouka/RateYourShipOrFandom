import time
import re
from bs4 import BeautifulSoup

def extract_filter_statistics(soup):
    """
    从filter部分提取准确的统计信息 - 改进版本，提取filter中的准确统计
    """
    stats = {
        'ratings': {},
        'warnings': {}, 
        'categories': {},
        'characters': {},
        'relationships': {},
        'fandoms': {}
    }
    
    def extract_from_section(section_id, stats_key, label):
        """从指定部分提取统计信息的辅助函数"""
        section_dd = soup.find('dd', id=section_id)
        if not section_dd:
            return 0
            
        items = section_dd.find_all('li')
        count = 0
        
        for item in items:
            # 获取整个li的文本
            full_text = item.get_text(strip=True)
            # 匹配格式: "角色名 (123,456)" 或 "角色名 (123)"
            match = re.search(r'^(.+?)\s*\((\d+,?\d+)\)$', full_text)
            if match:
                name = match.group(1).strip()
                count_val = int(match.group(2).replace(',', ''))
                stats[stats_key][name] = count_val
                count += 1
            else:
                # 备选方案：分别提取名称和数量
                a_tag = item.find('a')
                span_tag = item.find('span', class_='count')
                if a_tag and span_tag:
                    name = a_tag.get_text(strip=True)
                    count_text = span_tag.get_text(strip=True)
                    count_match = re.search(r'\((\d+,?\d+)\)', count_text)
                    if count_match:
                        count_val = int(count_match.group(1).replace(',', ''))
                        stats[stats_key][name] = count_val
                        count += 1
        
        return count
    
    # 从exclude部分提取各种统计
    extract_from_section('exclude_character_tags', 'characters', '角色')
    extract_from_section('exclude_relationship_tags', 'relationships', '关系')
    extract_from_section('exclude_rating_tags', 'ratings', '评级')
    extract_from_section('exclude_archive_warning_tags', 'warnings', '警告')
    extract_from_section('exclude_category_tags', 'categories', '分类')
    extract_from_section('exclude_fandom_tags', 'fandoms', '同人圈')
    
    # 如果exclude部分没有找到足够的数据，尝试include部分
    if len(stats['characters']) < 5:
        extract_from_section('include_character_tags', 'characters', '角色(include)')
    
    if len(stats['relationships']) < 5:
        extract_from_section('include_relationship_tags', 'relationships', '关系(include)')
    
    return stats

def get_total_pages_and_stats(driver, tag_url):
    """获取总页数和筛选统计"""
    driver.get(tag_url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # 作品总数
    total_works = 0
    h2 = soup.find('h2', class_='heading')
    if h2:
        m = re.search(r'Works\s*\(([\d,]+)\)', h2.text)
        if m:
            total_works = int(m.group(1).replace(',', ''))

    # 页数判断
    total_pages = 1
    pagination = soup.find('ol', class_='pagination') or soup.find('ul', class_='pagination')
    if pagination:
        nums = []
        for li in pagination.find_all('li'):
            a = li.find('a')
            if a and a.text.isdigit():
                nums.append(int(a.text))
        if nums:
            total_pages = max(nums)

    # 如果没有分页，根据作品数估算
    if total_pages == 1 and total_works > 20:
        total_pages = (total_works + 19) // 20

    filter_stats = extract_filter_statistics(soup)

    return total_pages, total_works, driver.page_source, filter_stats