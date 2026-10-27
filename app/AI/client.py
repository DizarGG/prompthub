import logging
import time

from ollama import Client
from app.config import setting

logger = logging.getLogger(__name__)


class AICL:
    def __init__(self):
        self.model = setting('OLLAMA_MODEL', 'qwen3:4b')
        self.client = Client(
            host=setting('OLLAMA_HOST', 'http://127.0.0.1:11434'),
            timeout=300.0,
            trust_env=False,  # локальная Ollama не должна идти через HTTP_PROXY
        )

    def generate_text(self, prompt: str) -> str:
        started = time.monotonic()
        logger.info('Ollama request started; model=%s', self.model)
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': (
                        'Ты профессиональный промпт-инженер. На основе задачи пользователя '
                        'создай один подробный, практичный промпт для нейросети. '
                        'Укажи роль, задачу, контекст, ограничения и формат ответа. '
                        'Верни только готовый промпт, без пояснений и вступления.')},
                    {'role': 'user', 'content': prompt},
                ],
                think=False,
                options={'temperature': 0.5, 'num_predict': 512},
            )
            text = (response.message.content or '').strip()
            if '</think>' in text:
                text = text.split('</think>', 1)[1].strip()
            if not text:
                raise ValueError('Модель вернула пустой ответ')
            return text
        finally:
            logger.info('Ollama request finished after %.1f seconds', time.monotonic() - started)
