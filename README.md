# bits-insights
Leetcode dream team.

🧠 Bits & Insights — Scholarly Search Platform

A minimalistic academic search web application built with Flask, powered by the arXiv API, with Firebase Authentication and Firestore database for user-specific data such as favorites and reading history.

🚀 Features
🔍 1. Advanced arXiv Search

Keyword search

Author search

Category filter

Combined queries (author + category)

Boolean search (AND/OR)

Custom relevance ranking using:

Term-frequency scoring

Title-weighted relevance boost

Clean search results page with:

Title

Authors

Abstract summary

PDF link

arXiv link

Publication date

📄 2. Paper Detail Page

Includes:

Title

Abstract

Authors

Publication date

Primary category

PDF link

Link to arXiv page

Also supports:

⭐ Add/Remove Favorites

📘 Recently Viewed (per user)

📚 3. Recently Viewed Papers

Automatically tracks papers the user views

Displays on homepage

Stored per user (Firebase)

Up to 10 items

❤️ 4. Favorites System

Stored in Firebase Firestore under:

users/{uid}/favorites/{arxiv_id}


Supports:

Add to favorites

Remove from favorites

Favorites page

Persistent across sessions

🔐 5. Authentication

Powered by Firebase Authentication:

Login

Signup

Persistent session

Auto-redirect after login

Navbar updates to show:

Logged-in email

Logout button

🚪 6. Logout

Firebase signOut()

Navbar updates instantly

Redirect to homepage

🎨 7. UI / UX

Minimalistic black and white design

Clean typography

Intuitive navigation

Responsive layout

🧩 8. Architecture

Backend: Flask

Frontend: HTML + CSS

Database: Firestore

Authentication: Firebase Auth

Data Source: arXiv API (via arxiv Python library)

Containers: Docker

📦 Tech Stack
Backend

Python 3.11

Flask

arxiv (Python library)

feedparser (legacy)

requests (legacy, minimal use)

Frontend

HTML5

CSS3

Firebase Web SDK (compat)

firebase-app-compat

firebase-auth-compat

firebase-firestore-compat

Infrastructure

Docker

Docker Compose

Firestore NoSQL database

Firebase Authentication

📁 Project Structure Example
bits-insights/
│
├── app.py
├── search_strategy.py
├── requirements.txt
├── Dockerfile
│
├── templates/
│   ├── index.html
│   ├── search_results.html
│   ├── paper_detail.html
│   ├── favorites.html
│   └── login.html
│
└── static/
    └── (optional CSS / images)

🔧 Installation & Run (Docker)
1. Clone repo
git clone <your repo>
cd bits-insights

2. Build and start
docker compose up --build

3. Visit the app

http://localhost:5000

🔥 Future Work

Discussion Forum (per-paper or general)

Browse page (filter by field / trending papers)

Notification system (alerts for new papers)

Better ranking algorithm (BM25, embeddings, etc.)