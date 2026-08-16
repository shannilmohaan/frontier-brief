import os

# Set dummy env vars before any app modules are imported so Settings() doesn't fail at test collection time
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/testdb")
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-key-for-tests")
os.environ.setdefault("YOUTUBE_API_KEY", "test-youtube-api-key")
os.environ.setdefault("REFRESH_KEY", "test-refresh-secret-key")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")
