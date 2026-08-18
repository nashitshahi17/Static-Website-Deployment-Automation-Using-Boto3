import json
from pathlib import Path
from .logger import logger

class StateManager:
    def __init__(self,state_file="deployment_state.json"):
        self.state_file = Path(state_file)

    def load(self):
        if not self.state_file.exists():
            return {}

        with self.state_file.open('r',encoding='utf-8') as file:
            return json.load(file)

    def save(self,state):
        with self.state_file.open('w',encoding='utf-8') as file:
            json.dump(state,file,indent=4)

    def clear(self):
        if self.state_file.exists():
            self.state_file.unlink()

    def clear_state(self):
        self.save_state({})
        logger.info("Deployment state cleared.")
