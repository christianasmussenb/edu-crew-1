import os

LLM_CONFIGS = {
    "openai": {
        "model": "gpt-4o-mini", # "gpt-4o-mini" or "gpt-4o"
        "api_key": os.getenv('OPENAI_API_KEY')
    },
    "groq": {
        "model": "groq/llama3-groq-8b-8192-tool-use-preview", 
        "api_key": os.getenv('GROQ_API_KEY')
    },
    "anthropic": {
        "model": "anthropic/claude-3-5-sonnet-20240620",
        "api_key": os.getenv('ANTHROPIC_API_KEY')
    }
}

LLM_CONFIG = LLM_CONFIGS["openai"] # Change this to switch between LLMs

EDU_FLOW_INPUT_VARIABLES = {
    "audience_level": "begginer",
    "topic": "Healthcare, latest advancements in medicine using AI",
} 