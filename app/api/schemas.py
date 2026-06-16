from pydantic import BaseModel, Field

class SentimentRequest(BaseModel):
    """Схема для входящего запроса (текст отзыва)"""
    text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Текст отзыва для анализа тональности",
        examples=[
            "Фильм просто отличный, всем рекомендую!",
            "Сюжет затянут, игра актеров слабая.",
            "Нормальное кино на один вечер, ничего особенного."
        ]
    )

class SentimentResponse(BaseModel):
    """Схема для исходящего ответа (результат предсказания)"""
    label: str = Field(..., description="Предсказанный класс тональности")
    confidence: float = Field(..., description="Уверенность модели в предсказании")
    label_id: int = Field(..., description="Числовой ID класса (0, 1 или 2)")