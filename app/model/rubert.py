import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from config import Config


class RuBERTModel:
    """Класс для работы с моделью RuBERT"""

    def __init__(self, model_path: str):
        # Загружаем токенизатор и модель
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)

        # Переводим модель в режим инференса (отключаем Dropout и BatchNorm в режиме обучения)
        self.model.eval()

        # Определяем устройство (GPU если есть, иначе CPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        # Маппинг ID классов на понятные названия (проверь, совпадают ли с твоим датасетом!)
        self.label_map = {
            0: "Негативный",
            1: "Нейтральный",
            2: "Позитивный"
        }

    def predict(self, text: str) -> dict:
        """Принимает текст и возвращает словарь с предсказанием"""

        # 1. Токенизация текста
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )

        # Переносим тензоры на то же устройство, где лежит модель (CPU или GPU)
        inputs = {key: val.to(self.device) for key, val in inputs.items()}

        # 2. Предсказание (в контексте torch.no_grad() для экономии памяти)
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits

        # 3. Обработка результатов
        # Преобразуем логиты в вероятности (softmax)
        probabilities = torch.softmax(logits, dim=-1)[0]

        # Находим индекс класса с максимальной вероятностью
        predicted_class_id = torch.argmax(logits, dim=-1).item()
        confidence = probabilities[predicted_class_id].item()

        return {
            "label_id": predicted_class_id,
            "label": self.label_map.get(predicted_class_id, "Неизвестно"),
            "confidence": round(confidence, 4)  # Округляем до 4 знаков
        }


_model_instance = None


def get_model() -> RuBERTModel:
    """Функция для получения единственного экземпляра модели"""
    global _model_instance
    if _model_instance is None:
        # Если модель еще не загружена, загружаем её
        _model_instance = RuBERTModel(Config.MODEL_PATH)
    return _model_instance