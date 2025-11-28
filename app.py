from flask import Flask, render_template, request, session, redirect, url_for
import requests
import feedparser
import os

from search_strategy import ArxivSearchStrategy

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-later"

strategy = ArxivSearchStrategy()

@app.route("/")
def home():
    history = session.get("reading_history", [])
    return render_template("index.html", history=history)


@app.route("/search")
def search():
    query = request.args.get("query", "").strip()
    author = request.args.get("author", "").strip()
    category = request.args.get("category", "").strip()

    # If no search parameters, return empty results
    if not query and not author and not category:
        return render_template(
            "search_results.html",
            papers=[],
            query="",
            author="",
            category="",
        )

    # -------- 1. Choose which search strategy to use --------
    # Priority example:
    #  (author + category) > author > (category only) > keywords

    if author and category:
        # Author + Category
        results_iter = strategy.search_author_in_category(
            author=author,
            category=category,
            max_results=40,
        )
    elif author:
        # Author only
        results_iter = strategy.search_by_author(
            author_name=author,
            max_results=40,
        )
    elif category and not query:
        # Category only, no keywords
        results_iter = strategy.search_by_category(
            category=category,
            max_results=40,
        )
    else:
        # Keywords (can have additional category filtering)
        if category:
            complex_q = f"({query}) AND cat:{category}" if query else f"cat:{category}"
            results_iter = strategy.complex_query(
                query=complex_q,
                max_results=40,
            )
        else:
            # Pure keyword search
            results_iter = strategy.search_by_keywords(
                keywords=query or "all",
                max_results=40,
            )

    # -------- 2. Optional: Custom scoring / ranking based on query --------
    # If the user entered keywords, use your rank_by_relevance_score to re-rank
    if query:
        ranked = strategy.rank_by_relevance_score(
            results_iter,
            query_terms=query.split(),
        )
        results_list = [r for score, r in ranked if score > 0] or [r for score, r in ranked]
    else:
        # No keywords (e.g., pure author/category search), keep original order
        results_list = list(results_iter)

    # -------- 3. Convert arxiv.Result to dict needed by template --------
    papers = []
    for r in results_list:
        # r.entry_id similar to "http://arxiv.org/abs/2401.12345v1"
        arxiv_id = r.entry_id.split("/")[-1]

        # published might be datetime or None
        if getattr(r, "published", None):
            published_str = r.published.strftime("%Y-%m-%d")
        else:
            published_str = ""

        authors = []
        try:
            authors = [a.name for a in r.authors]
        except Exception:
            authors = []

        papers.append({
            "title": r.title,
            "summary": r.summary,
            "authors": authors,
            "html_link": r.entry_id,
            "pdf_link": getattr(r, "pdf_url", None),
            "published": published_str,
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
    # Use our ArxivSearchStrategy to get paper by ID
    result = strategy.get_paper_by_id(arxiv_id)

    if result is None:
        # If not found, render a simple not found page
        return render_template("paper_detail.html", paper=None, arxiv_id=arxiv_id)

    # ===== Convert arxiv.Result to dict for template =====
    # arxiv_id: some libraries use result.get_short_id(), or you can use the passed-in value
    paper_id = arxiv_id

    # Published date
    if getattr(result, "published", None):
        published_str = result.published.strftime("%Y-%m-%d")
    else:
        published_str = ""

    # Authors list
    try:
        authors = [a.name for a in result.authors]
    except Exception:
        authors = []

    # Primary category (might be missing)
    primary_category = getattr(result, "primary_category", "")

    paper = {
        "arxiv_id": paper_id,
        "title": result.title,
        "summary": result.summary,
        "authors": authors,
        "published": published_str,
        "html_link": result.entry_id,          # Detail page link
        "pdf_link": getattr(result, "pdf_url", None),
        "primary_category": primary_category,
    }

    # ====== Continue to keep your previous reading_history logic (stored in session)======
    history = session.get("reading_history", [])

    # Remove duplicates: if the same paper was viewed, delete the old one
    history = [h for h in history if h["arxiv_id"] != paper_id]

    # Insert at the front
    history.insert(0, {
        "arxiv_id": paper_id,
        "title": result.title,
    })

    # Keep at most 10 entries
    history = history[:10]
    session["reading_history"] = history
    # ====================================================

    # This is the old session-based favorites feature. If you have switched to Firebase favorites, the frontend might not use this anymore,
    # but it's harmless to keep it. Pass an is_favorite to the template for compatibility with the old template.
    favorites = session.get("favorites", [])
    is_favorite = any(f["arxiv_id"] == paper_id for f in favorites)

    return render_template(
        "paper_detail.html",
        paper=paper,
        arxiv_id=paper_id,
        is_favorite=is_favorite,
    )


@app.route("/toggle_favorite/<arxiv_id>", methods=["POST"])
def toggle_favorite(arxiv_id):
    title = request.form.get("title", "")
    favorites = session.get("favorites", [])

    # Check if it's already in favorites
    exists = any(f["arxiv_id"] == arxiv_id for f in favorites)

    if exists:
        # If already favorited, remove it
        favorites = [f for f in favorites if f["arxiv_id"] != arxiv_id]
    else:
        # If not favorited, add to the front
        favorites.insert(0, {
            "arxiv_id": arxiv_id,
            "title": title,
        })
        # Keep at most 50 entries
        favorites = favorites[:50]

    session["favorites"] = favorites

    # After operation, return to the paper detail page
    return redirect(url_for("paper_detail", arxiv_id=arxiv_id))

@app.route("/favorites")
def favorites_page():
    return render_template("favorites.html")


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/browse")
def browse():
    # 1. Read from frontend
    category = request.args.get("category", "cs.AI").strip()  # Default cs.AI
    days_str = request.args.get("days", "7").strip()          # Default 7 days

    try:
        days = int(days_str)
    except ValueError:
        days = 7

    # 2. Construct query: by category + recent N days
    #   Here we use search_recent_papers + arxiv's query syntax
    query = f"cat:{category}"

    results_iter = strategy.search_recent_papers(
        keywords=query,
        days=days,
        max_results=30,
    )

    # 3. Convert arxiv.Result to dict for template
    papers = []
    for r in results_iter:
        arxiv_id = r.entry_id.split("/")[-1]

        if getattr(r, "published", None):
            published_str = r.published.strftime("%Y-%m-%d")
        else:
            published_str = ""

        try:
            authors = [a.name for a in r.authors]
        except Exception:
            authors = []

        papers.append({
            "title": r.title,
            "summary": r.summary,
            "authors": authors,
            "html_link": r.entry_id,
            "pdf_link": getattr(r, "pdf_url", None),
            "published": published_str,
            "arxiv_id": arxiv_id,
        })

    # 4. Some common categories for dropdown
    categories = [
        ("cs.AI", "AI"),
        ("cs.LG", "Machine Learning"),
        ("cs.CL", "Computation & Language"),
        ("cs.CV", "Computer Vision"),
        ("math.PR", "Probability"),
    ]

    day_options = [7, 30, 90]

    return render_template(
        "browse.html",
        papers=papers,
        current_category=category,
        current_days=days,
        categories=categories,
        day_options=day_options,
    )

@app.route("/forum")
def forum():
    return render_template("forum.html")

@app.route("/forum/<thread_id>")
def forum_thread(thread_id):
    return render_template("thread.html", thread_id=thread_id)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
