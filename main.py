from kubernetes import client, config
import pandas as pd
import numpy as np
import tensorflow as tf
import joblib
token = "eyJhbGciOiJSUzI1NiIsImtpZCI6Ikw4Zl8zS3hzdmN5aVpXVi1lNkRzUVppUzZYLUxSMHI0RDNxdnhRRUgtcGsifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4iLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6IjRlN2I1YmExLTdhMjgtNGVhMC1iODVhLWI3ZWY5ODE3YTY5OSIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.j980WjWTiosCv-4pjZDSnHwzCadDCpYn5FCRTIO90yJrRqBha5RMpST9NX2N08yjaIYARZwbd7WrvRD0hFfijFtBINTIwXyEXLg4pizVtBmWSvNz44saeZ62_Zql7L6Y1S6OzEqhqMj7YIfs5pGnEDbjrS5vw1qyKIdbB7XFF2YEpe2pFGQe9wWvsg1FxJUG-F6vK4NmXlrdatjhY1d3E_qpUn1YahUgPL8swTMqYwU-ETK1DL7wKUQcJjOoB30G9FSeNFML4JQ3ty4C5t7pxrzq8FJL37xD-mwy6v79Rr1XDVTHgHPMEB7ZeGmjRSI5zGBhO8VN_VXgoa3ebgT2ZQ"

configuration = client.Configuration()
configuration.host = "http://192.168.21.130"
configuration.verify_ssl = False
# configuration.api_key = {"Authorization": "Bearer " + token}

ApiClient = client.ApiClient(configuration)

v1apps = client.AppsV1Api(ApiClient)
v1core = client.CoreV1Api(ApiClient)
api_custom = client.CustomObjectsApi(ApiClient)

#ct = make_column_transformer((MinMaxScaler(), ['frontend_cpu_usage', 'frontend_memory_usage', 'backend_cpu_usage', 'backend_memory_usage', 'database_cpu_usage', 'database_memory_usage']),
#                             (OneHotEncoder(handle_unknown="ignore"), ['frontend', 'backend', 'database', 'frontend_memory_pressure', 'frontend_disk_pressure', 'backend_memory_pressure', 'backend_disk_pressure', 'database_memory_pressure', 'database_disk_pressure']))

ct = joblib.load('ct.save')

sample = np.array([[
    'minikube-m02',
    'minikube-m03',
    'minikube-m03',
    'False',
    'False',
    'False',
    'False',
    'False', 
    'False',
    0.21,
    0.18,
    0.25,
    0.2,
    0.25,
    0.2
]])


df = pd.DataFrame(sample, columns=['frontend', 'backend', 'database', 'frontend_memory_pressure',
    'frontend_disk_pressure',
    'backend_memory_pressure',
    'backend_disk_pressure',
    'database_memory_pressure', 
    'database_disk_pressure',
    'frontend_cpu_usage',
    'frontend_memory_usage',
    'backend_cpu_usage',
    'backend_memory_usage',
    'database_cpu_usage',
    'database_memory_usage'
])
ct
df_normal = ct.transform(df)
model = tf.keras.models.load_model('test.h5')

print(model.predict(df_normal))