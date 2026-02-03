# AlsunSeniors

## Local development

### Backend (Flask)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```
If you previously ran the app before the `external_id` column was added, delete `alsun.db` so the schema can rebuild.

### Frontend
Open `http://localhost:5000/index.html` after the server starts so the frontend can reach the API.

### Admin login (demo)
* Username: `admin`
* Password: `admin`

The admin tools remain hidden until a successful login.

## Facebook integration notes
* Upload a cookies file in the admin portal and supply the course ID to associate it with a course.
* The backend stores a cursor per course so future scrapes can be incremental (full-history sync only on first run).
* Scheduling for midnight syncs will be added once the hosting environment is ready (cron/queue).
* Set `FBSCRAPE_CMD` to a command that runs the FBScrapeIdeas script and writes JSON to `FB_OUTPUT_PATH`.
  * Example: `FBSCRAPE_CMD="python /path/to/FBScrapeIdeas/main.py"` (adapt the script to read env vars).
* If you clone `FBScrapeIdeas` into `integrations/FBScrapeIdeas`, the backend will auto-detect `main.py` without `FBSCRAPE_CMD`.
