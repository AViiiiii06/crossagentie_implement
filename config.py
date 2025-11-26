from autogen_ext.models.ollama import OllamaChatCompletionClient

model1="deepseek-r1:8b"
model2="llama3.2:latest"
model3="llama3.2-vision:latest"

host="http://localhost:11434"

def get_model1_client():
    return OllamaChatCompletionClient(
        model=model1,
        host=host,
        model_info={
            "json_output": True,
            "function_calling": False,
            "vision": False,
            "supports_image_input": False,
            "supports_audio_input": False,
            "supports_pdf_input": False,
            "supports_stream": True,
            "supports_tools": False}
    )

def get_model2_client():
    return OllamaChatCompletionClient(
        model=model2,
        host=host,
        model_info={
            "json_output": True,
            "function_calling": False,
            "vision": False,
            "supports_image_input": False,
            "supports_audio_input": False,
            "supports_pdf_input": False,
            "supports_stream": True,
            "supports_tools": False}
    )

def get_model3_client():
    return OllamaChatCompletionClient(
        model=model3,
        host=host,
        model_info={
            "json_output": True,
            "function_calling": False,
            "vision": False,
            "supports_image_input": False,
            "supports_audio_input": False,
            "supports_pdf_input": False,
            "supports_stream": True,
            "supports_tools": False}
    )


