from .base import FunctionalTest


class ItemValidationTest(FunctionalTest):

    def test_cannot_add_empty_list_items(self):
        # Edith goes to the home page and accidentally tries to submit
        # and empty list item. She hits Enter on the empty input box

        # The home page refreshes, and there is an error message
        # saying that list items can't be blank

        # She tries again with some text, which works now.

        # Perversely, she now decides to submit a second blank list item.

        # She receives a similar warning on the list page

        # And she can correct by filling some text in.
        self.fail('write me!')