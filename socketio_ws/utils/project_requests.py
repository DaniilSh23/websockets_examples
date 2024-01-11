"""
Логика различных http запросов.
"""
import aiohttp
from socketio_ws.utils.settings import AI_WEBAPP_GET_GPT_ANSWER, AI_WEBAPP_TOKEN, MY_LOGGER, OPENAI_CLIENT


async def get_gpt_answer(prompt, query, base_text=None, temp=0.5):
    """
    Функция для того, чтобы отправить запрос к модели GPT и получить ответ.
    prompt - инструкция для модели GPT
    query - запрос пользователя
    base_text - текст, на котором модель должна базировать свой ответ
    temp - (значение от 0 до 1) чем выше, тем более творчески будет ответ модели, то есть она будет додумывать что-то.
    """
    messages = [
        {"role": "system", "content": prompt},
    ]
    if base_text:
        messages.append({"role": "user", "content": f"Data with response information: \n{base_text}\n\n"
                                                    f"User question: \n{query}"})
    else:
        messages.append({"role": "user", "content": f"User question: \n{query}"})

    try:
        completion = await OPENAI_CLIENT.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo",
        )
    except Exception as err:
        MY_LOGGER.error(f'Ошибка от OpenAI: {err}')
        return False, f'Ошибка от OpenAI: {err}'
    answer = completion.choices[0].message.content
    return True, answer  # возвращает ответ


async def get_gpt_answer_through_my_webapp(
    prompt: str,
    query: str,
    base_text: str = '',
    temp: float = 0.5,
):
    """
    Получить ответ модели AI через мою веб-приложуху.
    """
    req_data = {
        "prompt": prompt,
        "query": query,
        "base_text": base_text,
        "temp": temp,
    }
    headers = {
        "Authorization": f"Bearer {AI_WEBAPP_TOKEN}"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url=AI_WEBAPP_GET_GPT_ANSWER, json=req_data, headers=headers) as response:
            if response.status == 200:
                MY_LOGGER.success(f'Успешный {response.method!r} запрос для получения ответа AI модели')
            else:
                MY_LOGGER.warning(f'Неудачный {response.method!r} запрос для получения ответа AI модели | '
                                  f'STATUS: {response.status} | DETAIL: {await response.text()}')
            return response.status, await response.json()
