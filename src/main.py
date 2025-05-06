import gradio as gr
from src.environment import Environment
from src.agent import OpenAIComputerUseAgent
import base64
from io import BytesIO
from PIL import Image
from pathlib import Path
import os
import argparse


def encode_screenshot(screenshot):
    # Convert screenshot to base64
    buffered = BytesIO()
    screenshot.save(buffered, format="PNG")
    screenshot_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return screenshot_base64


def computer_use_loop(agent, env, task):
    """
    Run the loop that executes computer actions until no 'computer_call' is found.
    """
    global STEP, LAST_RESPONSE_ID
    screenshot = env.get_whole_screenshot(STEP)
    screenshot_base64 = encode_screenshot(screenshot)
    response = agent.get_initial_action(task, screenshot_base64, LAST_RESPONSE_ID)

    while True:
        computer_calls = [item for item in response.output if item.type == "computer_call"]
        if not computer_calls:
            # yield "No computer call found. Output from model:"
            messages = [item for item in response.output if item.type == "message"]
            message = messages[0] if messages else None
            if message:
                for content in message.content:
                    yield content.text + "\n"
            else:
                for item in response.output:
                    yield str(item) + "\n"
            LAST_RESPONSE_ID = response.id
            break  # Exit when no computer calls are issued.

        # We expect at most one computer call per response.
        computer_call = computer_calls[0]
        last_call_id = computer_call.call_id
        action = computer_call.action

        # Execute the action
        yield env.handle_model_action(action) + "\n"
        STEP += 1

        # Take a screenshot after the action
        screenshot = env.get_whole_screenshot(STEP)
        screenshot_base64 = encode_screenshot(screenshot)

        # Send the screenshot back as a computer_call_output
        response = agent.get_action(response.id, last_call_id, screenshot_base64, computer_call.pending_safety_checks)


def init():
    global ENV, AGENT, STEP, LAST_RESPONSE_ID, APP_BUNDLE
    # Initialize environment and agent
    output_dir = Path(f"logs/{APP_BUNDLE}")  # Replace with the desired output directory
    os.makedirs(output_dir, exist_ok=True)
    ENV = Environment(APP_BUNDLE, output_dir)
    AGENT = OpenAIComputerUseAgent(display_size=ENV.size)  # Replace with actual display size
    STEP = 0
    LAST_RESPONSE_ID = None


with gr.Blocks() as demo:
    chatbot = gr.Chatbot(type="messages")
    msg = gr.Textbox()
    clear = gr.Button("Clear")

    def user(user_message, history: list):
        return "", history + [{"role": "user", "content": user_message}]

    def bot(history: list):
        input_text = history[-1]["content"]
        history.append({"role": "assistant", "content": ""})
        for message in computer_use_loop(AGENT, ENV, input_text):
            history[-1]["content"] += message
            yield history

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear.click(lambda: init(), None, chatbot, queue=False)

if __name__ == "__main__":
    global APP_BUNDLE
    parser = argparse.ArgumentParser(description="Launch the OpenAI Computer Use Agent")
    parser.add_argument("--app_bundle", help="Application bundle identifier")
    args = parser.parse_args()
    APP_BUNDLE = args.app_bundle
    init()
    demo.launch()
