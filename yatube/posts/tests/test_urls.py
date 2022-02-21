from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def test_about_urls_uses_correct_templates(self):
        templates_url_names_quest = (
            '/',
            '/about/author/',
            '/about/tech/'
        )
        for address in templates_url_names_quest:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK
                )


class PostURLTests(TestCase):
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

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names_guest = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post.author.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/unexisting_page/': 'lol.html',
        }
        for address, template in templates_url_names_guest.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                if address == '/unexisting_page/':
                    self.assertEqual(
                        response.status_code,
                        HTTPStatus.NOT_FOUND
                    )
                else:
                    self.assertEqual(
                        response.status_code,
                        HTTPStatus.OK
                    )

        templates_url_names_authorized = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.author.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names_authorized.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                if address == '/unexisting_page/':
                    self.assertEqual(
                        response.status_code,
                        HTTPStatus.NOT_FOUND
                    )
                else:
                    self.assertEqual(
                        response.status_code,
                        HTTPStatus.OK
                    )

    def test_comment_field_exists_at_desired_location_anonymous(self):
        response = self.client.get('/posts/1/comment/')
        self.assertEqual(response.status_code, 302)
