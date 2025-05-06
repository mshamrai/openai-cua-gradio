from macapptree import get_tree_screenshot
from macapptree.run import launch_app
import pyautogui
import subprocess
from PIL import Image
import time
import AppKit
import macapptree.apps as apps
import clipboard


class Environment:
    def __init__(self, app_bundle, output_dir):
        self.app_bundle = app_bundle
        self.output_dir = output_dir
        self.size = self._get_size()
        launch_app(self.app_bundle)

    def activate_window(self):
        workspace = AppKit.NSWorkspace.sharedWorkspace()

        app = apps.application_for_bundle(self.app_bundle, workspace)
        app.activateWithOptions_(AppKit.NSApplicationActivateIgnoringOtherApps)
        time.sleep(1)

    def _get_size(self):
        screenshot_file_path = self.output_dir / (str(-1) + ".png")
        COMMAND = 'screencapture -C -o "{filename}"'
        command = COMMAND.format(filename=screenshot_file_path)
        subprocess.getstatusoutput(command)
        screenshot = Image.open(screenshot_file_path)

        COMMAND = 'rm "{filename}"'
        command = COMMAND.format(filename=screenshot_file_path)
        subprocess.getstatusoutput(command)
        return screenshot.size[0] // 2, screenshot.size[1] // 2

    def get_whole_screenshot(self, step):
        self.activate_window()
        screenshot_file_path = self.output_dir / (str(step) + ".png")
        COMMAND = 'screencapture -C -o "{filename}"'
        command = COMMAND.format(filename=screenshot_file_path)
        subprocess.getstatusoutput(command)
        screenshot = Image.open(screenshot_file_path)
        return screenshot
    
    def handle_model_action(self, action):
        """
        Given a computer action (e.g., click, double_click, scroll, etc.),
        execute the corresponding operation.
        """
        action_type = action.type
        
        try:
            msg = ""
            match action_type:

                case "click":
                    x, y = action.x, action.y
                    button = action.button
                    msg = f"Action: click at ({x}, {y}) with button '{button}'"
                    # Not handling things like middle click, etc.
                    if button != "left" and button != "right":
                        button = "left"
                    self.click(x, y, button)

                case "scroll":
                    x, y = action.x, action.y
                    clicks = max(action.scroll_x, action.scroll_y)
                    msg = f"Action: scroll at ({x}, {y}) with {clicks} clicks"
                    self.scroll(clicks, x, y)

                case "keypress":
                    keys = action.keys
                    new_keys = []
                    for key in keys:
                        if key == "CMD":
                            new_keys.append("command")
                        new_keys.append(key.lower())
                    msg = f"Action: press key(s) {new_keys}"
                    self.press_key(new_keys)
                
                case "type":
                    text = action.text
                    msg = f"Action: type text: {text}"
                    self.type_text(text)
                
                case "wait":
                    msg = f"Action: wait"
                    time.sleep(2)

                case "screenshot":
                    # Nothing to do as screenshot is taken at each turn
                    msg = f"Action: screenshot"

                case "double_click":
                    x, y = action.x, action.y
                    msg = f"Action: double click at ({x}, {y})"
                    self.click(x, y, "left", clicks=2)

                case "drag":
                    path = action.path
                    x1, y1 = path[0].x, path[0].y
                    x2, y2 = path[1].x, path[1].y
                    msg = f"Action: drag from ({x1}, {y1}) to ({x2}, {y2})"
                    self.drag(x1, y1, x2, y2)

                # Handle other actions here

                case _:
                    msg = f"Unrecognized action: {action}"
                
            print(msg)
            return msg

        except Exception as e:
            print(f"Error handling action {action}: {e}")
    
    def click(self, x, y, button, clicks=1):
        pyautogui.click(x, y, button=button, clicks=clicks)
        # time.sleep(0.1)

    def scroll(self, clicks, x, y):
        pyautogui.scroll(clicks, x, y)
        # time.sleep(0.1)

    def type_text(self, text):
        # pyautogui.typewrite(text)
        clipboard.copy(text)
        pyautogui.hotkey('command', 'v', interval=0.1)

    def press_key(self, keys):
        # if key in pyautogui.KEYBOARD_KEYS:
        pyautogui.press(keys)
        # time.sleep(0.1)

    def move_cursor(self, x, y):
        pyautogui.moveTo(x, y)
        # time.sleep(0.1)

    def drag(self, x1, y1, x2, y2):
        pyautogui.moveTo(x1, y1)
        pyautogui.dragTo(x2, y2)