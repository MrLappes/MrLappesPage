# PlatePal Shared Markdown Editor

A real-time collaborative markdown editor with authentication, built with Vue.js and FastAPI.

## Features

- 🔐 **User Authentication** - JSON-based user credentials
- 📝 **Real-time Collaboration** - Multiple users can edit simultaneously using WebSockets
- 🖼️ **Image Upload** - Upload and embed images in markdown
- 👁️ **Live Preview** - See rendered markdown in real-time
- 💾 **Auto-save** - Changes are automatically saved
- 📥 **Export** - Download documents as .md files
- 🎨 **Dark Mode Support** - Matches the main site theme

## Setup

### Backend Setup

1. Navigate to the backend directory:
```bash
cd sm-backend
```

2. Create a virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Configure users in `users.json`:
```json
[
  {
    "username": "admin",
    "identifier": "admin123"
  },
  {
    "username": "user1",
    "identifier": "pass123"
  }
]
```

4. Start the backend server:
```bash
python main.py
```

Backend runs on: `http://localhost:8001`

### Frontend Setup

1. Navigate to the website directory:
```bash
cd platepal-website
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

Frontend runs on: `http://localhost:5173`

## Usage

1. Open your browser and navigate to `http://localhost:5173/login`
2. Login with credentials from `users.json`
3. You'll be redirected to `/sm` (Shared Markdown editor)
4. Create a new document or select an existing one
5. Start typing markdown in the editor
6. See the live preview on the right
7. Upload images using the "Upload Image" button
8. Download your document using the "Download" button

## Architecture

### Frontend (Vue.js)
- **Login.vue** - Authentication page
- **SharedMarkdown.vue** - Main editor interface
- Real-time updates via WebSocket
- Markdown rendering with `marked` library
- Styled with Tailwind CSS and @tailwindcss/typography

### Backend (FastAPI)
- RESTful API for document management
- WebSocket for real-time collaboration
- SQLite database for persistence
- Token-based authentication
- Image storage as BLOBs in database

### Database Schema

**documents**
- id (PRIMARY KEY)
- name (UNIQUE)
- content (TEXT)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

**images**
- id (PRIMARY KEY)
- filename (TEXT)
- data (BLOB)
- document_id (FOREIGN KEY)
- uploaded_at (TIMESTAMP)

**sessions**
- token (PRIMARY KEY)
- username (TEXT)
- created_at (TIMESTAMP)
- expires_at (TIMESTAMP)

## Security Notes

- Sessions expire after 7 days
- Tokens are stored in localStorage
- All API endpoints (except login) require authentication
- WebSocket connections are authenticated
- CORS is configured for localhost (update for production)

## Production Deployment

1. Update CORS origins in `sm-backend/main.py`
2. Use environment variables for configuration
3. Set up a reverse proxy (nginx/traefik)
4. Use a production ASGI server like Gunicorn with Uvicorn workers
5. Consider using PostgreSQL instead of SQLite
6. Implement rate limiting
7. Add HTTPS
8. Secure user credentials (use proper password hashing)

## API Endpoints

See [sm-backend/README.md](sm-backend/README.md) for detailed API documentation.

## Development

Both servers support hot-reload during development:
- Frontend: Vite HMR
- Backend: Uvicorn auto-reload (add `--reload` flag)

## Troubleshooting

**Port already in use:**
- Backend: Change port in `main.py` (line with `uvicorn.run`)
- Frontend: Set port in `vite.config.js` or use `--port` flag

**WebSocket connection failed:**
- Ensure backend is running
- Check browser console for errors
- Verify token is valid

**Authentication failed:**
- Check credentials in `users.json`
- Clear localStorage and try again
- Check backend logs

## License

MIT
