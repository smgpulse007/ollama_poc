import requests
import json
from typing import Dict, Any, Optional

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialize the Ollama client.
        
        Args:
            base_url (str): The base URL of the Ollama server. Defaults to localhost:11434.
        """
        self.base_url = base_url.rstrip('/')
        
    def generate(self, 
                prompt: str, 
                model: str = "llama2", 
                stream: bool = False,
                **kwargs) -> Dict[str, Any]:
        """Generate a response from the model.
        
        Args:
            prompt (str): The prompt to send to the model
            model (str): The model to use. Defaults to "llama2"
            stream (bool): Whether to stream the response. Defaults to False
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dict[str, Any]: The response from the model
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            **kwargs
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        if stream:
            return response.iter_lines()
        return response.json()
    
    def list_models(self) -> Dict[str, Any]:
        """List all available models.
        
        Returns:
            Dict[str, Any]: List of available models
        """
        url = f"{self.base_url}/api/tags"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

# Example usage
if __name__ == "__main__":
    client = OllamaClient()
    
    # List available models
    models = client.list_models()
    print("Available models:", models)
    
    # Generate a response
    response = client.generate(
        prompt="What is the capital of France?",
        model="llama2"
    )
    print("\nResponse:", response.get('response', '')) 