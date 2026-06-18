from aiogram import types, Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
import os
from app.bot.text import Text
from app.bot.keyboards import *
from app.bot.utils import *
from app.bot.fsm import *

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    await message.answer(
        Text.start_text,
        reply_markup=main_menu_keyboard
    )


@router.message(F.text == '🆘 Помощь')
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    await message.answer(
        Text.help_text,
        reply_markup=back_to_menu()
    )


@router.message(F.text == "✉️ Анализ отдельного отзыва")
async def get_command_analyze_simple_review(message: types.Message, state: FSMContext):
    await state.set_state(AnalyzeSimpleReview.waiting_simple_review_text)
    await message.answer("Отправьте текст отзыва, который нужно проанализировать: ")

@router.message(StateFilter(AnalyzeSimpleReview.waiting_simple_review_text), F.text)
async def analyze_simple_review(message: types.Message, state: FSMContext):
    """Обработчик любого текстового сообщения"""
    # Получаем текст от пользователя
    text = message.text
    answer_text = await analyze_review(text)
    await message.answer(
        text=answer_text,
        reply_markup=back_to_menu()
    )
    await state.clear()


@router.message(F.text == "🗂 Анализ пакета отзывов")
async def get_command_analyze_pack_reviews(message: types.Message, state: FSMContext):
    await state.set_state(AnalyzePackReviews.waiting_pack_reviews_file)
    await message.answer("Отправьте файл формата .csv с отзывами, которые нужно проанализировать\n\n "
                         "Требования:\n"
                         "1️⃣ Размер файла до 10 МБ\n"
                         "2️⃣ Формат файла .csv\n"
                         "3️⃣ В файле только 1 колонка с отзывами")

@router.message(StateFilter(AnalyzePackReviews.waiting_pack_reviews_file), F.document)
async def analyze_pack_reviews(message: types.Message, state: FSMContext, bot: Bot):
    document = message.document

    if not document.file_name.endswith(".csv"):
        await message.answer(
            text = "❌ Файл должен быть формата .csv",
            reply_markup=main_menu_keyboard
        )
        await state.clear()
        return

    if document.file_size > 10 * 1024**2:
        await message.answer(
            text = "❌ Файл превышает размер 10 МБ",
            reply_markup=main_menu_keyboard
        )
        await state.clear()
        return

    df = await read_document(document, bot)
    if df.shape[1] > 1:
        await message.answer(
            text="❌ Файл должен содержать только одну колонку с отзывами",
            reply_markup=main_menu_keyboard
        )
        await state.clear()
        return

    processing_msg = await message.answer("⏳ Файл получен. Начинаю анализ...")
    try:
        col = df.columns[0]
        reviews_count = df.shape[0]
        results = []
        for idx, row in df.iterrows():
            text = str(row[col])

            if text.strip() == '' or pd.isna(text):
                results.append(
                    {
                        "label" : pd.NA,
                        "confidence" : 0.0,
                    }
                )
                continue

            result = await analyze_row_of_pack(text)
            results.append(result)

            if (idx + 1) % 10 == 0:
                progress = int((idx + 1) / reviews_count * 100)
                await processing_msg.edit_text(
                    f"⏳ Обработано {idx + 1} из {reviews_count} отзывов ({progress}%)"
                )

        df['label'] = [r['label'] for r in results]
        df['confidence'] = [r['confidence'] for r in results]

        output_buffer = io.BytesIO()
        df.to_csv(output_buffer, index=False, encoding='utf-8-sig')
        output_buffer.seek(0)

        temp_file_path = f"temp_result_{message.from_user.id}.csv"
        with open(temp_file_path, 'wb') as f:
            f.write(output_buffer.getvalue())

        result_file = types.FSInputFile(temp_file_path, filename="analyzed_reviews.csv")
        await message.answer_document(
            result_file,
            caption=f"✅ <b>Анализ завершен!</b>\n\n"
                    f"Обработано отзывов: {reviews_count}\n"
                    f"Результаты добавлены в колонки:\n"
                    f"• label — тональность\n"
                    f"• confidence — уверенность модели\n\n"
                    f"📊 <b>Статистика пакета отзывов:</b>\n"
                    f"• Негативных отзывов: {len([0 for res in results if res['label'] == 'Негативный']) / reviews_count * 100:.2f}%\n"
                    f"• Нейтральных отзывов: {len([0 for res in results if res['label'] == 'Нейтральный']) / reviews_count * 100:.2f}%\n"
                    f"• Позитивных отзывов: {len([0 for res in results if res['label'] == 'Позитивный']) / reviews_count * 100:.2f}%\n"
                    f"• NaN или ERROR: {len([0 for res in results if (pd.isna(res['label']) or res['label'] == 'ERROR')]) / reviews_count * 100:.2f}%\n"
                    f"• Средняя уверенность модели: {sum([result['confidence'] for result in results]) / reviews_count * 100:.2f}%\n",
            reply_markup=main_menu_keyboard
        )

        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        await processing_msg.delete()
    except Exception as e:
        await processing_msg.edit_text(f"❌ Ошибка при обработке файла: {str(e)}")

    await state.clear()


@router.message(F.text == 'ℹ️ О боте')
async def about(message : types.Message):
    await message.answer(
        Text.about_text,
        reply_markup=main_menu_keyboard
    )


@router.callback_query(F.data == "back_to_menu")
async def callback_back_to_menu(callback_query: types.CallbackQuery):
    await callback_query.answer()

    try:
        await callback_query.message.delete()
    except Exception:
        await callback_query.message.edit_text(text=Text.start_text)

    await callback_query.message.answer(
        text=Text.start_text,
        reply_markup=main_menu_keyboard
    )
