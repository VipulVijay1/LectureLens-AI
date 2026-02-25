import os
import faiss
from collections import OrderedDict
from app.core.logger import logger
from app.core.config import DATA_DIR, MAX_CACHE_SIZE


class IndexManager:
    def __init__(self):
        self.cache = OrderedDict()

    def get_index(self, video_id: str):
        # If index already in cache → move to end (most recently used)
        if video_id in self.cache:
            logger.info(f"Cache hit for video {video_id}")
            self.cache.move_to_end(video_id)
            return self.cache[video_id]

        logger.info(f"Cache miss for video {video_id}, loading from disk")
        # Otherwise load from disk
        index = self._load_from_disk(video_id)

        # Add to cache
        self.cache[video_id] = index

        # Evict if needed
        if len(self.cache) > MAX_CACHE_SIZE:
            self.cache.popitem(last=False)  # Remove least recently used

        return index

    def _load_from_disk(self, video_id: str):
        video_path = os.path.join(DATA_DIR, video_id)
        index_path = os.path.join(video_path, "index.faiss")

        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Index not found for video {video_id}")

        return faiss.read_index(index_path)


# Singleton instance
index_manager = IndexManager()