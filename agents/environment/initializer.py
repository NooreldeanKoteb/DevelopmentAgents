import asyncio
import os
import subprocess
from pathlib import Path
from typing import List, Dict

class ProjectInitializer:
    """Handles project initialization and structure setup."""

    def __init__(self, root_dir: str = None):
        self.root_dir = Path(root_dir) if root_dir else Path.cwd()
        self.env_template = {
            "OPENAI_API_KEY": "",
            "REDIS_URL": "redis://localhost:6379",
            "ENVIRONMENT": "development",
            "LOG_LEVEL": "INFO",
            "VECTOR_DB_PATH": "./data/vector_store",
            "MAX_TOKENS": "2000",
            "RATE_LIMIT": "50",
        }

    async def initialize_project(self) -> bool:
        """Main initialization method."""
        try:
            print("Starting project initialization...")
            
            # Create project structure
            await self._create_project_structure()
            
            # Initialize Git
            await self._init_git()
            
            # Setup Poetry
            await self._setup_poetry()
            
            # Create environment files
            await self._create_env_files()
            
            # Setup Docker
            await self._setup_docker()
            
            print("Project initialization completed successfully!")
            return True
            
        except Exception as e:
            print(f"Error during project initialization: {str(e)}")
            return False

    async def _create_project_structure(self):
        """Create the project directory structure."""
        directories = [
            "agents/base",
            "agents/project_manager",
            "agents/knowledge",
            "agents/coding",
            "agents/testing",
            "agents/environment",
            "agents/security",
            "agents/documentation",
            "core/config",
            "core/messaging",
            "core/storage",
            "core/monitoring",
            "core/utils",
            "prompts/code",
            "prompts/search",
            "prompts/analysis",
            "prompts/testing",
            "tests/unit",
            "tests/integration",
            "tests/e2e",
            "docs/architecture",
            "docs/api",
            "docs/guides",
        ]

        print("Creating project structure...")
        for dir_path in directories:
            full_path = self.root_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            init_file = full_path / "__init__.py"
            init_file.touch(exist_ok=True)

    async def _init_git(self):
        """Initialize Git repository and create .gitignore."""
        print("Initializing Git repository...")
        
        # Initialize Git if not already initialized
        if not (self.root_dir / ".git").exists():
            process = await asyncio.create_subprocess_shell(
                "git init",
                cwd=str(self.root_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            await process.communicate()

        # Create .gitignore
        gitignore_content = """
.env
.env.*
!.env.example
__pycache__/
*.py[cod]
*$py.class
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
.coverage
htmlcov/
.DS_Store
.idea/
.vscode/
*.swp
*.swo
data/vector_store/
"""
        with open(self.root_dir / ".gitignore", "w") as f:
            f.write(gitignore_content.strip())

    async def _setup_poetry(self):
        """Initialize and configure Poetry."""
        print("Setting up Poetry...")
        
        if not (self.root_dir / "pyproject.toml").exists():
            process = await asyncio.create_subprocess_shell(
                "poetry init --name autonomous-ai-dev --description 'Autonomous AI Development System' --author 'AI Team' --python '^3.11' --dependency langchain --dependency openai --dependency pydantic --dependency redis --dependency chromadb --no-interaction",
                cwd=str(self.root_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            await process.communicate()

    async def _create_env_files(self):
        """Create environment files."""
        print("Creating environment files...")
        
        # Create .env.example
        env_example = "\n".join([f"{k}={v}" for k, v in self.env_template.items()])
        with open(self.root_dir / ".env.example", "w") as f:
            f.write(env_example)
        
        # Create .env if it doesn't exist
        env_file = self.root_dir / ".env"
        if not env_file.exists():
            with open(env_file, "w") as f:
                f.write(env_example)
            print("Created .env file. Please update with your actual values.")

    async def _setup_docker(self):
        """Create Docker configuration files."""
        print("Setting up Docker configuration...")
        
        # Create Dockerfile
        dockerfile_content = """
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy project files
COPY pyproject.toml poetry.lock* ./
COPY . .

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

CMD ["poetry", "run", "python", "-m", "agents.environment.setup"]
"""
        with open(self.root_dir / "Dockerfile", "w") as f:
            f.write(dockerfile_content.strip())

        # Create docker-compose.yml
        docker_compose_content = """
version: '3.8'

services:
  app:
    build: .
    volumes:
      - .:/app
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  redis:
    image: redis:latest
    ports:
      - "6379:6379"
"""
        with open(self.root_dir / "docker-compose.yml", "w") as f:
            f.write(docker_compose_content.strip())

async def main():
    """Entry point for project initialization."""
    initializer = ProjectInitializer()
    success = await initializer.initialize_project()
    if success:
        print("\nNext steps:")
        print("1. Update .env file with your OpenAI API key and other credentials")
        print("2. Run 'poetry install' to install dependencies")
        print("3. Run 'docker-compose up' to start the services")
    return 0 if success else 1

if __name__ == "__main__":
    asyncio.run(main()) 