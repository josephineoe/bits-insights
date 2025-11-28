# bits-insights
Leetcode dream team.

# 🧠 Bits & Insights — Scholarly Search Platform

A minimalistic academic search web application built with **Flask**, powered by the **arXiv API**, and enhanced with **Firebase Authentication** and **Firestore** for user-specific features such as favorites and reading history.

---

## 🚀 Features

### 🔍 1. Advanced arXiv Search
- Keyword search  
- Author search  
- Category filter  
- Combined author + category search  
- Boolean query support (AND / OR)  
- Custom relevance ranking using:
  - Term-frequency scoring  
  - Extra weight for title matches  
- Organized search result cards displaying:
  - Title  
  - Authors  
  - Abstract summary  
  - Publication date  
  - PDF link  
  - arXiv link  

---

### 📄 2. Paper Detail Page
Includes:
- Full paper metadata  
- Title, abstract, authors  
- Primary category  
- PDF & arXiv page links  
- ⭐ Add / Remove favorites  
- 📘 Recently viewed tracking (up to 10 items)  

---

### 📚 3. Recently Viewed
- Automatically updated when a paper is viewed  
- Displayed on homepage  
- Stored per user (Firestore)  
- Maintains up to 10 items  

---

### ❤️ 4. Favorites System
Stored in **Firestore** under:
users/{uid}/favorites/{arxiv_id}


Supports:
- Add favorite  
- Remove favorite  
- Favorites page  
- Always synced to user’s authentication state  

---

### 🔐 5. Authentication
Using **Firebase Authentication**:
- Login  
- Signup  
- Persistent login session  
- Auto redirect after login  
- Navbar shows:
  - User email  
  - Logout button  

---

### 🚪 6. Logout
- Firebase signOut  
- Navbar refresh  
- Redirect to homepage  

---

### 🎨 7. UI / UX
- Minimalistic **black & white** theme  
- Simple and clean layout  
- Responsive spacing  
- Easy navigation  

---

## 🧩 Architecture

### Backend
- **Flask** (Python web framework)  
- **search_strategy.py** for advanced arXiv search operations  
- **Session system** for non-auth users (recently viewed fallback)  

### Frontend
- HTML5 + CSS (no Bootstrap, pure minimal style)  
- Firebase Web SDK (compat version):
  - firebase-app-compat  
  - firebase-auth-compat  
  - firebase-firestore-compat  

### Data
- arXiv API (via `arxiv` Python library)  
- Firestore NoSQL Database  

### Infrastructure
- Docker containerization  
- Docker Compose for development  

---

## 📦 Tech Stack

### Backend
- Python 3.11  
- Flask  
- arxiv Python library  
- feedparser (legacy)  
- requests (legacy)

### Frontend
- HTML / CSS  
- Firebase Web SDK (compat)

### Database / Auth
- Firebase Firestore  
- Firebase Authentication  

---

## 🛠 Installation & Run (Docker)

### 1. Clone repository
```bash
git clone <your repo url>
cd bits-insights

docker compose up --build