import arxiv
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import datetime
import os
import json

HISTORY_FILE = "sent_history.json"

def load_sent_history():
    if not os.path.exists(HISTORY_FILE):
        return set()
    if os.path.getsize(HISTORY_FILE) == 0:
        return set()
    with open(HISTORY_FILE, "r") as f:
        return set(json.load(f))

def save_sent_history(sent_ids):
    with open(HISTORY_FILE, "w") as f:
        json.dump(list(sent_ids), f)

def search_arxiv(keyword,max_results=50):
    # 日期范围搜索（arXiv 查询语法）

    search = arxiv.Search(
        query=keyword,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    client = arxiv.Client()
    results = []
    for result in client.results(search):
        results.append({
            'id': result.get_short_id(),
            'title': result.title.strip(),
            'authors': [a.name for a in result.authors],
            'summary': result.summary.strip(),
            'url': result.entry_id,
            'published': result.published.strftime('%Y-%m-%d')
        })
    return results

def generate_html(papers, keyword, num_papers,filename="papers.html"):
    today = datetime.datetime.now(datetime.timezone.utc)
    datestamp = today.strftime("%Y-%m-%d")
    style = """
    <style>
    body { font-family: 'Segoe UI', Arial, sans-serif; background: #f8f9fa; color: #333; }
    h2 { color: #2d6cdf; }
    .paper-list { margin: 0; padding: 0; }
    .paper-item { background: #fff; border-radius: 8px; box-shadow: 0 2px 8px #eee; margin: 16px 0; padding: 16px; }
    .title { font-size: 1.1em; font-weight: bold; color: #1a237e; margin-bottom: 8px; }
    .authors { color: #555; font-size: 0.95em; margin-bottom: 6px; }
    .abstract { font-size: 0.98em; margin-bottom: 8px; }
    .meta { font-size: 0.92em; color: #888; }
    a { color: #1565c0; text-decoration: none; }
    a:hover { text-decoration: underline; }
    </style>
    """
    html = f"""
    <html>
    <head>
    {style}
    </head>
    <body>
        <h2>{datestamp} -> arXiv 最新论文推荐（关键词：{keyword}，数量：{num_papers}）</h2>
        <div class="paper-list">
    """
    for p in papers:
        html += f"""
        <div class="paper-item">
            <div class="title"><a href="{p['link']}" target="_blank">{p['title']}</a></div>
            <div class="authors">作者：{p['authors']}</div>
            <div class="abstract">{p['summary']}</div>
            <div class="meta">arXiv编号：{p['id']} | 发布时间：{p['published']}</div>
        </div>
        """
    html += """
        </div>
        <div style="margin-top:30px;color:#aaa;font-size:0.9em;">本邮件由GitHub Actions自动发送 | arXiv聚合服务</div>
    </body>
    </html>
    """
    # return html
    # html = f"""
    # <html>
    # <head>
    #     <style>
    #         body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
    #         h1 {{ color: #333; }}
    #         .paper {{ margin-bottom: 30px; }}
    #         .title {{ font-size: 18px; font-weight: bold; }}
    #         .meta {{ color: #555; font-size: 14px; }}
    #         .abstract {{ margin-top: 10px; }}
    #     </style>
    # </head>
    # <body>
    #     <h1>{datestamp} | {num_papers} Papers | arXiv Daily: {keyword}</h1>
    # """
    #
    # for i, paper in enumerate(papers, 1):
    #     html += f"""
    #     <div class="paper">
    #         <div class="title">{i}. {paper['title']}</div>
    #         <div class="meta">Authors: {', '.join(paper['authors'])}</div>
    #         <div class="meta">Published: {paper['published']}</div>
    #         <div class="meta">Link: <a href="{paper['url']}">{paper['url']}</a></div>
    #         <div class="abstract">{paper['summary']}</div>
    #     </div>
    #     """

    # html += "</body></html>"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    
def generate_pdf(papers, keyword , num_papers ,filename='papers.pdf'):
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    content = []

    today = datetime.datetime.now(datetime.timezone.utc)
    datestamp = today.strftime("%Y%m%d")
    content.append(Paragraph(f"{datestamp}:{num_papers}_pieces:arxiv_daily_of_{keyword}", styles['Title']))
    content.append(Spacer(1, 20))

    for i, paper in enumerate(papers, 1):
        content.append(Paragraph(f"<b>{i}. {paper['title']}</b>", styles['Heading3']))
        content.append(Paragraph(f"authors: {', '.join(paper['authors'])}", styles['Normal']))
        content.append(Paragraph(f"published time: {paper['published']}", styles['Normal']))
        content.append(Paragraph(f"<a href='{paper['url']}'>{paper['url']}</a>", styles['Normal']))
        content.append(Paragraph(f"abstract: {paper['summary']}", styles['Normal']))
        content.append(Spacer(1, 20))

    doc.build(content)

def fetch_new_papers(keyword, target_count):
    sent_ids = load_sent_history()
    collected = []

    results = search_arxiv(keyword, max_results=20)

    for paper in results:
        if paper["id"] not in sent_ids and len(collected) < target_count:
            collected.append(paper)
            sent_ids.add(paper["id"])

    save_sent_history(sent_ids)
    return collected

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python arxiv_pdf.py <keyword> <num_papers>")
        sys.exit(1)
    
    keyword = sys.argv[1]
    num_papers = int(sys.argv[2])
    papers = fetch_new_papers(keyword, num_papers)
    # generate_pdf(papers,keyword,num_papers)
    generate_html(papers,keyword,num_papers)
