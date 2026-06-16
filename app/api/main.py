from fastapi import FastAPI, HTTPException
from app.api.schemas import SentimentRequest, SentimentResponse
from app.model.rubert import get_model
from config import Config

# Инициализация FastAPI приложения
app = FastAPI(
    title="Sentiment Analysis API",
    description="API для классификации тональности отзывов на русском языке (RuBERT)",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    """
    Событие, которое выполняется один раз при запуске сервера.
    Здесь мы валидируем конфиг и загружаем тяжелую модель в память,
    чтобы первый запрос пользователя не ждал 10 секунд её загрузки.
    """
    print(" Запуск сервера...")
    Config.validate()
    get_model()  # Предзагрузка модели
    print("✅ Сервер готов к обработке запросов!")


@app.get("/")
def read_root():
    """Простая проверка, что сервер работает (Health Check)"""
    return {"status": "ok", "message": "Sentiment Analysis API is running"}


@app.post("/predict", response_model=SentimentResponse)
def predict_sentiment(request: SentimentRequest):
    """
    Главный эндпоинт. Принимает текст, возвращает тональность.
    ВАЖНО: Используем обычный def (не async def), так как инференс модели
    блокирует поток. FastAPI автоматически запустит эту функцию в отдельном потоке,
    чтобы не блокировать весь сервер.
    """
    try:
        # Получаем экземпляр модели (она уже загружена в память)
        model = get_model()

        # Делаем предсказание
        result = model.predict(request.text)

        return result

    except Exception as e:
        # Если что-то пошло не так, возвращаем красивую ошибку 500
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке текста: {str(e)}")