import onnxruntime as ort

# Verifica los proveedores disponibles
providers = ort.get_all_providers()
print("Proveedores disponibles:", providers)

# Asegúrate de que el proveedor CUDA está disponible
if 'CUDAExecutionProvider' in providers:
    print("CUDA está habilitado correctamente.")
else:
    print("CUDA no está habilitado.")
