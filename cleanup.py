from src.cleanup_manager import CleanupManager
from src.state_manager import StateManager

def main():
    state_manager = StateManager()
    state = state_manager.load()
    cleanup_manager = CleanupManager()
    resources = cleanup_manager.get_resources_from_state(state)
    cleanup_manager.preview_cleanup(resources)

if __name__ == "__main__":
    main()
