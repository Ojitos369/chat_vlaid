* exporta la api de openai en OPENAI_API_KEY  
    `export OPENAI_API_KEY='<key>'`
* ejecutar los comandos  
    ```shell
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        pyinstaller --onefile main.py 
        cd dist 
        cp main vlaid 
        cp vlaid ~/vlaid 
        cd ..
    ```
* crea los archivos functions.json, functions.py en la carpeta ~/vlaid  

functions.py
```python

def tu_funcion(*args, **kwargs):
    print("Aqui va todo tu codigo")

def saluda(nombre):
    print(f"Hola {nombre}")

# Agrega todas las funciones que ocupes

available_functions = {
    "tu_funcion": tu_funcion,
}
```  

functions.json
```json
{
    "functions": [
        {
            "name": "tu_funcion",
            "description": "una descripcion para que sea identificada tu funcion",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre_de_parametro": {
                        "type": "tipo_de_dato",
                        "description": "una descripcion para que sea identificada tu parametro"
                    }
                },
                "required": [
                    "nombre_de_parametro_que sea requerido"
                ]
            }
        },
        {
            "name": "saluda",
            "description": "Esta funcion saluda a la persona que se le pasa",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {
                        "type": "string",
                        "description": "nombre de la persona a saludar"
                    }
                },
                "required": [
                    "nombre"
                ]
            }
        }
    ]
}
```