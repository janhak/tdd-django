from django.core.urlresolvers import resolve
from django.test import TestCase
from django.template.loader import render_to_string
from django.http import HttpRequest
from django.utils.html import escape

from lists.models import Item, List
from lists.views import home_page


class HomePageTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = home_page(request)
        expected_html = render_to_string('home.html', request=request)
        self.assertEqual(response.content.decode(), expected_html)


class NewListTest(TestCase):

    def test_saving_a_POST_request(self):
        self.client.post(
            '/lists/new',
            data={'item_text': 'A new list item'}
        )
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_redirects_after_POST(self):
        response = self.client.post(
            '/lists/new',
            data={'item_text': 'A new list item'}
        )
        new_list = List.objects.first()
        self.assertRedirects(response, '/lists/{}/'.format(new_list.id))

    def test_validation_errors_are_sent_back_to_home_page_template(self):
        response = self.client.post(
            '/lists/new',
            data={'item_text': ''}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        expected_error = escape("You can't have an empty list item")
        self.assertContains(response, expected_error)

    def test_invalid_list_items_are_not_saved(self):
        self.client.post('/lists/new', data={'item_text': ''})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)


class ListViewTest(TestCase):

    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get('/lists/{}/'.format(list_.id))
        self.assertTemplateUsed(response, 'list.html')

    def test_passes_correct_list_to_template(self):
        List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get('/lists/{}/'.format(correct_list.id))
        self.assertEqual(response.context['list'], correct_list)

    def test_displays_only_items_for_that_list(self):
        first_list = List.objects.create()
        Item.objects.create(text='First and foremost', list=first_list)
        Item.objects.create(text='Second but important', list=first_list)
        second_list = List.objects.create()
        Item.objects.create(text='Foo', list=second_list)
        Item.objects.create(text='Bar', list=second_list)

        response = self.client.get('/lists/{}/'.format(first_list.id))

        self.assertContains(response, 'First and foremost')
        self.assertContains(response, 'Second but important')
        self.assertNotContains(response, 'Foo')
        self.assertNotContains(response, 'Bar')

    def test_can_save_a_POST_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            '/lists/{}/'.format(correct_list.id),
            data={'item_text': 'New Item for Existing List'}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'New Item for Existing List')
        self.assertEqual(new_item.list, correct_list)

    def test_POST_redirects_to_list_view(self):
        List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            '/lists/{}/'.format(correct_list.id),
            data={'item_text': 'New Item for Existing List'}
        )

        self.assertRedirects(response, '/lists/{}/'.format(correct_list.id))

    def test_validation_errors_end_up_on_lists_page(self):
        list_ = List.objects.create()
        response = self.client.post(
            '/lists/{}/'.format(list_.id),
            data={'item_text': ''}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')
        expected_error = escape("You can't have an empty list item")
        self.assertContains(response, expected_error)


