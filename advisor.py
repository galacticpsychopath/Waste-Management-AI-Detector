import ollama

def get_advice(object_name):
    """
    Queries Ollama to get recyclability advice and a DIY project for the given object.
    """
    # You can change the model
    model_name = 'gpt-oss:120b-cloud' 
    
    prompt = (
        f"I have a object detected as: '{object_name}'. "
        "1. Is it recyclable? (Yes/No) "
        "2. If yes, give me ONE creative DIY project idea. "
        "3. If no, give me safe disposal instructions. "
        "Keep the response short and friendly."
    )
    
    print(f"Thinking about {object_name}...")
    try:
        response = ollama.chat(model=model_name, messages=[
            {'role': 'user', 'content': prompt},
        ])
        return response['message']['content']
    except Exception as e:
        return f"Error connecting to Ollama (ensure 'ollama serve' is running and model '{model_name}' is pulled): {e}"

if __name__ == "__main__":
    print(get_advice("plastic bottle"))
