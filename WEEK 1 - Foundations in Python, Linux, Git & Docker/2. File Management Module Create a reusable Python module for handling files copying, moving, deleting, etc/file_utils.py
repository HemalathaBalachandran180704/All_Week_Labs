# file_utils.py
import os
import shutil
from pathlib import Path


def copy_file(src: str, dest: str, overwrite: bool = False) -> None:
    """Copy a file from src to dest."""
    src_path, dest_path = Path(src), Path(dest)
    if not src_path.is_file():
        raise FileNotFoundError(f"Source file not found: {src}")
    if dest_path.exists() and not overwrite:
        raise FileExistsError(f"Destination already exists: {dest}")
    shutil.copy2(src_path, dest_path)


def move_file(src: str, dest: str, overwrite: bool = False) -> None:
    """Move a file from src to dest."""
    src_path, dest_path = Path(src), Path(dest)
    if not src_path.is_file():
        raise FileNotFoundError(f"Source file not found: {src}")
    if dest_path.exists() and not overwrite:
        raise FileExistsError(f"Destination already exists: {dest}")
    shutil.move(str(src_path), str(dest_path))


def delete_file(path: str) -> None:
    """Delete a file."""
    file_path = Path(path)
    if file_path.is_file():
        file_path.unlink()
    else:
        raise FileNotFoundError(f"File not found: {path}")


def rename_file(src: str, new_name: str) -> None:
    """Rename a file (keeps same directory)."""
    src_path = Path(src)
    if not src_path.is_file():
        raise FileNotFoundError(f"File not found: {src}")
    new_path = src_path.with_name(new_name)
    src_path.rename(new_path)


def list_files(directory: str, extension: str = None) -> list[str]:
    """List all files in a directory. Optionally filter by extension."""
    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")
    if extension:
        return [str(f) for f in dir_path.glob(f"*.{extension.lstrip('.')}")]
    return [str(f) for f in dir_path.iterdir() if f.is_file()]


def copy_folder(src: str, dest: str, overwrite: bool = False) -> None:
    """Copy a whole folder."""
    src_path, dest_path = Path(src), Path(dest)
    if not src_path.is_dir():
        raise NotADirectoryError(f"Source folder not found: {src}")
    if dest_path.exists():
        if overwrite:
            shutil.rmtree(dest_path)
        else:
            raise FileExistsError(f"Destination already exists: {dest}")
    shutil.copytree(src_path, dest_path)


def delete_folder(path: str) -> None:
    """Delete a folder and its contents."""
    folder_path = Path(path)
    if folder_path.is_dir():
        shutil.rmtree(folder_path)
    else:
        raise NotADirectoryError(f"Folder not found: {path}")
