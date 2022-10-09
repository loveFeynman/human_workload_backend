import gradio as gr
from fastapi import HTTPException, FastAPI, Response, Depends
from pydantic import BaseModel
import human
import docker
from fastapi.middleware.cors import CORSMiddleware

import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CUSTOM_PATH = "/gradio"

pubkey = ""
workload_id = ""
mnemonic =  "sound prevent lock blame review horn junk cupboard enrich south warfare visit"
result = {}

class Data(BaseModel):
    workload_id: str
    signature: str
    pubkey: str

@app.get("/")
def read_main():
    print("read main")

@app.post("/set-state/")
def set_gradio(data: Data):
    global app
    print(data.signature, data.workload_id, data.pubkey)
    inputs = [
        gr.components.Textbox(placeholder = "input to the AI algorithm", label = "Input"),
        gr.JSON({
            "signature": data.signature
        }, visible = False),
        gr.JSON({
            "workload_id": data.workload_id
        }, visible = False),
        gr.JSON({
            "public_key": data.pubkey
        }, visible = False)
    ]
        
    io = gr.Interface(
        fn = execute_algorithm,
        inputs = inputs,
        outputs = gr.components.Textbox(label = "Output")
    )
        
    path=CUSTOM_PATH+"/"+data.signature
    app = gr.mount_gradio_app(app, io, path=path)
    return path
    

def execute_algorithm(inputs, signature_hash, workload_id, pubkey):
    workload = workload_id['workload_id']
    signature = signature_hash['signature']
    pub_key = pubkey['public_key']

    result = human.query_execution_status(workload, signature, pub_key)
    try:
        # if result['status'] == 'Running':
            try:
                docker_client = docker.from_env() 
                print(docker_client)

                try:
                    container = docker_client.containers.run("lovefeynman/aitest", inputs)
                    docker_client.containers.prune()
                    # container = docker_client.containers.run("lovefeynman/aitest", inputs)
                except:
                    return "running algorithm fails"

                try:
                    human.update_status(workload, mnemonic, signature, pub_key)
                except:
                    return "update status fails"

                return int(container)
            except:
                return {"error": "docker image running failed"}
        # else:
        #     return "error"
    except:
        return "error:no such workload"
