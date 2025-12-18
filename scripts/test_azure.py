#!/usr/bin/env python3
"""Test Azure OpenAI connection"""

import pytest

pytest.skip("Manual Azure connectivity check; skip during automated tests", allow_module_level=True)

from openai import AzureOpenAI
import sys
import os
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import Settings

print('🔧 Testing Azure OpenAI Connection...')
print(f'Endpoint: {Settings.AZURE_OPENAI_ENDPOINT}')
print(f'Deployment: {Settings.AZURE_OPENAI_DEPLOYMENT_NAME}')
print(f'API Version: {Settings.AZURE_OPENAI_API_VERSION}')
print('')

try:
    client = AzureOpenAI(
        azure_endpoint=Settings.AZURE_OPENAI_ENDPOINT,
        api_key=Settings.AZURE_OPENAI_API_KEY,
        api_version=Settings.AZURE_OPENAI_API_VERSION
    )
    
    print('Sending test request to GPT-4o...')
    response = client.chat.completions.create(
        model=Settings.AZURE_OPENAI_DEPLOYMENT_NAME,
        messages=[
            {'role': 'user', 'content': '用中文说："Azure OpenAI 连接成功！"'}
        ],
        max_tokens=50,
        temperature=0.7
    )
    
    result = response.choices[0].message.content
    print(f'\n✅ SUCCESS!')
    print(f'GPT-4o Response: {result}')
    print(f'\nTokens used: {response.usage.total_tokens}')
    print(f'  - Prompt: {response.usage.prompt_tokens}')
    print(f'  - Completion: {response.usage.completion_tokens}')
    print('\n🎉 Azure OpenAI is working correctly!')
    
except Exception as e:
    print(f'\n❌ ERROR: {e}')
    print('\nPlease check:')
    print('1. Deployment name is correct (check Azure OpenAI Studio → Deployments)')
    print('2. Model is fully deployed and ready')
    print('3. API key and endpoint are correct')
    sys.exit(1)
