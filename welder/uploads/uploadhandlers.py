from django.core.files.uploadhandler import MemoryFileUploadHandler
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.core.files.uploadedfile import (
  InMemoryUploadedFile, TemporaryUploadedFile,
)

class DirectoryUploadHandler(MemoryFileUploadHandler):
  def file_complete(self, file_size):

    if not self.activated:
      return

    self.file.seek(0)
    return InMemoryUploadedFile(
      file=self.file,
      field_name=self.field_name,
      name=self.file_name,
      content_type=self.content_type,
      size=file_size,
      charset=self.charset,
      content_type_extra=self.file_name
    )

class DirectoryUploadHandlerBig(TemporaryFileUploadHandler):
  def file_complete(self, file_size):
    self.file.seek(0)
    self.file.size = file_size
    self.file.content_type_extra = self.file_name
    return self.file
