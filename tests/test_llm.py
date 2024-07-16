# -*- coding: utf-8 -*-

import os

import pytest
from llm import OpenAIWrapper, GeminiWrapper

def test_make_prompt():
    wrapper = OpenAIWrapper("dummy_key")
    prompt = wrapper.make_prompt([], "user", "Hello")
    assert prompt == [{"role": "user", "content": "Hello"}]


@pytest.mark.parametrize("wrapper_class", [OpenAIWrapper, GeminiWrapper])
def test_initialization(wrapper_class):
    wrapper = wrapper_class("dummy_key")
    assert wrapper.client is not None


# モックを使用したレスポンステスト
def test_openai_response(mocker):
    mock_client = mocker.Mock()
    mock_client.chat.completions.create.return_value = mocker.Mock(choices=[mocker.Mock(message=mocker.Mock(content="Test response"))])
    
    wrapper = OpenAIWrapper("dummy_key")
    wrapper.client = mock_client
    
    response, _ = wrapper.response([{"role": "user", "content": "Test"}])
    assert wrapper.read_text(response) == "Test response"


# 実際のAPIを使用したテスト（注意：実際のAPIキーが必要）
@pytest.mark.integration
def test_real_api_call():
    wrapper = OpenAIWrapper(os.getenv("OPENAI_API_KEY"))
    response, _ = wrapper.chat_response("Hello, AI!")
    assert len(wrapper.read_text(response)) > 0

if __name__ == '__main__':
    prompt_log_name = './log_files/prompt/prompt_log.csv'
    system_prompt_name = './prompt_files/system/voicechat.csv'
    GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')
    streaming = True

    AI_client = GeminiWrapper(GEMINI_API_KEY, prompt_log_name)

    question = input('AIに聞きたい内容を入力してください\n')

    config = {}
    config['model_name'] = 'gemini-1.5-pro'
    config['streaming'] = streaming

    system_prompt = AI_client.load_prompt(system_prompt_name)
    response = AI_client.chat_response(question, config, system_prompt)

    if not streaming:
        text = AI_client.read_text(response)
        print(text)
    else:
        text = ''
        for chunk in response:
            text = text + AI_client.read_text(chunk)
            print(text)

    AI_client.save_assistant_response(text)

    if __name__ == '__main__':
    prompt_log_name = './log_files/prompt/prompt_log.csv'
    system_prompt_name = './prompt_files/system/voicechat.csv'
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    streaming = True

    AI_client = OpenAIWrapper(OPENAI_API_KEY, prompt_log_name)

    question = input('AIに聞きたい内容を入力してください\n')

    config = {}
    config['model_name'] = 'gpt-4o'
    config['streaming'] = streaming

    system_prompt = AI_client.load_prompt(system_prompt_name)
    response = AI_client.chat_response(question, config, system_prompt)

    if not streaming:
        text = AI_client.read_text(response)
        print(text)
    else:
        text = ''
        for chunk in response:
            text = text + AI_client.read_text(chunk)
            print(text)

    AI_client.save_assistant_response(text)