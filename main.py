import click
import openai
import os
import sys
import json

home = os.path.expanduser("~")
path = os.path.join(home, "vlaid")
hist_file = os.path.join(path, ".vlaid_hist.json")
funtions_file = os.path.join(path, "functions.json")
functions_py = os.path.join(path, "functions.py")
openai.api_key = os.environ["OPENAI_API_KEY"]

available_functions = {}
# import functions from functions.py
try:
    exec(open(functions_py).read())
except:
    print("Error importing functions.py")
    pass

historial = []
try:
    with open(hist_file, "r") as f:
        historial = f.read()
        historial = json.loads(historial)
        historial = historial["historial"]
except:
    historial = []

functions = []
# available_functions = {}
try:
    with open(funtions_file, "r") as f:
        functions = f.read()
        functions = json.loads(functions)
        # available_functions = functions["available_functions"]
        functions = functions["functions"]
except:
    functions = []

def llamada(messages):
    response_message = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions,
        function_call="auto",
    )
    return response_message

def get_openai_response(messages):
    # Set up the prompt for OpenAI
    
    response_message = llamada(messages)
    # .content
    response_message = response_message.choices[0].message
    
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        function_name = response_message["function_call"]["name"]
        fuction_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        r = fuction_to_call(
            location=function_args.get("location"),
            unit=function_args.get("unit"),
        )
        chat, function_response = False, None
        if r:
            try:
                chat, function_response = r
            except:
                function_response = r
        if function_response is not chat:
            click.echo(function_response)
        response_message = None
        if chat:
            messages.append({"role": "function", "content": function_response})
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
        if save:
            click.echo(response)
            response = {"role": "assistant", "content": response}
            
            historial.append(response)
    elif actual == "ch":
        historial = []
        click.echo("Historial cleared")

    if len(historial) > 500:
        historial = historial[-500:]

    with open(hist_file, "w") as f:
        save = {"historial": historial}
        save = json.dumps(save, indent=4)
        f.write(save)

if __name__ == "__main__":
    main()
