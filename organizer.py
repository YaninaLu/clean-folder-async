import asyncio
from sys import argv
import os
import aioshutil
from pathlib import Path
from transliteration import normalize_name


IMAGES = (".jpeg", ".png", ".jpg", ".svg", ".bmp", ".heic")
VIDEOS = (".avi", ".mp4", ".mov", ".mkv")
DOCS = (".doc", ".docx", ".txt", ".pdf", ".xls", ".pptx", ".xlsx")
AUDIO = (".mp3", ".ogg", ".wav", ".amr")
ARCHIVES = (".zip", ".gz", ".tar", ".tar.gz")

IMAGE_DIR = "images"
AUDIO_DIR = "audio"
VIDEO_DIR = "video"
DOCUMENTS_DIR = "documents"
ARCHIVES_DIR = "archives"

ignored_folders = [IMAGE_DIR, VIDEO_DIR, DOCUMENTS_DIR, AUDIO_DIR, ARCHIVES_DIR]


async def move_file(f: str, path: str, folder_name: str) -> None:
    """
    Moves the given file into corresponding folder depending on the file extension.
    :param f: path to the file
    :param path: path to the directory where the file is
    :param folder_name: name of a folder to move the file to
    """
    new_path = os.path.join(path, folder_name)
    if os.path.exists(new_path):
        await aioshutil.move(f, os.path.join(new_path, os.path.basename(f)))
    else:
        os.mkdir(os.path.join(path, folder_name))
        await aioshutil.move(f, os.path.join(new_path, os.path.basename(f)))


async def move_archive(f: str, path: str) -> None:
    """
    Moves the archive to the "archives" directory, unpacks it into the folder and deletes the original archive.
    :param f: path to the archive
    :param path: path to the directory where the file is
    """
    new_path = os.path.join(path, ARCHIVES_DIR)
    if os.path.exists(new_path):
        new_addr = os.path.join(new_path, os.path.basename(f))
        await aioshutil.move(f, new_addr)
        await aioshutil.unpack_archive(new_addr, os.path.join(new_addr, os.path.splitext(new_addr)[0]))
        os.remove(new_addr)
    else:
        os.mkdir(os.path.join(path, ARCHIVES_DIR))
        new_addr = os.path.join(new_path, os.path.basename(f))
        await aioshutil.move(f, new_addr)
        await aioshutil.unpack_archive(new_addr, os.path.join(new_addr, os.path.splitext(new_addr)[0]))
        os.remove(new_addr)


def is_empty_dir(directory: str) -> bool:
    """
    Checks if the directory is empty.
    :param directory: path to the directory
    :return: True if the directory is empty, False otherwise
    """
    return len(os.listdir(directory)) == 0


async def sort_file(subfolders: asyncio.Queue) -> None:
    """
    Traverses the given folder, deletes it if empty, sorts the files in it according to their extensions.
    :param subfolders: a queue of folders to process
    """
    while True:
        path = await subfolders.get()

        for filename in os.listdir(path):
            f = os.path.join(path, filename)
            if os.path.isdir(f):
                if filename in ignored_folders:
                    continue
                if is_empty_dir(f):
                    os.rmdir(f)
            else:
                new_path = os.path.join(path, normalize_name(f))
                if not os.path.exists(new_path):
                    os.rename(f, new_path)
                extension = Path(new_path).suffix.lower()

                if extension in IMAGES:
                    await move_file(new_path, path, IMAGE_DIR)
                elif extension in VIDEOS:
                    await move_file(new_path, path, VIDEO_DIR)
                elif extension in DOCS:
                    await move_file(new_path, path, DOCUMENTS_DIR)
                elif extension in AUDIO:
                    await move_file(new_path, path, AUDIO_DIR)
                elif extension in ARCHIVES:
                    await move_archive(new_path, path)

        subfolders.task_done()


async def find_subfolders(path: str, subfolders: asyncio.Queue):
    """
    Traverses the target folder and finds all the subfolders.
    :param subfolders: a queue to store found subfolders
    :param path: path to the target folder
    :return: list of paths to the subfolders of the target folder
    """
    for folder in os.walk(path):
        if folder[0].split(os.path.sep)[-1] not in ignored_folders:
            await subfolders.put(folder[0])


async def sort_folder():
    """
    Takes subfolders of the target folder and sorts them in different threads.
    """
    if len(argv) != 2:
        print("You have to specify the path to the directory to organize.")
        quit()

    path = argv[1]
    subfolders = asyncio.Queue()
    await find_subfolders(path, subfolders)

    sorters = [asyncio.create_task(sort_file(subfolders)) for _ in range(subfolders.qsize())]
    await subfolders.join()

    for sorter in sorters:
        sorter.cancel()


if __name__ == "__main__":
    asyncio.run(sort_folder())
