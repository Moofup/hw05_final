import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..models import Group, Post, Comment

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Nameless')
        cls.group = Group.objects.create(
            title='Test-group',
            slug='t-group',
            description='test-description'
        )
        cls.post = Post.objects.create(
            text='Тестовый заголовок',
            author=cls.author,
        )

        @classmethod
        def tearDownClass(cls):
            super().tearDownClass()
            shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)

    def test_create_post(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        tested_post = Post.objects.order_by('id').last()

        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(
            group=tested_post.group,
            author=tested_post.author,
            text=tested_post.text).exists()
                        )

    def test_edit_post(self):
        old_post = self.post
        form_data = {
            'text': 'Новый тестовый текст',
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        new_post = Post.objects.get(id=self.post.id)
        self.assertNotEqual(old_post.text, new_post.text)

    def test_comment_nonauthorized_not_added(self):
        comments_count = Comment.objects.count()
        comment_form = {
            'text': 'Хлебом не корми, хлебом покорми'
        }
        self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=comment_form,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count)

    def test_comment_authorized_added(self):
        comments_count = Comment.objects.count()
        comment_form = {
            'text': 'Хлебом не корми, хлебом покорми'
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=comment_form,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
