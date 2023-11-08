import click
import openai
import os
import sys
import json
from ojitos369.errors import CatchErrors as CE
from src.functions import *

ce = CE()
path = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(path, "src")
hist_file = os.path.join(src_path, ".vlaid_hist.json")
funtions_file = os.path.join(src_path, "functions.json")
functions_py = os.path.join(src_path, "functions.py")
logs_file = os.path.join(src_path, "logs.txt")
openai.api_key = os.environ["OPENAI_API_KEY"]

historial = []
limite_historial = 3
model_to_use = "gpt-4-1106-preview"
"""
tlc = 10
m = 0.02
mpc = 3
cpm = (m * mpc) * 1.3
cpm
md = tlc/cpm
md
# >> 0.26
"""

try:
    with open(hist_file, "r") as f:
        historial = f.read()
        historial = json.loads(historial)
        historial = historial["historial"]
except:
    historial = []

functions = []
try:
    with open(funtions_file, "r") as f:
        functions = f.read()
        functions = json.loads(functions)
        functions = functions["functions"]
except:
    functions = []

def llamada(messages):
    response_message = openai.ChatCompletion.create(
        model=model_to_use,
        messages=messages,
        functions=functions,
        function_call="auto",
    )
    return response_message

def get_openai_response(messages):
    # Set up the prompt for OpenAI
    
    response_message = llamada(messages)
    response_message = response_message.choices[0].message
    
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        r = None
        try:
            function_name = response_message["function_call"]["name"]
            fuction_to_call = available_functions[function_name]
            function_args = json.loads(response_message["function_call"]["arguments"])
            r = fuction_to_call(
                location=function_args.get("location"),
                unit=function_args.get("unit"),
            )
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
        response_message = None
        if chat:
            messages.append({"role": "function", "content": function_response, "name": function_name})
            response_message = llamada(messages)
            response_message = response_message.choices[0].message.content
        return chat, response_message

    else:
        return True, response_message.content


def clear_previous_line():
    sys.stdout.write('\r')
    sys.stdout.flush()


@click.command()
@click.argument('message', nargs=-1)
def main(message):
    global historial
    # print(historial)
    if type(message) in [tuple, list]:
        message = ' '.join(message)
    actual = ""
    if message:
        actual = message
    else:
        actual = input("> ")

    if actual != "exit" and actual != "ch":
        # Get the response from OpenAI
        antreriores = historial
        antreriores.append({"role": "user", "content": actual})
        save, response = get_openai_response(antreriores)
        if save and response:
            click.echo(response)
            response = {"role": "assistant", "content": response}
            historial.append(response)
        elif not response:
            click.echo("...")
    elif actual == "ch":
        historial = []
        click.echo("Historial cleared")

    if len(historial) > limite_historial:
        historial = historial[-limite_historial:]

    with open(hist_file, "w") as f:
        save = {"historial": historial}
        save = json.dumps(save, indent=4)
        f.write(save)

if __name__ == "__main__":
    main()
