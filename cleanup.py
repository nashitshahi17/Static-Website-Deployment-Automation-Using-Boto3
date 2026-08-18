import argparse
from src.cleanup_manager import CleanupManager
from src.state_manager import StateManager

def main():
    parser = argparse.ArgumentParser(description="Clean up AWS resources")
    parser.add_argument("--delete-s3",action="store_true",help="Delete the S3 bucket and all objects")
    args = parser.parse_args()
    state_manager = StateManager()
    state = state_manager.load()
    cleanup_manager = CleanupManager()
    resources = cleanup_manager.get_resources_from_state(state)
    cleanup_manager.preview_cleanup(resources)
    if args.delete_s3:
        bucket_name = resources.get("bucket_name")
        cleanup_manager.cleanup_s3_bucket(bucket_name)

if __name__ == "__main__":
    main()
