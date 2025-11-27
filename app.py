from flask import Flask, render_template, request, session
import requests
import feedparser


app = Flask(__name__)
app.secret_key = "dev-secret-key-change-later"

@app.route("/")
def home():
    history = session.get("reading_history", [])
    return render_template("index.html", history=history)


@app.route("/search")
def search():
    query = request.args.get("query", "").strip()
    author = request.args.get("author", "").strip()
    category = request.args.get("category", "").strip()

    # If nothing is entered, return an empty results page
    if not query and not author and not category:
        return render_template("search_results.html", papers=[], query="", author="", category="")

    # Construct arXiv search query string
    search_query = "all:" + (query or "all")
    if author:
        search_query += f"+AND+au:{author}"
    if category:
        search_query += f"+AND+cat:{category}"

    url = f"http://export.arxiv.org/api/query?search_query={search_query}&start=0&max_results=20"

    # Add a timeout to avoid hanging
    resp = requests.get(url, timeout=5)
    xml_data = resp.text

    # Use feedparser to parse the Atom feed (more robust)
    feed = feedparser.parse(xml_data)

    papers = []
    for entry in feed.entries:
        title = entry.title if "title" in entry else "Untitled"
        summary = entry.summary if "summary" in entry else ""

        # The unique arXiv ID, e.g., "2401.12345v1"
        arxiv_id = ""
        if "id" in entry:
            # entry.id typically looks like "http://arxiv.org/abs/2401.12345v1"
            arxiv_id = entry.id.split("/abs/")[-1]

        # Authors
        authors = []
        if "authors" in entry:
            authors = [a.name for a in entry.authors if hasattr(a, "name")]

        # Published date
        published = ""
        if "published" in entry:
            published = entry.published[:10]

        # Links
        html_link = entry.link if "link" in entry else None
        pdf_link = None
        if "links" in entry:
            for link in entry.links:
                href = getattr(link, "href", "")
                type_ = getattr(link, "type", "")
                if "pdf" in href or type_ == "application/pdf":
                    pdf_link = href
                    break

        papers.append({
            "title": title,
            "summary": summary,
            "authors": authors,
            "html_link": html_link,
            "pdf_link": pdf_link,
            "published": published,
            "arxiv_id": arxiv_id,
        })

    return render_template(
        "search_results.html",
        papers=papers,
        query=query,
        author=author,
        category=category,
    )

@app.route("/paper/<arxiv_id>")
def paper_detail(arxiv_id):
    # Use the id_list parameter to query by arXiv ID
    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"

    resp = requests.get(url, timeout=5)
    xml_data = resp.text

    feed = feedparser.parse(xml_data)

    if not feed.entries:
        # If the paper is not found, just show a simple message
        return render_template("paper_detail.html", paper=None, arxiv_id=arxiv_id)

    entry = feed.entries[0]

    title = entry.title if "title" in entry else "Untitled"
    summary = entry.summary if "summary" in entry else ""

    authors = []
    if "authors" in entry:
        authors = [a.name for a in entry.authors if hasattr(a, "name")]

    published = ""
    if "published" in entry:
        published = entry.published[:10]

    html_link = entry.link if "link" in entry else None
    pdf_link = None
    if "links" in entry:
        for link in entry.links:
            href = getattr(link, "href", "")
            type_ = getattr(link, "type", "")
            if "pdf" in href or type_ == "application/pdf":
                pdf_link = href
                break

    # You can also get the primary category (if needed)
    primary_category = getattr(entry, "arxiv_primary_category", {}).get("term", "") \
        if hasattr(entry, "arxiv_primary_category") else ""

    # ========= Update "reading history" here =========
    history = session.get("reading_history", [])

    # Remove duplicates: if the same paper was viewed before, remove the old one
    history = [h for h in history if h["arxiv_id"] != arxiv_id]

    # Insert at the beginning
    history.insert(0, {
        "arxiv_id": arxiv_id,
        "title": title,
    })

    # Keep at most 10 records
    history = history[:10]

    session["reading_history"] = history
    # =======================================

    paper = {
        "arxiv_id": arxiv_id,
        "title": title,
        "summary": summary,
        "authors": authors,
        "published": published,
        "html_link": html_link,
        "pdf_link": pdf_link,
        "primary_category": primary_category,
    }

    return render_template("paper_detail.html", paper=paper, arxiv_id=arxiv_id)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
