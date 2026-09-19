import os
import uuid

from django.utils.deconstruct import deconstructible


@deconstructible
class UUIDUploadTo:
    """`upload_to` that stores user uploads as <folder>/<uuid4>.<ext>.

    The user's original filename is dropped: it can leak personal info, hold
    odd characters, and collide with another user's file. Deconstructible so
    migrations can serialize it.
    """

    def __init__(self, folder):
        self.folder = folder

    def __call__(self, instance, filename):
        ext = os.path.splitext(filename)[1].lower()
        return f'{self.folder}/{uuid.uuid4().hex}{ext}'
