# Blueprint CAD Designer — Quickstart

This folder contains a minimal scaffold for a Django-backed Blueprint/CAD designer and a small React frontend.

Prerequisites
- Python 3.10+ virtualenv
- Node.js and npm (for the frontend)

Quick setup
1. Create and activate virtualenv, then install Python deps:

   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt

2. Run Django migrations, seed demo data, and start server:

   python cadsite/manage.py migrate
   python cadsite/manage.py seed_demo
   python cadsite/manage.py unpack_realtinytalk  # optional: extracts archived realTinyTalk into frontend static
   python cadsite/manage.py runserver 8000

3. Start frontend dev server (optional):

   cd frontend/blueprint
   npm install
   npm start

Notes
- The frontend is a minimal React skeleton; it hits `/api/floorplans/svg_preview/` to show an SVG preview.
- There is an archived `realTinyTalk` IDE in `_archive/realtinytalk_old` — the file `public/realtinytalk.html` is a stub that points to the archive.
- Export functionality and geometry operations (shapely / ezdxf) will be added in the next iteration.
