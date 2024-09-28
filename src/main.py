from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from .db.database import Base, engine
from .authentication.auth import auth_router
from .post.posts import post_router
from .error import add_error_handlers

description = """
# MyBlog

Developed a role-based blogging platform with user and admin roles. MyBlog allows users to create, manage, and interact with blog posts while providing administrators the ability to manage users and content. The project uses **PostgreSQL** as the database (via **neon.tech**), **Mega.nz** for cloud storage, and is deployed on **Render**.

## Features

- **User Authentication:** Signup, login, password reset, profile management.
- **Blog Management:** Create, edit, and delete posts with hashtags, likes, and comments.
- **Administrative Control:** Admin can manage users (block, deactivate, delete).
- **Cloud Storage:** Integration with Mega.nz for file storage.
- **GitHub Repo:** https://github.com/SOO2023/myblog_api.

"""

version = "v1"
app = FastAPI(title="MyBlog", description=description, version=version)
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
