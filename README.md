# Ghost Net

A simple Flask + Docker project for managing and visualizing your home network devices.

## Features
- Minimal Flask app scaffolded for easy extension
- Ready for Docker deployment
- Persistent data storage in the `data/` directory (excluded from git)
- Static assets (like images) can be placed in `public/images/` (e.g., `ghost_face.png`)

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run locally:**
   ```bash
   python app.py
   ```
   Visit [http://localhost:5000](http://localhost:5000)

3. **Build and run with Docker:**
   ```bash
   docker build -t ghost-net .
   docker run -p 5000:5000 -v $(pwd)/data:/app/data ghost-net
   ```

4. **Add images:**
   Place any images you want to use in `public/images/` (e.g., `ghost_face.png`).

## Version Control
- The `data/` directory is excluded from git to keep your database private and persistent.
- `.env` and other sensitive files are also excluded by default.

## Next Steps
- Add your own routes, templates, and features!
- Use the persistent database for storing network device info or other data.

---

MIT License 