import psutil
import time
import subprocess
import json
from datetime import datetime

def get_container_stats():
    try:
        result = subprocess.run(
            ['docker', 'stats', 'ollama_poc-ollama-1', '--no-stream', '--format', '{{json .}}'],
            capture_output=True,
            text=True
        )
        return json.loads(result.stdout)
    except Exception as e:
        return f"Error getting container stats: {str(e)}"

def get_gpu_stats():
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total', '--format=csv,noheader,nounits'],
            capture_output=True,
            text=True
        )
        gpu_util, mem_used, mem_total = map(float, result.stdout.strip().split(', '))
        return {
            'gpu_utilization': gpu_util,
            'gpu_memory_used': mem_used,
            'gpu_memory_total': mem_total
        }
    except Exception as e:
        return f"Error getting GPU stats: {str(e)}"

def get_process_stats():
    process = psutil.Process()
    return {
        'cpu_percent': process.cpu_percent(),
        'memory_percent': process.memory_percent(),
        'memory_info': process.memory_info()._asdict()
    }

def monitor_resources():
    print("Starting resource monitoring...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n=== Resource Usage at {timestamp} ===")
            
            # Container stats
            container_stats = get_container_stats()
            print("\nContainer Stats:")
            print(f"CPU Usage: {container_stats.get('CPUPerc', 'N/A')}")
            print(f"Memory Usage: {container_stats.get('MemUsage', 'N/A')}")
            print(f"Net I/O: {container_stats.get('NetIO', 'N/A')}")
            
            # GPU stats
            gpu_stats = get_gpu_stats()
            print("\nGPU Stats:")
            print(f"GPU Utilization: {gpu_stats.get('gpu_utilization', 'N/A')}%")
            print(f"GPU Memory Used: {gpu_stats.get('gpu_memory_used', 'N/A')} MB")
            print(f"GPU Memory Total: {gpu_stats.get('gpu_memory_total', 'N/A')} MB")
            
            # Process stats
            process_stats = get_process_stats()
            print("\nApplication Stats:")
            print(f"CPU Usage: {process_stats['cpu_percent']}%")
            print(f"Memory Usage: {process_stats['memory_percent']:.2f}%")
            print(f"Memory Info: {process_stats['memory_info']}")
            
            print("\n" + "="*50)
            time.sleep(2)  # Update every 2 seconds
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    monitor_resources() 