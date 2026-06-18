from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

storage = MemoryStorage()

class AnalyzeSimpleReview(StatesGroup):
    waiting_simple_review_text = State() # ожидание текста отзыва

class AnalyzePackReviews(StatesGroup):
    waiting_pack_reviews_file = State() # ожидание .csv файла
