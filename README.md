# Posts and Comments Management API with AI Moderation

This project is a simple API for managing posts and comments,
equipped with AI-powered moderation and automatic response features. 
It is built using FastAPI and Pydantic for request handling 
and data validation.

# Set up project 
### 1) Firstly you should create .env file and fill it via example .env.sample
### 2) Set up Gemini API in Google Cloud Vertex AI
This project uses Gemini API in Google Cloud Vertex AI to moderate comments and posts. 
Also for automatic responses to comments
1) Firstly you should go to: https://cloud.google.com/vertex-ai?hl=en#build-with-gemini
2) Click on "Set up the Vertex AI Gemini API" button -> Documentation(left side bar) -> Set up a project and a development environment(Get started in the left sidebar)
3) Go to project selector -> Create project
4) Enable the Vertex AI API.
5) Google Cloud Console > IAM & Admin > Service Accounts > Create Service Account > Select roles: Vertex AI Service Agent, Vertex AI User
6) When you create Service Account, click on > click KEYS > Add Key > .json
7) Save json file to the root of the project and set in .env file: GOOGLE_APPLICATION_CREDENTIALS=path_to_your_file.json and GOOGLE_CLOUD_PROJECT_ID=id_of_google_gloud_project
### 3) To run project docker-compose:
    docker-compose up
#### To run project docker-compose if you want remake image:
    docker-compose up --build


