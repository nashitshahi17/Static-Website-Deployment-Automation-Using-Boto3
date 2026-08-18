import argparse
from src.cleanup_manager import CleanupManager
from src.state_manager import StateManager

def main():
    parser = argparse.ArgumentParser(description="Clean up AWS resources")
    parser.add_argument("--delete-s3",action="store_true",help="Delete the S3 bucket and all objects")
    parser.add_argument("--execute",action="store_true",help="Execute the cleanup and delete AWS resources.")
    args = parser.parse_args()
    state_manager = StateManager()
    state = state_manager.load()
    cleanup_manager = CleanupManager()
    resources = cleanup_manager.get_resources_from_state(state)
    if args.execute:
        print("\nWARNING: This will delete AWS resources created by this project.")
        confirmation = input("Type 'DELETE' to continue: ")
    if confirmation != "DELETE":
        print("Cleanup cancelled.")
        return
    cleanup_manager.cleanup_all()
    # cleanup_manager.preview_cleanup(resources)
    # if args.delete_s3:
    #     bucket_name = resources.get("bucket_name")
    #     cleanup_manager.cleanup_s3_bucket(bucket_name)

if __name__ == "__main__":
    main()
