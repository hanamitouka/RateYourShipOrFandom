import os
import time
import random
import json
from bs4 import BeautifulSoup
import re

from download.page_stats import get_total_pages_and_stats
from utils.file_utils import ensure_folder
from utils.chrome_driver import create_driver

def download_ao3_pages(tag_url, save_folder):
    ensure_folder(save_folder)
    driver = create_driver()

    total_pages, total_works, first_html, filter_stats = get_total_pages_and_stats(driver, tag_url)
    
    print(f"总页数: {total_pages}, 总作品数: {total_works}")

    # 保存第一页
    with open(f"{save_folder}/page_1.html", "w", encoding="utf-8") as f:
        f.write(first_html)

    # 抽样 or 全量
    if total_pages <= 20:
        target_pages = list(range(2, total_pages + 1))
        sampling_mode = "完整分析"
        print("使用完整分析模式")
    else:
        all_pages = list(range(2, total_pages + 1))
        sample_size = min(19, len(all_pages))
        target_pages = random.sample(all_pages, sample_size)
        sampling_mode = f"随机抽样（20/{total_pages}）"
        print(f"使用抽样模式，抽取 {sample_size + 1} 页")

    downloaded = 1

    for i, page in enumerate(target_pages, 1):
        url = f"{tag_url}?page={page}"
        print(f"下载页面 {page} ({i}/{len(target_pages)})")
        
        driver.get(url)
        time.sleep(3 + random.random() * 2)  # 随机延迟避免被封
        
        # 检查是否被重定向到验证页面
        if "checkpoint" in driver.current_url or "captcha" in driver.current_url:
            print("遇到验证码，停止下载")
            break

        html = driver.page_source
        
        # 检查页面是否包含作品
        if "work blurb group" not in html:
            print(f"页面 {page} 可能为空或格式错误，跳过")
            continue

        with open(f"{save_folder}/page_{page}.html", "w", encoding="utf-8") as f:
            f.write(html)

        downloaded += 1

    driver.quit()

    # 计算抽样因子
    sampling_factor = total_pages / downloaded if downloaded < total_pages else 1

    info = {
        "total_pages": total_pages,
        "total_works": total_works,
        "downloaded_pages": downloaded,
        "sampling_mode": sampling_mode,
        "sampling_factor": sampling_factor,
        "is_sampling": downloaded < total_pages,
        "filter_stats": filter_stats
    }

    with open(f"{save_folder}/download_info.json", "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)

    print(f"下载完成: {downloaded}/{total_pages} 页")
    return info