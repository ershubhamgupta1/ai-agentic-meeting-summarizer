---
title: sample-app
app_file: ui.py
sdk: gradio
sdk_version: 5.44.1
---



Steps to create app from scratch


Agentic AI setup

1) install cursor AI IDE
2) create directory in any folder for example : mkdir sample-agentic-app
3) install uv : curl -Ls https://astral.sh/uv/install.sh | sh (close the terminal and open it again to active it)
4) run uv sync to create .vnenv file: uv sync
5) create project.tom file that will work as package.json using : uv init
6) run this command to activate jupyter : source .venv/bin/activate  # macOS/Linux
7) create notebook file: either using : jupyter notebook or manually create file using cursor IDE
8) create agent.py file to actually put your code for production 
9) to install and add package in toml file: uv add OpenAI
10) create account on huggingface using url : https://huggingface.co and create token( click on avatar and list will be visible)
11) go to  cursor ide terminal and run the command: gradio deploy (it will ask some questions like token, space etc )
12) create requirments.txt and packages.txt for dependencies on hugging face otherwise at hugging face portal u will get module not found error: uv pip freeze > requirements.txt
13) crete packages.txt for dependencies like ffmpeg manually    
14) sometimes u get issue of dependency at hugging face due to some incompatible versions with other versions so u can try running these dependencies on local first otherwise it takes time if u directly do it on hugging face: python3 -m pip install -r requirements.txt

Notes

1) jupyter helps to give web interface to write run python code
2) just to install the package we can run : uv pip install OpenAI 
3) to install and add package in toml file: uv add OpenAI
4) notebook we use just for testing and run the code locally but usually not in prod
5) if you are facing dependency conflict/incompatible issue then run : python3 -m piptools compile requirements.in
6) install packages locally : python3 -m venv .venv && source .venv/bin/activate && uv pip install -r requirements.txt


commands:

1) Install dependencies on existing project: uv sync
2) Install ffmpeg: brew install ffmpeg
3) Activate Virtual Environment: source .venv/bin/activate

4) run project locally:  python3 ui.py

5) to install and add package in toml file: uv add OpenAI



TODO

Add agent that get the transcripted text and try to improvise the textRefiningTool.py