import uvicorn
from config import Config

if __name__ == "__main__":
    # Запускаем сервер Uvicorn, используя параметры из нашего Config
    uvicorn.run(
        "app.api.main:app",
        host=Config.FAST_API_HOST,
        port=Config.FAST_API_PORT,
        reload=True # reload=True автоматически перезагружает сервер при изменении кода
    )