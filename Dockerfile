FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# Install Ollama
RUN apt-get update && apt-get install -y curl
RUN curl -fsSL https://ollama.com/install.sh | sh

# Expose the Ollama API port
EXPOSE 11434

# Set environment variables for resource management
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_ORIGINS=*
ENV NVIDIA_VISIBLE_DEVICES=all

# Command to run Ollama
CMD ["ollama", "serve"] 