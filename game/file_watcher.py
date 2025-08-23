# game/file_watcher.py
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class HotReloadHandler(FileSystemEventHandler):
    def __init__(self, game_instance):
        self.game = game_instance

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"File modified: {event.src_path}. Setting reload flag.")
            self.game.needs_reload = True

def start_watching(game_instance, path='.'):
    event_handler = HotReloadHandler(game_instance)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print(f"Watching for file changes in '{path}/game'...")
    return observer