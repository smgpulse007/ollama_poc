from ollama_client import OllamaClient
import time
import psutil
import os

def print_stats():
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024 ** 2)  # in MB
    cpu = process.cpu_percent(interval=1)
    print(f"[Resource] CPU: {cpu:.2f}% | Memory: {mem:.2f} MB")

def test_memory_usage():
    client = OllamaClient()
    print("Starting memory and CPU test...")
    print_stats()
    print("Sending a prompt to the model...")
    start_time = time.time()
    response = client.generate(
        prompt="Write a detailed explanation of how large language models work, including their architecture and training process.",
        model="gemma3:4b",
        temperature=0.7,
        max_tokens=1000
    )
    end_time = time.time()
    print("\nResponse received!")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    print_stats()
    print("\nFirst 200 characters of response:")
    print(response.get('response', '')[:200])
    print("\nTo check container memory usage, run in another terminal:")
    print("docker stats ollama_poc-ollama-1 --no-stream")

if __name__ == "__main__":
    test_memory_usage() 