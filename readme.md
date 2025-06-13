### Fusión manual de ramas sam_branch y release 1.0.0






Librerías empleadas:

Configuración de entorno de python:
    py -3.10 -m venv faceenv 
    faceenv\Scripts\activate 

Librerías:
pip install paddleocr
pip install paddlepaddle
pip install insightface[all] onnxruntime-gpu opencv-python
pip install streamlit
pip install faiss-cpu==1.8.0 #<--- esta versión no tiene problema de compatibilidad con paddleOCR
pip install PyMySQL
pip install streamlit-webrtc
//pip install av
pip install streamlit-option-menu



Para soporte de CUDA en torch y easyOCR

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121