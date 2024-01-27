import subprocess

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core import lifespan


def create_app() -> FastAPI:
    # init FastAPI with lifespan
    app = FastAPI(lifespan=lifespan)
    # set CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include the routers
    from app.api import auth_router, identify_router
    app.include_router(auth_router)
    app.include_router(identify_router)

    return app


app = create_app()

# TODO: start in docker


def server_run(debug: bool = False, port: int = 5000):
    if not debug:
        # Run FastAPI with reload

        subprocess.Popen(["uvicorn", "app:app", "--host",
                          "0.0.0.0", "--port", str(port), "--reload"])
    else:

        uvicorn.run(app, host='0.0.0.0', port=port)


if __name__ == "__main__":
    server_run(True)
