# built-in
import os
from io import BytesIO
# third-party module
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from PIL import Image
# project
from core.steam_api import SteamAPI


class ImageHandler:

    @staticmethod
    def _get_filename(target_id, is_bundle, target_type):
        category = 'bundle' if is_bundle else 'app'
        return f'steam_{category}_{target_id}_{target_type}.jpg'

    @staticmethod
    def _get_capsule(target_id, is_bundle, token):
        image_bytes = SteamAPI.get_target_capsule(
            target_id, is_bundle, token)
        if image_bytes is None:
            return None
        image_content = BytesIO(image_bytes)
        return Image.open(image_content)

    @staticmethod
    def _get_header(target_id, is_bundle, token):
        image_bytes = SteamAPI.get_target_header(
            target_id, is_bundle, token)
        if image_bytes is None:
            return None
        image_content = BytesIO(image_bytes)
        return Image.open(image_content)

    @classmethod
    def download_image(cls, target_id, is_bundle, token, filepath):
        capsule = cls._get_capsule(target_id, is_bundle, token)
        header = cls._get_header(target_id, is_bundle, token)
        if capsule:
            filename = cls._get_filename(target_id, is_bundle, 'capsule')
            file_directory = os.path.join(filepath, filename)
            capsule.save(file_directory)
        if header:
            filename = cls._get_filename(target_id, is_bundle, 'header')
            file_directory = os.path.join(filepath, filename)
            header.save(file_directory)
