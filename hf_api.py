from huggingface_hub.inference_api import InferenceApi
from dotenv import load_dotenv
import os
import time
import json
import requests
import io
import uuid
from pathlib import Path
from PIL import Image
from datetime import datetime

load_dotenv()
HF_BASE_URL = "https://api-inference.huggingface.co/models"

class HF_API:
    def __init__(self, repo_id, output_path="./generated_images"):
        self.repo_id = repo_id
        self.session = requests.Session()
        #token = os.getenv("hf_token")
        self.session.headers.update({'Authorization': f'Bearer {os.getenv("hf_token")}'})
        self.output_path = output_path

    def _make_fpath(self, image_name):
        self.dir = str(datetime.now().strftime("%y_%m_%d_%H_%M_"))
        Path(self.output_path).joinpath(self.dir).mkdir(parents=True, exist_ok=True)
        self._fpath = Path(self.output_path).joinpath(self.dir,image_name)

    def _bytes_to_image(self,bytes):
        image = Image.open(io.BytesIO(bytes))
        self.creation_id = str(uuid.uuid4())
        self.image_name = self.creation_id + ".png"
        self._make_fpath(self.image_name)
        image.save(self._fpath, "PNG")

    def generate(self, query):
        data = json.dumps(query)
        data = {
            "inputs": query,
            "use_cache": False
        }
        response = self.session.post(f"{HF_BASE_URL}/{self.repo_id}", data=data)
        while True:
            try:
                response = self.session.post(f"{HF_BASE_URL}/{self.repo_id}", data=data)
                response.raise_for_status()
            except requests.exceptions.HTTPError as err:
                # if the model is still loading, the endpoint will return a 503 status code
                if response.status_code == 503:
                    print("Model is still loading, waiting for {} seconds before retrying.".format(30))
                    self.status = "Model is still loading, waiting for {} seconds before retrying.".format(30)
                    time.sleep(30)
                elif response.status_code == 429:
                    print(f'HTTP error occurred: {err}')
                    print("Too many requests, waiting for {} seconds before retrying.".format(30))
                    self.status = "Too many requests, waiting for {} seconds before retrying.".format(30)
                    time.sleep(30)
            except Exception as err:
                print(f'Other error occurred: {err}') 
                self.status = "Unknown error occurred: {err}"
            else:
                print("Success!")
                self._bytes_to_image(response.content)
                prompt_path = Path(self.output_path).joinpath(self.dir,self.creation_id + ".txt")
                with open(prompt_path, "w") as f:
                    f.write(query)
                self.status = "Success"
                break
            