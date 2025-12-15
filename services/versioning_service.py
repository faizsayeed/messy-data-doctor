import os
import pandas as pd
from datetime import datetime

def save_new_version(df, filename, action, base_dir):
    """
    Save cleaned dataset as a new version.
    """

    os.makedirs(base_dir, exist_ok=True)

    # Save latest cleaned version (used for compare)
    latest_path = os.path.join(base_dir, filename)
    df.to_csv(latest_path, index=False)

    # Also save timestamped version (for history)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(filename)
    versioned_name = f"{name}_{timestamp}{ext}"

    versioned_path = os.path.join(base_dir, versioned_name)
    df.to_csv(versioned_path, index=False)


def get_versions(filename):
    """
    List all saved versions for a dataset.
    """
    name, _ = os.path.splitext(filename)

    versions = []
    base_dir = os.path.join(os.path.dirname(__file__), "..", "storage", "versions")

    if not os.path.exists(base_dir):
        return versions

    for f in os.listdir(base_dir):
        if f.startswith(name + "_"):
            versions.append(f)

    versions.sort(reverse=True)
    return versions


def load_version(filename, version, base_dir):
    """
    Load a specific version by index.
    """
    versions = get_versions(filename)

    if version < 0 or version >= len(versions):
        return None

    path = os.path.join(base_dir, versions[version])
    return pd.read_csv(path)
