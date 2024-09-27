from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from .db.database import Base, engine
from .authentication.auth import auth_router
from .post.posts import post_router
from .error import add_error_handlers


version = "v1"
app = FastAPI(title="MyBlog", description="This is an api for MyBlog", version=version)
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(post_router)

add_error_handlers(app)


@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
def not_authenticated_error(request, exc):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "message": "Not authenticated. Kindly login to use this endpoint.",
            "error_code": "not_authenticated_error",
        },
    )


@app.get("/")
async def home():
    return {"message": "Hello! Welcome."}
