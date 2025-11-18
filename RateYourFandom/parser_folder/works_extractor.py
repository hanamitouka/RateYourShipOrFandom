import re
from bs4 import BeautifulSoup

from bs4 import BeautifulSoup
import re

def extract_works_data(html_content, filename):
    """从 AO3 列表页 HTML 内容中提取作品数据（超兼容升级版）"""

    soup = BeautifulSoup(html_content, "html.parser")
    works = []

    # AO3 的每个作品都在 <li class="work blurb group"> 中
    work_elems = soup.find_all("li", class_=re.compile(r"work.*blurb.*group"))

    for elem in work_elems:
        data = {
            "source_file": filename,
            "title": "",
            "author": "",
            "url": "",

            "rating": "",
            "warnings": [],
            "categories": [],
            "fandoms": [],
            "relationships": [],
            "characters": [],
            "freeforms": [],

            "words": 0,
            "chapters": "0",
            "kudos": 0,
            "hits": 0,
            "bookmarks": 0,
            "comments": 0,

            "year": "未知",
        }

        # ========== 标题 & URL ==========
        h = elem.find("h4", class_="heading")
        if h:
            a = h.find("a")
            if a:
                data["title"] = a.text.strip()
                href = a.get("href", "")
                if href.startswith("/"):
                    data["url"] = "https://archiveofourown.org" + href
                else:
                    data["url"] = href

        # 必须有标题才视为有效作品
        if not data["title"]:
            continue

        # ========== 作者 ==========
        author = elem.find("a", rel="author")
        if author:
            data["author"] = author.text.strip()
        else:
            # fallback 方式
            byline = elem.find("span", class_="byline")
            if byline:
                author_link = byline.find("a", rel="author")
                if author_link:
                    data["author"] = author_link.text.strip()

        # ========== 必需标签（rating / warnings / categories） ==========
        tags = elem.find("ul", class_="required-tags")
        if tags:
            # Rating
            rating = tags.find("span", class_="rating")
            if rating:
                data["rating"] = rating.text.strip()

            # Warnings
            for w in tags.find_all("span", class_="warnings"):
                wt = w.text.strip()
                if wt and wt != "No Archive Warnings Apply":
                    data["warnings"].append(wt)

            # Categories
            for c in tags.find_all("span", class_="category"):
                ct = c.text.strip()
                if ct:
                    data["categories"].append(ct)

        fandom_h5 = elem.find("h5", class_="fandoms")
        if fandom_h5:
            for a in fandom_h5.find_all("a", class_="tag"):
                fandom_text = a.text.strip()
                if fandom_text:
                    data["fandoms"].append(fandom_text)
        # ========== AO3 标签（fandom / relationship / character / freeform） ==========
        tag_section = elem.find("ul", class_="tags")
        if tag_section:
            for li in tag_section.find_all("li"):
                cls = " ".join(li.get("class", []))  # 多 class 拼成字符串
                a = li.find("a", class_="tag")
                if not a:
                    continue

                text = a.text.strip()
                if not text:
                    continue

                
                # relationship / relationships
                if "relationship" in cls:
                    data["relationships"].append(text)

                # character / characters
                elif "character" in cls:
                    data["characters"].append(text)

                # freeform / freeforms
                elif "freeform" in cls:
                    data["freeforms"].append(text)

        # ========== Stats 区域（字数 / kudos / 收藏等） ==========
        stats = elem.find("dl", class_="stats")

        def get_int(dd):
            if not dd:
                return 0
            text = dd.text.replace(",", "").strip()
            if "/" in text:
                text = text.split("/")[0]
            return int(text) if text.isdigit() else 0

        if stats:
            data["words"] = get_int(stats.find("dd", class_="words"))
            data["comments"] = get_int(stats.find("dd", class_="comments"))
            data["bookmarks"] = get_int(stats.find("dd", class_="bookmarks"))
            data["kudos"] = get_int(stats.find("dd", class_="kudos"))
            data["hits"] = get_int(stats.find("dd", class_="hits"))

            chapters_dd = stats.find("dd", class_="chapters")
            if chapters_dd:
                data["chapters"] = chapters_dd.text.strip()

        # ========== 年份提取 ==========
        date = elem.find("p", class_="datetime")
        if date:
            m = re.search(r"(20\d{2})", date.text)
            if m:
                data["year"] = m.group(1)

        works.append(data)

    return works
