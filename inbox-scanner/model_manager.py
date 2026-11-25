from pathlib import Path
from huggingface_hub import hf_hub_download

MODELS_DIR = Path("models")

# Curated catalog of ready-to-use .litertlm bundles
RECOMMENDED_MODELS = {
    "1": {
        "name": "Gemma 4 E2B Instruct (Fast, balanced)",
        "repo_id": "litert-community/gemma-4-E2B-it-litert-lm",
        "filename": "gemma-4-E2B-it.litertlm",
    },
}

def find_local_models() -> list[Path]:
    """Finds all .litertlm files in ./models and ~/.litert-lm/models."""
    search_dirs = [MODELS_DIR, Path.home() / ".litert-lm" / "models"]
    found = []
    for directory in search_dirs:
        if directory.exists():
            found.extend(directory.rglob("*.litertlm"))
    return sorted(set(found))

def download_model(repo_id: str, filename: str, target_dir: Path = MODELS_DIR) -> Path:
    """Downloads a .litertlm model file from Hugging Face into the local models folder."""
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {filename} from {repo_id}... (this may take a few minutes)")
    downloaded_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=str(target_dir),
    )
    print(f"Model saved to: {downloaded_path}")
    return Path(downloaded_path)

def resolve_model_interactive() -> Path:
    """CLI helper allowing the user to pick an existing model, provide a path, or download one."""
    local_models = find_local_models()

    print("\n=== Model Selection ===")
    if local_models:
        print("Existing local models found:")
        for idx, path in enumerate(local_models, 1):
            print(f"  [{idx}] {path}")
    else:
        print("No local .litertlm models found yet.")

    print("\nOptions:")
    print("  [D] Download a recommended model from Hugging Face")
    print("  [C] Enter a custom path to an existing .litertlm file")
    if local_models:
        print(f"  [1-{len(local_models)}] Select one of the existing local models above")

    choice = input("\nChoose an option: ").strip()

    # Select from discovered local models
    if choice.isdigit() and 1 <= int(choice) <= len(local_models):
        return local_models[int(choice) - 1]

    # Use a custom path anywhere on disk
    if choice.lower() == "c":
        custom_path = Path(input("Enter full path to .litertlm file: ").strip().strip('"'))
        if custom_path.is_file() and custom_path.suffix == ".litertlm":
            return custom_path
        raise FileNotFoundError(f"Valid .litertlm file not found at: {custom_path}")

    # Download from Hugging Face
    if choice.lower() == "d":
        print("\nAvailable models to download:")
        for key, info in RECOMMENDED_MODELS.items():
            print(f"  [{key}] {info['name']} ({info['repo_id']})")
        print("  [H] Enter a custom Hugging Face repo_id and filename")

        dl_choice = input("Select model to download: ").strip()
        if dl_choice in RECOMMENDED_MODELS:
            selected = RECOMMENDED_MODELS[dl_choice]
            return download_model(selected["repo_id"], selected["filename"])
        elif dl_choice.lower() == "h":
            repo = input("Hugging Face repo_id (e.g. litert-community/gemma-4-E2B-it-litert-lm): ").strip()
            fname = input("Filename (e.g. gemma-4-E2B-it.litertlm): ").strip()
            return download_model(repo, fname)

    raise ValueError("Invalid selection.")