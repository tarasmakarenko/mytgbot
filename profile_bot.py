import cProfile
import pstats
import asyncio
from unittest.mock import AsyncMock, MagicMock
from for_test import handlers, utils

async def test_scenario():
    # Створюємо мок для message.reply_text()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()

    # Створюємо мок для update
    mock_update = MagicMock()
    mock_update.message = mock_message
    mock_update.effective_user.id = 123456789  # для логів

    # Мок для context
    mock_context = MagicMock()

    # Виклик асинхронних функцій
    if hasattr(handlers, 'start'):
        await handlers.start(mock_update, mock_context)
    if hasattr(handlers, 'help_command'):
        await handlers.help_command(mock_update, mock_context)

    # Синхронна функція
    if hasattr(utils, 'get_welcome_message'):
        msg = utils.get_welcome_message("test_user")
        print(f"Welcome message: {msg}")

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    asyncio.run(test_scenario())

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative").print_stats(10)