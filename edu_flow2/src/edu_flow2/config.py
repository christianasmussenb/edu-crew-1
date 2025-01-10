import os

LLM_CONFIGS = {
    "openai": {
        "model": "gpt-4o-mini", # "gpt-4o-mini" or "gpt-4o"
        "api_key": os.getenv('OPENAI_API_KEY')
    },
    "groq": {
        "model": "groq/llama3-groq-8b-8192", 
        "api_key": os.getenv('GROQ_API_KEY')
    },
    "cerebras": {
        "model": "cerebras/gemma2-9b",
        "api_key": os.getenv('CEREBRAS_API_KEY')
    }
}

LLM_CONFIG = LLM_CONFIGS["openai"] # Change this to switch between LLMs

EDU_FLOW_INPUT_VARIABLES = {
    "audience_level": os.getenv('EDUFLOW_LEVEL', 'beginner'),
    "topic": os.getenv('EDUFLOW_TOPIC', 'Latest LLM models and finance'),
} 