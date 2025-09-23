# Corner-Pocket Backend 🎱
*"Because tracking your pool losses should be as smooth as your bad break shots"*

The backend that powers Corner-Pocket - where pool players come to argue about whether that was really a legal shot, and the code actually works (unlike your 8-ball skills).

Built with FastAPI because we like our APIs fast (and simple for now), and our excuses for missing shots even faster.

## What's This Thing Do? 🤔

Corner-Pocket is a social app for pool players who want to:
- Record matches and make opponents approve them (no more "I totally won that game")
- Track stats across 8-ball, 9-ball, and 10-ball (prepare for humbling insights)
- Connect with friends and schedule games (then actually show up this time)
- Settle disputes with immutable match records (blockchain for bar arguments)

## The Stack 🛠️
*"We use the good stuff so you don't have to suffer"*

- **FastAPI** - Because life's too short for slow APIs
- **PostgreSQL** - Real database for real data (coming soon™)
- **SQLAlchemy + Alembic** - ORM and migrations that don't make you cry
- **JWT Authentication** - Proper security, not security theater
- **Docker** - Containers that actually work
- **Poetry** - Dependency management for adults

## Get This Thing Running 🚀
*"Easier than sinking the 8-ball on the break (and way less controversial)"*

### The "I Just Want It to Work" Approach

```bash
# Clone and enter the danger zone
gh repo clone https://github.com/Mattsface/corner-pocket-backend.git

# OR the old school way: git clone https://github.com/Mattsface/corner-pocket-backend.git
cd corner-pocket-backend

# Copy the env file (don't skip this, trust us)
cp .env.example .env

# Fire up the database (PostgreSQL goes brrr)
docker compose up -d db

# Install dependencies like a civilized person
poetry install

# Run migrations (currently none, but good habits)
poetry run alembic upgrade head

# Start the server
poetry run uvicorn corner_pocket_backend.main:corner_pocket_backend --reload
```

**Moment of truth:**
```bash
curl http://localhost:8000/health
# Should return {"ok": true} - if not, something's already sideways
```

If that worked, congrats! You're ahead of 73% of developers who skip the README.

### The Docker Way (For the Lazy)

```bash
# Build the image (grab a coffee)
docker build -t corner-pocket-backend .

# Run it (with env file because we're not animals)
docker run -p 8000:8000 --env-file .env corner-pocket-backend

# Or use compose like a pro
docker compose up
```

## Dev Setup 💻
*"Don't mess this up (but if you do, here's how to fix it)"*

### Prerequisites
- Python 3.12+ (because we live in the future)
- Poetry (install from https://python-poetry.org)
- Docker & Docker Compose (for the database and deployment)
- GitHub CLI (optional but awesome): https://cli.github.com/

### Development Dependencies
```bash
# Install everything including the good stuff
poetry install --with dev

# Lint your code (because standards matter)
poetry run ruff check .

# Type checking (catch bugs before they catch you)
poetry run mypy corner_pocket_backend

# Run tests (when we have some)
poetry run pytest
```

### Environment Setup
Copy `.env.example` to `.env` and adjust the values:

| Variable | What It Does | Default | Don't Mess With This |
|----------|--------------|---------|---------------------|
| `ENV` | Environment name | `dev` | Unless you know what you're doing |
| `DB_HOST` | Database host | `localhost` | - |
| `DB_PORT` | Database port | `5432` | - |
| `DB_NAME` | Database name | `cornerpocket` | - |
| `DB_USER` | Database user | `cp` | - |
| `DB_PASSWORD` | Database password | `changeme` | **Yes, change this** |
| `JWT_SECRET` | Token signing key | `change_this_secret` | **Seriously, change this** |
| `CORS_ORIGINS` | Allowed origins | `http://localhost:19006,http://localhost:8081` | Add your frontend URLs |

## API Docs 📡
*"The digital equivalent of calling your shots"*

### Auto-Generated Docs
- **Swagger UI**: http://localhost:8000/docs (the pretty one)
- **ReDoc**: http://localhost:8000/redoc (the boring one)

### Auth Flow (Because We're Not Animals)

**1. Register a new player**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "shark@poolhall.com",
    "handle": "8ballwiz", 
    "display_name": "Minnesota Fats Jr",
    "password": "not123456"
  }'
```

**2. Login and get your golden ticket**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "shark@poolhall.com",
    "password": "not123456"
  }'

# Returns: {"access_token": "eyJ...", "token_type": "bearer"}
```

**3. Use that token for protected stuff**
```bash
# Get your profile
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/api/v1/me

# Create a match
curl -X POST http://localhost:8000/api/v1/matches \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H 'Content-Type: application/json' \
  -d '{
    "opponent_id": "some-uuid",
    "game_type": "EIGHT_BALL",
    "race_to": 5
  }'
```

## Database Stuff 💾
*"Where we keep track of your embarrassing losses"*

### Current State
Right now we're using in-memory stubs (fancy way of saying "fake data that disappears"). This is fine for development but probably not what you want for tracking your epic comeback victories.

