"""
Lokantra Backend - Hugging Face Spaces Gradio SDK Entry Point
"""
import os
import sys

# Ensure backend directory is in Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Ensure uploads, logs, and simulations directories exist
uploads_dir = os.path.join(backend_dir, 'uploads')
simulations_dir = os.path.join(uploads_dir, 'simulations')
logs_dir = os.path.join(backend_dir, 'logs')
os.makedirs(uploads_dir, exist_ok=True)
os.makedirs(simulations_dir, exist_ok=True)
os.makedirs(logs_dir, exist_ok=True)

# ZeroGPU registration for Hugging Face Spaces
try:
    import spaces
    @spaces.GPU
    def _zero_gpu_init():
        return True
except Exception:
    pass

from app import create_app

# Create Flask application instance
app = create_app()

@app.route('/')
def home():
    return {
        'status': 'online',
        'service': 'Lokantra AI Swarm Intelligence Engine API',
        'version': '0.1.0',
        'health_check': '/health'
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port, threaded=True)
