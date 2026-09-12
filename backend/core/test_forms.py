from django.test import TestCase
from .forms import PostUploadForm, SearchForm
from django.core.files.uploadedfile import SimpleUploadedFile


class TestForms(TestCase):

    # Minimal valid 1x1 GIF payload — Django's ImageField validates actual
    # image content (via Pillow), so plain bytes like b'file_content' fail.
    VALID_GIF = (
        b'GIF87a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00'
        b'\x00\x02\x02D\x01\x00;'
    )

    def test_PostUploadForm_valid_data(self):
        image = SimpleUploadedFile(
            'test.gif', self.VALID_GIF, content_type='image/gif')
        form = PostUploadForm(data={'caption': 'hello'}, files={'image': image})
        self.assertTrue(form.is_valid())

    def test_PostUploadForm_no_data(self):
        form = PostUploadForm(data={})
        self.assertFalse(form.is_valid())
        # Both 'image' and 'caption' are required on this form (the form
        # re-declares caption without required=False, unlike the model).
        self.assertEqual(len(form.errors), 2)

    def test_SearchForm_valid_data(self):
        form = SearchForm(data={'search': 'arash'})
        self.assertTrue(form.is_valid())

    def test_SearchForm_no_data(self):
        form = SearchForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
