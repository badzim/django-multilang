import time
from django.conf import settings
from openai import OpenAI
from django.utils.translation import gettext as _
import logging

logger = logging.getLogger('documentation')


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def check_time_interval(request, interval_key='last_question_time', interval_seconds=settings.CHAT_INTERVAL_SECONDS):
    last_question_time = request.session.get(interval_key, 0)
    current_time = time.time()
    time_diff = current_time - last_question_time
    if time_diff < interval_seconds:
        return False, _("views.chatbot.wait_before_retry")
    request.session[interval_key] = current_time
    return True, None


def call_openai_api(question, context, user_language):
    personalized_prompt = _(f"views.chatbot.personalized_user_prompt : {question}.")
    system_prompt = _(f"views.chatbot.system_prompt {user_language}.")
    assistant_prompt = _(f"views.chatbot.assistant_prompt {context}.")
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": personalized_prompt},
            {"role": "assistant", "content": assistant_prompt},
        ],
        **settings.GPT_SETUP,
    )
    logger.debug(f"System Prompt: {system_prompt}")
    logger.debug(f"User Prompt: {personalized_prompt}")
    logger.debug(f"Assistant Prompt: {assistant_prompt}")
    return response.choices[0].message.content.strip()
