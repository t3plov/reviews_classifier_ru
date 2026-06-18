import aiohttp
from config import Config
import pandas as pd
import io

API_URL = f"http://{Config.FAST_API_HOST}:{Config.FAST_API_PORT}/predict"

async def analyze_review(text: str) -> str:
    if not text or len(text.strip()) == 0:
        return "Пожалуйста, отправьте текстовый отзыв"

    try:
        async with aiohttp.ClientSession() as session:
            payload = {"text": text}

            async with session.post(API_URL, json=payload) as response:
                if response.status == 200:
                    result = await response.json()

                    # Форматируем красивый ответ
                    label = result["label"]
                    confidence = result["confidence"]
                    confidence_percent = confidence * 100

                    answer = (
                        f"📊 <b>Результат анализа:</b>\n\n"
                        f"✏️ Тональность: {label}\n"
                        f"📈 Уверенность модели: {confidence_percent:.2f}%\n\n"
                        f"📝 Текст: {text[:100]}{'...' if len(text) > 100 else ''}"
                    )
                    return answer
                else:
                    error_data = await response.json()
                    return f"❌ Ошибка сервера: {error_data}"
    except aiohttp.ClientError:
        return "❌ В данный момент проблемы с сервером"
    except Exception as e:
        return f"❌ Произошла ошибка: {str(e)}"

async def read_document(document, bot):
    file = await bot.get_file(document.file_id)
    file_bytes = await bot.download_file(file.file_path)
    csv_content = file_bytes.read()
    df = pd.read_csv(io.BytesIO(csv_content), encoding='utf-8-sig')

    return df

async def analyze_row_of_pack(text: str):
    async with aiohttp.ClientSession() as session:
        payload = {"text": text}

        async with session.post(API_URL, json=payload) as response:
            if response.status == 200:
                response_result = await response.json()
                result = {
                    "label" : response_result["label"],
                    "confidence" : response_result["confidence"]
                }
                return result
            else:
                result = {
                    "label" : "ERROR",
                    "confidence" : 0.0
                }
                return result
