import arxiv
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import datetime

def search_arxiv(keyword, max_results=10):
    search = arxiv.Search(
        query=keyword,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    client = arxiv.Client()
    results = []
    for result in client.results(search):
        results.append({
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

    content.append(Paragraph("📚 最近的论文报告", styles['Title']))
    content.append(Spacer(1, 20))

    for i, paper in enumerate(papers, 1):
        content.append(Paragraph(f"<b>{i}. {paper['title']}</b>", styles['Heading3']))
        content.append(Paragraph(f"🧑 作者: {', '.join(paper['authors'])}", styles['Normal']))
        content.append(Paragraph(f"📅 发布时间: {paper['published']}", styles['Normal']))
        content.append(Paragraph(f"🔗 <a href='{paper['url']}'>{paper['url']}</a>", styles['Normal']))
        content.append(Paragraph(f"📄 摘要: {paper['summary']}", styles['Normal']))
        content.append(Spacer(1, 20))

    doc.build(content)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python fetch_and_generate.py <keyword> <num_papers>")
        sys.exit(1)

    keyword = sys.argv[1]
    num_papers = int(sys.argv[2])
    papers = search_arxiv(keyword, num_papers)
    generate_pdf(papers)

