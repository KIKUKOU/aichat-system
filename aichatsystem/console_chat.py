#!/usr/bin/env python3
"""
The console chat.
"""

import os

from llm.gemini_wrapper import GeminiWrapper
from llm.openai_wrapper import OpenAIWrapper

if __name__ == '__main__':
    PROMPT_LOG_NAME = './log_files/prompt/prompt_log.csv'
    SYSTEM_PROMPT_NAME = './prompt_files/system/consolechat.csv'
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')
    streaming = True

    is_exit = False
    while not is_exit:
        use_ai = input('\n"openai"と"gemini"のどちらを使用しますか？（終了時は"exit"と入力）\n\n')  # noqa: RUF001
        # NOTE: Japanese sentence, so use Full-width letter.
        if use_ai == 'exit':
            is_exit = True
            break
        if use_ai == 'openai':
            init_config = {}
            LLM_client = OpenAIWrapper(OPENAI_API_KEY, init_config, PROMPT_LOG_NAME)
            break
        elif use_ai == 'gemini':
            init_config = {}
            LLM_client = GeminiWrapper(GEMINI_API_KEY, init_config, PROMPT_LOG_NAME)
            break

    while not is_exit:
        question = input('\nAIに聞きたい内容を入力してください（終了時は"exit"と入力）\n\n')  # noqa: RUF001
        # NOTE: Japanese sentence, so use Full-width letter.

        if question == 'exit':
            is_exit = True
            break

        if use_ai == 'openai':
            llm_config = {}
            llm_config['model_name'] = 'gpt-4o'
            llm_config['streaming'] = streaming
        elif use_ai == 'gemini':
            llm_config = {}
            llm_config['model_name'] = 'gemini-1.5-pro'
            llm_config['streaming'] = streaming
            llm_config['temperature'] = 1
            llm_config['top_p'] = 0.95
            llm_config['top_k'] = 64
            llm_config['max_output_tokens'] = 8192
            llm_config['response_mime_type'] = 'text/plain'

        system_prompt = LLM_client.load_prompt(SYSTEM_PROMPT_NAME)
        response, prompt = LLM_client.get_chat_response(question, llm_config, system_prompt)
        if not streaming:
            text = LLM_client.read_text(response)
        else:
            text = ''
            for chunk in response:
                text = text + LLM_client.read_text(chunk)

        print('\n============ Answer ============\n')
        print(f'{text}\n')
        print('================================')

        LLM_client.save_assistant_response(text)
