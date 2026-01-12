# Corner-Pocket Backend 🎱

> ⚠️ **Work in Progress** - This project is under active development. APIs may change, features are incomplete, and dragons may exist. Contributions and feedback welcome!

*Self-hosted pool/billiards match tracking for tournaments, leagues, and friendly games*

An open-source backend for pool players and communities who want to run their own match tracking platform. Host tournaments, organize leagues, track stats, and settle debates about who really won that game.

Built with FastAPI, PostgreSQL, and a love for the game.

## ✨ Features

- **Match Recording** - Log matches with opponent approval (no more disputed results)
- **Multi-Game Support** - 8-ball, 9-ball, and 10-ball tracking
- **Statistics** - Track performance across game types and opponents
- **Self-Hosted** - Run your own instance for your pool hall, league, or friend group
- **API-First** - Clean REST API for building your own clients

## 📱 Client Apps

Corner-Pocket is designed as a platform with multiple client applications:

| Client | Status | Repository |
|--------|--------|------------|
| **Mobile App** (React Native) | 🚧 In Progress | Coming soon |
| **Web App** | 📋 Planned | Coming soon |

The backend provides a complete REST API, so you can also build your own clients!

## 🚧 Project Status

This is an active work-in-progress. Here's what's done and what's coming:

| Feature | Status |
|---------|--------|
| JWT Authentication | ✅ Complete |
| User Registration/Login | ✅ Complete |
| Database Models | ✅ Complete |
| Match Creation | 🚧 In Progress |
| Match Approval Flow | 📋 Planned |
| Statistics API | 📋 Planned |
| Tournament Support | 📋 Planned |
| League Management | 📋 Planned |

## 🛠️ Tech Stack

- **FastAPI** - Modern, fast Python web framework
- **PostgreSQL** - Production-ready database
- **SQLAlchemy + Alembic** - ORM and migrations
- **JWT Authentication** - Secure token-based auth
- **Docker** - Easy deployment
- **Poetry** - Dependency management

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/Mattsface/corner-pocket-backend.git
cd corner-pocket-backend

# Copy environment config
cp .env.example .env

# Start the database
docker compose up -d db

# Install dependencies
poetry install

# Run migrations
poetry run alembic upgrade head

# Start the server
poetry run uvicorn corner_pocket_backend.main:corner_pocket_backend --reload
```

Verify it's running:
```bash
curl http://localhost:8000/health
# {"ok": true}
```

## 📚 Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🐳 Docker Deployment

```bash
docker compose up
```

## 🧪 Running Tests

```bash
poetry run pytest
```

## 🤝 Contributing

Contributions are welcome! This project is in early stages, so there's plenty to do:

- Bug fixes and improvements
- Documentation
- New features
- Testing

### Development Workflow

1. Fork the repo and create a branch (`feat/your-feature`)
2. Make your changes
3. Run linting and tests: `poetry run ruff check . && poetry run pytest`
4. Submit a PR with a clear description

### Branch Naming

- `feat/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code improvements
- `test/` - Tests

## 📋 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `DB_NAME` | Database name | `cornerpocket` |
| `DB_USER` | Database user | `cp` |
| `DB_PASSWORD` | Database password | `changeme` |
| `JWT_SECRET` | Token signing key | `change_this_secret` |
| `CORS_ORIGINS` | Allowed origins | `http://localhost:19006` |

⚠️ **Change `DB_PASSWORD` and `JWT_SECRET` in production!**

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

## 💬 Contact

- **Issues**: [GitHub Issues](https://github.com/Mattsface/corner-pocket-backend/issues)
- **Author**: Matthew Spah

---

*Built with ❤️ for the pool community*
