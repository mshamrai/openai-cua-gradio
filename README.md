# OpenAI CUA Gradio app

Run an OpenAI‑powered UI agent against any macOS application from the command line.

## Usage

After you create a virtual environment and install the dependencies:

1. Add your **OpenAI API key** to `run.sh`.
2. Find the bundle identifier of the macOS application you want the agent to control (e.g. Safari’s bundle ID is `com.apple.Safari`).  
   You can look it up with:
   ```bash
   osascript -e 'id of app "Safari"'
   ```
3. Start the agent, passing the bundle identifier you found:
    ```
    sh run.sh -a com.apple.Safari
    ```