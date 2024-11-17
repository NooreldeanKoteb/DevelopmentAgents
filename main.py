from core.config import (
    get_settings,
    setup_logging,
    initialize_monitoring
)

def main():
    # Initialize core systems
    setup_logging()
    initialize_monitoring()
    
    settings = get_settings()
    
    # Your application logic here
    print(f"Running in {settings.ENVIRONMENT} mode")

if __name__ == "__main__":
    main() 