from fastapi import UploadFile
from mega import Mega
import os, secrets
from .settings.config import config
from .error import ImageFormatNotSupportedException
from .db.models import ImageMapper
from sqlalchemy.orm import Session

mega = Mega()

EMAIL = config.MAIL_USERNAME
MEGA_PASSWORD = config.MEGA_PASSWORD
m = mega.login(EMAIL, MEGA_PASSWORD)


async def upload_image(file: UploadFile, folder_name: str, session: Session) -> str:

    ext = file.filename.split(".")[-1]
    if ext not in ["jpeg", "jpg", "png", "bmp", "webp", "ico"]:
        raise ImageFormatNotSupportedException(
            "The uploaded file should be on of: jpeg, jpg, png, bmp, webp, ico"
        )

    filename = secrets.token_hex(10) + "." + ext
    existing_folder = m.find(folder_name)
    folder_id = existing_folder[1]["h"]

    with open(filename, "wb") as f:
        f.write(await file.read())

    mega_file = m.upload(filename, dest=folder_id)
    public_url = m.get_upload_link(mega_file)
    os.remove(filename)

    image_key = None
    folder_id = existing_folder[1]["h"]
    files_in_folder = m.get_files_in_node(folder_id)
    for file_key, file_info in files_in_folder.items():
        if file_info["a"]["n"] == filename:
            image_key = file_key
            break

    add_image_mapper = ImageMapper(
        image_name=filename, image_id=image_key, image_url=public_url
    )
    session.add(add_image_mapper)
    session.commit()
    session.refresh(add_image_mapper)

    return public_url


def delete_image(link: str, session: Session):
    image_details = (
        session.query(ImageMapper).filter(ImageMapper.image_url == link).first()
    )
    if image_details:
        file_to_delete = image_details.image_id
        m.destroy(file_to_delete)
        session.delete(image_details)
        session.commit()
    else:
        return {"message": "Invalid link"}


# {
#     "Ijl2UYJS": {
#         "h": "Ijl2UYJS",
#         "p": "N20wmT6S",
#         "u": "wLINhigHy8I",
#         "t": 0,
#         "a": {"n": "cf77d786ece9a9409b86.jpeg"},
#         "k": (1554755573, 1984877389, 3547166626, 303148554),
#         "s": 8122,
#         "ts": 1727442966,
#         "iv": (2614343357, 1702654861, 0, 0),
#         "meta_mac": (2809556462, 1737281491),
#         "key": (
#             3346536776,
#             322085056,
#             1947933260,
#             1973248473,
#             2614343357,
#             1702654861,
#             2809556462,
#             1737281491,
#         ),
#     }
# }
