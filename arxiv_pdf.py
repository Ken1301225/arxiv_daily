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

def generate_pdf(papers, filename='papers.pdf'):
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("Paper", styles['Title']))
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
    
    today = datetime.datetime.now(datetime.timezone.utc)
    datestamp = today.strftime("%Y%m%d")
    keyword = sys.argv[1]
    num_papers = int(sys.argv[2])
    papers = fetch_new_papers(keyword, num_papers)
    generate_pdf(papers,filename=f"{datestamp}:{num_papers}_pieces:arxiv_daily_of_{keyword}.pdf")
