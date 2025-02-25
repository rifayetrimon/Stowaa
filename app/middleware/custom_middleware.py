from fastapi.middleware.cors import CORSMiddleware

# def add_cors_middleware(app):
#     origins = [
#         "http://localhost:3000",  # React or Vue development server
#         "http://localhost:8000",  # FastAPI server (if testing from same machine)
#         "http://localhost:5000",  # FastAPI server (if testing from same machine)
#         "https://your-frontend-domain.com",  # Production frontend domain
#     ]

#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=origins,
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )



def add_cors_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
        allow_headers=["*"],  # Allow all headers
    )