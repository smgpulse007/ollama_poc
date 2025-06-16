from ollama_client import OllamaClient

def test_model():
    client = OllamaClient()
    
    # Simple prompt
    prompt = "Explain what Docker is in one sentence."
    
    print("Sending prompt:", prompt)
    print("\nResponse:")
    
    response = client.generate(
        prompt=prompt,
        model="gemma3:4b",
        temperature=0.7,
        max_tokens=100
    )
    
    print(response.get('response', ''))

if __name__ == "__main__":
    test_model() 