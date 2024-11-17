import asyncio
import subprocess
import sys
from pathlib import Path
from typing import List, Dict

class EnvironmentSetup:
    """Handles environment setup and validation for the AI Development System."""
    
    REQUIRED_PYTHON_VERSION = (3, 11)
    REQUIRED_TOOLS = {
        "git": "Git is required for version control",
        "docker": "Docker is required for containerization",
        "poetry": "Poetry is required for dependency management"
    }

    async def setup_environment(self) -> bool:
        """Main setup method that orchestrates the environment configuration."""
        try:
            print("Starting environment setup...")
            
            # Validate Python version
            if not self._check_python_version():
                return False

            # Check required tools
            if not await self._verify_tools():
                return False

            # Setup Docker permissions
            if not await self._setup_docker_permissions():
                print("Please log out and log back in for Docker permissions to take effect")
                return False

            # Create virtual environment and install dependencies
            if not await self._setup_poetry_env():
                return False

            # Setup Docker configuration
            if not await self._setup_docker_config():
                return False

            print("Environment setup completed successfully!")
            return True

        except Exception as e:
            print(f"Error during environment setup: {str(e)}")
            return False

    def _check_python_version(self) -> bool:
        """Verify Python version meets requirements."""
        current_version = sys.version_info[:2]
        if current_version < self.REQUIRED_PYTHON_VERSION:
            print(f"Python {'.'.join(map(str, self.REQUIRED_PYTHON_VERSION))} or higher is required")
            return False
        return True

    async def _verify_tools(self) -> bool:
        """Verify all required tools are installed."""
        for tool, message in self.REQUIRED_TOOLS.items():
            if not await self._check_tool_installed(tool):
                print(f"Missing requirement: {message}")
                print(f"Please install {tool} before continuing")
                return False
        return True

    async def _check_tool_installed(self, tool: str) -> bool:
        """Check if a specific tool is installed."""
        try:
            process = await asyncio.create_subprocess_exec(
                "which", tool,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            await process.communicate()
            return process.returncode == 0
        except Exception:
            return False

    async def _setup_docker_permissions(self) -> bool:
        """Ensure current user has Docker permissions."""
        try:
            # Check if user is in docker group
            process = await asyncio.create_subprocess_shell(
                "groups $USER | grep docker",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            
            if not stdout:
                print("Adding user to docker group...")
                process = await asyncio.create_subprocess_shell(
                    "sudo usermod -aG docker $USER",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                await process.communicate()
                print("User added to docker group. Please log out and log back in for changes to take effect.")
                return False
            return True

        except Exception as e:
            print(f"Error setting up Docker permissions: {str(e)}")
            return False

    async def _setup_poetry_env(self) -> bool:
        """Set up Poetry virtual environment and install dependencies."""
        try:
            # Initialize poetry project if not already initialized
            if not Path("pyproject.toml").exists():
                print("Initializing new Poetry project...")
                process = await asyncio.create_subprocess_shell(
                    "poetry init --name autonomous-ai-dev --description 'Autonomous AI Development System' "
                    "--author 'AI Team' --python '^3.11' --no-interaction",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                await process.communicate()

            # Install dependencies
            print("Installing project dependencies...")
            dependencies = [
                "langchain",
                "openai",
                "pydantic",
                "redis",
                "chromadb",
                "pytest-asyncio",
                "black",
                "ruff",
                "mypy",
                "sphinx",
                "prometheus-client"
            ]
            
            for dep in dependencies:
                process = await asyncio.create_subprocess_shell(
                    f"poetry add {dep}",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                await process.communicate()

            return True

        except Exception as e:
            print(f"Error setting up Poetry environment: {str(e)}")
            return False

    async def _setup_docker_config(self) -> bool:
        """Create Docker configuration files."""
        try:
            # Create Dockerfile
            dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false \\
    && poetry install --no-interaction --no-ansi

COPY . .

CMD ["poetry", "run", "python", "-m", "agents.environment.setup"]
"""
            with open("Dockerfile", "w") as f:
                f.write(dockerfile_content)

            # Create docker-compose.yml
            compose_content = """services:
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
    volumes:
      - redis_data:/data

volumes:
  redis_data:
"""
            with open("docker-compose.yml", "w") as f:
                f.write(compose_content)

            return True

        except Exception as e:
            print(f"Error setting up Docker configuration: {str(e)}")
            return False

async def main():
    """Entry point for environment setup."""
    setup = EnvironmentSetup()
    success = await setup.setup_environment()
    
    if success:
        print("\nNext steps:")
        print("1. Log out and log back in if Docker permissions were updated")
        print("2. Activate the virtual environment with: poetry shell")
        print("3. Start the services with: docker compose up -d")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main()) 