### File Structure
```
corner_pocket_backend/
├── main.py                 # FastAPI app factory
├── api/v1/                 # REST endpoints
│   ├── auth.py            # Login/logout/JWT magic
│   ├── matches.py         # Match creation and approval
│   └── stats.py           # Performance tracking
├── core/                  # Config and security
│   ├── config.py          # Environment settings
│   └── security.py        # JWT handling
├── models/                # Database models (coming soon™)
├── schemas/               # Pydantic request/response models
└── services/              # Business logic layer
    ├── users.py           # User management (stub)
    ├── matches.py         # Match logic (stub)
    └── stats.py           # Statistics (stub)
```

### Future Database Plans
- PostgreSQL for real data persistence
- SQLAlchemy models for Users, Matches, Games, Friendships
- Alembic migrations for schema changes
- Proper foreign keys and constraints (revolutionary!)

## Testing 🧪
*"Because breaking things in prod is expensive"*

```bash
# Run all tests (when we have some)
poetry run pytest

# Run with coverage (for the overachievers)
poetry run pytest --cov=corner_pocket_backend

# Run specific test file
poetry run pytest tests/test_auth.py

# Run and watch for changes (development mode)
poetry run pytest --watch
```

### Current Test Coverage
- Health endpoint ✅
- Auth flow (coming soon™)
- Match creation (on the roadmap)
- Stats calculation (eventually)

## Deployment 🚀
*"Ship it like you're running the table"*

### Docker Production Build
```bash
# Build for production (no cache, no mercy)
docker build --no-cache -t corner-pocket-backend .

# Run with proper env
docker run -p 8000:8000 --env-file .env.production corner-pocket-backend
```

### Environment Variables for Production
Don't use the defaults in production unless you want to get hacked faster than a tourist at a pool hall:

- `JWT_SECRET` - Generate a real secret (use `openssl rand -hex 32`)
- `DB_PASSWORD` - Use a real password, not "changeme"
- `CORS_ORIGINS` - Set to your actual frontend domains
- `ENV` - Set to "production" for production logging

## When Things Go Sideways 🔧
*"Like when you scratch on the 8-ball, but fixable"*

### Common Issues

**"Docker won't start"**
- Try turning it off and on again: `docker system prune`
- Check if something's hogging port 8000: `lsof -i :8000`
- Make sure Docker Desktop is actually running (classic mistake)

**"Poetry is being difficult"**
- Clear the environment: `poetry env remove python && poetry install`
- Update Poetry: `pip install --upgrade poetry`
- When in doubt, delete `.venv/` and start over

**"Database connection fails"**
- Is PostgreSQL running? `docker compose ps`
- Check your `.env` file exists and has the right values
- Try connecting manually: `psql -h localhost -U cp -d cornerpocket`

**"Import errors everywhere"**
- Make sure you're in the Poetry shell: `poetry shell`
- Check all `__init__.py` files exist
- Restart your editor (seriously, sometimes it helps)

**"JWT tokens don't work"**
- Check your `JWT_SECRET` is set and consistent
- Make sure you're sending the header: `Authorization: Bearer <token>`
- Token might be expired (they last 24 hours by default)

## Contributing 🤝
*"Help us make this thing less terrible"*

### Code Style
- We use `ruff` for linting (because it's fast and opinionated)
- Type hints everywhere (mypy will yell at you if you don't)
- Comments should be helpful, not just restatements of the code
- If you write something clever, explain it so future you doesn't hate present you

### Development Workflow
1. Branch off `main` with a descriptive name (`feat/match-approval-flow`)
2. Make your changes (try not to break everything)
3. Run the linter and tests (`poetry run ruff check . && poetry run pytest`)
4. Commit with a message that explains what you did and why
5. Push and create a PR (include context, not just "fix bug")

### Branch Naming
- `feat/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code improvements that don't change behavior
- `test/` - Adding or updating tests

Don't break the build or you're buying the next round! 🍺

## What's Next 🎯
*"Because this is just the opening break"*

### Immediate Roadmap (The Next Rack)
- **Real Database**: Ditch the in-memory stubs and get Postgres + Alembic running
- **Mobile App**: Wire up the React Native frontend so you can actually use this thing
- **Friends System**: Add/connect with other players (pool is better with witnesses)
- **Match Approval Flow**: Build the "did you really sink that shot?" verification system

### Coming Soon™ (The Tournament Dreams)
- **Push Notifications**: Get pinged when someone challenges your questionable skills
- **Advanced Stats**: Track performance across game types (prepare for reality checks)
- **Planned Matches**: Schedule games and actually show up this time
- **Web Client**: For when you want to argue about match results from your desktop

### The Long Game (Hall of Fame Status)
- **League Integration**: Connect with local pool leagues and tournaments
- **Location Features**: Find games and players near you
- **Live Scoring**: Real-time match updates for maximum drama
- **Social Wagering**: Betting pools on matches (where legal, obviously)

---

## License 📜
*"The legal stuff nobody reads"*

[Add your license here - MIT is popular and reasonable]

## Support 💬
*"When you need help or want to complain"*

- **Issues**: [GitHub Issues](link-to-issues) - Bug reports and feature requests
- **Discussions**: [GitHub Discussions](link-to-discussions) - Questions and general chat
- **Email**: [your-email] - For private stuff or security issues

---

*Built with ❤️ and probably too much caffeine by me who take pool way too seriously and spends way too much time doing it.*