import click
from openai import OpenAI
import os
import sys
import json
import datetime
from ojitos369.errors import CatchErrors as CE
from src.functions import *

ce = CE()
path = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(path, "src")
hist_file = os.path.join(src_path, ".vlaid_hist.json")
funtions_file = os.path.join(src_path, "functions.json")
functions_py = os.path.join(src_path, "functions.py")
logs_file = os.path.join(src_path, "logs.txt")
settings_file = os.path.join(src_path, "settings.json")

client = OpenAI()

def try_func(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error = ce.show_error(e)
        print(error)
        with open(logs_file, "a+") as f:
            fecha = datetime.datetime.now()
            # dd/mm/YY H:M:S
            fecha = fecha.strftime("%d/%m/%Y %H:%M:%S")
            f.write(f"{fecha}: {error}\n")

class Chat:
    def __init__(self):
        self.historial = []
        self.limite_historial = 3
        self.model_to_use = "gpt-4o"
        self.context_limit = 1000
        with open(settings_file, "r") as f:
            ajustes = json.loads(f.read())
            self.limite_historial = ajustes.get("limite_mensajes", self.limite_historial)
            self.model_to_use = ajustes.get("model_to_use", self.model_to_use)
            self.context_limit = ajustes.get("context_limit", self.context_limit)
        try:
            with open(hist_file, "r") as f:
                self.historial = f.read()
                self.historial = json.loads(self.historial)
                self.historial = self.historial["historial"]
        except:
            self.historial = []

        self.functions = []
        try:
            with open(funtions_file, "r") as f:
                self.functions = f.read()
                self.functions = json.loads(self.functions)
                self.functions = self.functions["functions"]
        except:
            self.functions = []

    def llamada(self):
        try:
            response_message = client.chat.completions.create(
                model=self.model_to_use,
                messages=self.messages,
                functions=self.functions,
                function_call="auto",
            )
        except Exception as e:
            error = ce.show_error(e)
            print(error)
            print(str(e))
            with open(logs_file, "a+") as f:
                fecha = datetime.datetime.now()
                # dd/mm/YY H:M:S
                fecha = fecha.strftime("%d/%m/%Y %H:%M:%S")
                f.write(f"{fecha}: {error}\n")
            raise e
        return response_message

    def get_openai_response(self):
        # Set up the prompt for OpenAI
        response_message = self.llamada()
        response_message = response_message.choices[0].message

        function_call = None
        try:
            function_call = response_message.function_call
        except:
            function_call = None
        
        if function_call:
            r = None
            try:
                function_name = function_call.name
                args = function_call.arguments
                fuction_to_call = available_functions[function_name]
                function_args = json.loads(args)
                r = fuction_to_call(**function_args)
                # print(f"r: {r}")
            except Exception as e:
                error = ce.show_error(e)
                # open and save logs
                with open(logs_file, "a+") as f:
                    fecha = datetime.datetime.now()
                    # dd/mm/YY H:M:S
                    fecha = fecha.strftime("%d/%m/%Y %H:%M:%S")
                    f.write(f"{fecha}: {error}\n")
                r = None
            chat, function_response = False, None
            if r:
                try:
                    chat, function_response = r
                except:
                    function_response = r
            if function_response and not chat:
                click.echo(function_response)
                self.messages.append({"role": "function", "content": str(function_response), "name": function_name})
                response_message = function_response
            if chat:
                self.messages.append({"role": "function", "content": str(function_response), "name": function_name})
                response_message = self.llamada()
                response_message = response_message.choices[0].message.content
            return chat, response_message
        else:
            return True, response_message.content

    def clear_previous_line(self):
        sys.stdout.write('\r')
        sys.stdout.flush()

    def run_chat(self, message):
        if type(message) in [tuple, list]:
            message = ' '.join(message)
        actual = ""
        if message:
            actual = message
        else:
            actual = input("> ")
        if actual.lower() not in ["exit", "ch", "limpiar"]:
            # Get the response from OpenAI
            self.messages = self.historial
            self.messages.append({"role": "user", "content": actual})
            save, response = self.get_openai_response()
            if save and response:
                click.echo(response)
                response = {"role": "assistant", "content": response}
                self.historial.append(response)
            elif not response:
                click.echo("...")
        elif actual.lower() in ["ch", "limpiar"]:
            self.historial = []
            click.echo("Historial cleared")
        if len(self.historial) > self.limite_historial:
            self.historial = self.historial[-self.limite_historial:]
        with open(hist_file, "w") as f:
            save = {"historial": self.historial}
            save = json.dumps(save, indent=4)
            f.write(save)


@click.command()
@click.argument('message', nargs=-1)
def main(message):
    chat = Chat()
    chat.run_chat(message)


if __name__ == "__main__":
    main()
