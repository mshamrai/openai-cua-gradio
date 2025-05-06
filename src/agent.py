from openai import OpenAI


class OpenAIComputerUseAgent:
    def __init__(self, display_size):
        self.display_size = display_size
        self.client = OpenAI()

    def get_initial_action(self, task, screenshot_base64, last_response_id):
        content = [
            {
                "type": "input_text",
                "text": task
            },
        ]
        if not last_response_id:
            content.append({
                "type": "input_image",
                "image_url": f"data:image/png;base64,{screenshot_base64}"
            })

        response = self.client.responses.create(
            model="computer-use-preview",
            previous_response_id=last_response_id,
            tools=[{
                "type": "computer_use_preview",
                "display_width": self.display_size[0],
                "display_height": self.display_size[1],
                "environment": "mac"
            }],
            input=[
                {
                    "role": "user",
                    "content": content
                },
                
            ],
            reasoning={
                "generate_summary": "concise",
            },
            truncation="auto"
        )
        return response
    
    def get_action(self, response_id, last_call_id, screenshot_base64, pending_safety_checks):
        # Send the screenshot back as a computer_call_output
        response = self.client.responses.create(
            model="computer-use-preview",
            previous_response_id=response_id,
            tools=[
                {
                    "type": "computer_use_preview",
                    "display_width": self.display_size[0],
                    "display_height": self.display_size[1],
                    "environment": "mac"
                }
            ],
            input=[
                {
                    "call_id": last_call_id,
                    "type": "computer_call_output",
                    "acknowledged_safety_checks": pending_safety_checks,
                    "output": {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{screenshot_base64}"
                    }
                }
            ],
            truncation="auto"
        )
        return response


if __name__ == '__main__':
    agent = OpenAIComputerUseAgent()
    print(agent.get_response())