from download.downloader import download_ao3_pages
from parser_folder.analyzer import analyze_folder
from output.csv_writer import write_csv

def main():
    tag_url = input("输入AO3标签页：")
    save_folder = "ao3_html_pages"
    output_folder = "ao3_csv_output"

    print("开始下载页面...")
    download_info = download_ao3_pages(tag_url, save_folder)
    
    print("分析数据...")
    stats = analyze_folder(save_folder)
    
    print("生成CSV文件...")
    write_csv(stats, output_folder)

    print("完成！CSV已生成在", output_folder, "文件夹中。")

if __name__ == "__main__":
    main()
