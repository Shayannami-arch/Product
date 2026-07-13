from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.core.window import Window

import os
import json
from datetime import datetime


class ProductApp(App):
    def build(self):
        self.title = "Product App"
        self.products = []
        self.selected_product_id = None

        self.data_file = os.path.join(self.user_data_dir, "products.json")
        self.load_products()

        root = BoxLayout(orientation="vertical", padding=10, spacing=8)

        title = Label(
            text="Product Management App",
            size_hint_y=None,
            height=42,
            font_size=22
        )
        root.add_widget(title)

        form = GridLayout(cols=2, spacing=6, size_hint_y=None, height=250)

        self.product_id_input = TextInput(multiline=False, input_filter="int")
        self.name_input = TextInput(multiline=False)
        self.brand_input = TextInput(multiline=False)
        self.expire_date_input = TextInput(multiline=False, hint_text="YYYY-MM-DD")
        self.buy_price_input = TextInput(multiline=False, input_filter="int")

        form.add_widget(Label(text="Product ID"))
        form.add_widget(self.product_id_input)

        form.add_widget(Label(text="Name"))
        form.add_widget(self.name_input)

        form.add_widget(Label(text="Brand"))
        form.add_widget(self.brand_input)

        form.add_widget(Label(text="Expire Date"))
        form.add_widget(self.expire_date_input)

        form.add_widget(Label(text="Buy Price"))
        form.add_widget(self.buy_price_input)

        root.add_widget(form)

        buttons = GridLayout(cols=4, spacing=6, size_hint_y=None, height=45)

        save_btn = Button(text="Save")
        edit_btn = Button(text="Edit")
        remove_btn = Button(text="Remove")
        reset_btn = Button(text="Reset")

        save_btn.bind(on_press=self.save_product)
        edit_btn.bind(on_press=self.edit_product)
        remove_btn.bind(on_press=self.remove_product)
        reset_btn.bind(on_press=self.reset_form)

        buttons.add_widget(save_btn)
        buttons.add_widget(edit_btn)
        buttons.add_widget(remove_btn)
        buttons.add_widget(reset_btn)

        root.add_widget(buttons)

        search_title = Label(
            text="Search",
            size_hint_y=None,
            height=30,
            font_size=18
        )
        root.add_widget(search_title)

        search_box = GridLayout(cols=2, spacing=6, size_hint_y=None, height=150)

        self.search_id_input = TextInput(multiline=False, input_filter="int")
        self.search_name_input = TextInput(multiline=False)
        self.search_brand_input = TextInput(multiline=False)
        self.search_price_input = TextInput(multiline=False, input_filter="int")

        search_box.add_widget(Label(text="Search ID"))
        search_box.add_widget(self.search_id_input)

        search_box.add_widget(Label(text="Search Name"))
        search_box.add_widget(self.search_name_input)

        search_box.add_widget(Label(text="Search Brand"))
        search_box.add_widget(self.search_brand_input)

        search_box.add_widget(Label(text="Search Price"))
        search_box.add_widget(self.search_price_input)

        root.add_widget(search_box)

        search_buttons = GridLayout(cols=2, spacing=6, size_hint_y=None, height=45)

        search_btn = Button(text="Search")
        show_all_btn = Button(text="Show All")

        search_btn.bind(on_press=self.search_products)
        show_all_btn.bind(on_press=self.show_all_products)

        search_buttons.add_widget(search_btn)
        search_buttons.add_widget(show_all_btn)

        root.add_widget(search_buttons)

        list_title = Label(
            text="Products List",
            size_hint_y=None,
            height=30,
            font_size=18
        )
        root.add_widget(list_title)

        self.scroll = ScrollView()
        self.list_box = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        self.scroll.add_widget(self.list_box)
        root.add_widget(self.scroll)

        self.refresh_list(self.products)
        return root

    def show_message(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.85, 0.35)
        )
        popup.open()

    def load_products(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.products = json.load(f)
            else:
                self.products = []
        except Exception:
            self.products = []

    def save_products_to_file(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.products, f, ensure_ascii=False, indent=2)

    def get_form_data(self):
        product_id_text = self.product_id_input.text.strip()
        name = self.name_input.text.strip()
        brand = self.brand_input.text.strip()
        expire_date = self.expire_date_input.text.strip()
        buy_price_text = self.buy_price_input.text.strip()

        if not product_id_text:
            raise ValueError("Product ID is required.")
        if not name:
            raise ValueError("Name is required.")
        if not brand:
            raise ValueError("Brand is required.")
        if not expire_date:
            raise ValueError("Expire Date is required.")
        if not buy_price_text:
            raise ValueError("Buy Price is required.")

        product_id = int(product_id_text)
        buy_price = int(buy_price_text)

        if product_id <= 0:
            raise ValueError("Product ID must be positive.")

        if buy_price <= 0:
            raise ValueError("Buy Price must be positive.")

        try:
            datetime.strptime(expire_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Expire Date format must be YYYY-MM-DD.")

        return {
            "product_id": product_id,
            "name": name,
            "brand": brand,
            "expire_date": expire_date,
            "buy_price": buy_price
        }

    def save_product(self, instance):
        try:
            product = self.get_form_data()

            for item in self.products:
                if item["product_id"] == product["product_id"]:
                    self.show_message("Error", "This Product ID already exists.")
                    return

            self.products.append(product)
            self.save_products_to_file()
            self.refresh_list(self.products)
            self.reset_form()
            self.show_message("Success", "Product saved successfully.")

        except Exception as e:
            self.show_message("Error", str(e))

    def edit_product(self, instance):
        try:
            product = self.get_form_data()

            for index, item in enumerate(self.products):
                if item["product_id"] == product["product_id"]:
                    self.products[index] = product
                    self.save_products_to_file()
                    self.refresh_list(self.products)
                    self.reset_form()
                    self.show_message("Success", "Product edited successfully.")
                    return

            self.show_message("Error", "Product ID not found.")

        except Exception as e:
            self.show_message("Error", str(e))

    def remove_product(self, instance):
        try:
            product_id_text = self.product_id_input.text.strip()
            if not product_id_text:
                self.show_message("Error", "Enter Product ID to remove.")
                return

            product_id = int(product_id_text)

            new_products = [
                item for item in self.products
                if item["product_id"] != product_id
            ]

            if len(new_products) == len(self.products):
                self.show_message("Error", "Product ID not found.")
                return

            self.products = new_products
            self.save_products_to_file()
            self.refresh_list(self.products)
            self.reset_form()
            self.show_message("Success", "Product removed successfully.")

        except Exception as e:
            self.show_message("Error", str(e))

    def search_products(self, instance):
        result = self.products

        search_id = self.search_id_input.text.strip()
        search_name = self.search_name_input.text.strip().lower()
        search_brand = self.search_brand_input.text.strip().lower()
        search_price = self.search_price_input.text.strip()

        if search_id:
            result = [
                item for item in result
                if str(item["product_id"]).startswith(search_id)
            ]

        if search_name:
            result = [
                item for item in result
                if search_name in item["name"].lower()
            ]

        if search_brand:
            result = [
                item for item in result
                if search_brand in item["brand"].lower()
            ]

        if search_price:
            result = [
                item for item in result
                if str(item["buy_price"]).startswith(search_price)
            ]

        self.refresh_list(result)

    def show_all_products(self, instance):
        self.search_id_input.text = ""
        self.search_name_input.text = ""
        self.search_brand_input.text = ""
        self.search_price_input.text = ""
        self.refresh_list(self.products)

    def reset_form(self, instance=None):
        self.product_id_input.text = ""
        self.name_input.text = ""
        self.brand_input.text = ""
        self.expire_date_input.text = ""
        self.buy_price_input.text = ""
        self.selected_product_id = None

    def select_product(self, product):
        self.selected_product_id = product["product_id"]
        self.product_id_input.text = str(product["product_id"])
        self.name_input.text = product["name"]
        self.brand_input.text = product["brand"]
        self.expire_date_input.text = product["expire_date"]
        self.buy_price_input.text = str(product["buy_price"])

    def refresh_list(self, products):
        self.list_box.clear_widgets()

        if not products:
            self.list_box.add_widget(
                Label(
                    text="No products found.",
                    size_hint_y=None,
                    height=40
                )
            )
            return

        for product in products:
            text = (
                f'ID: {product["product_id"]} | '
                f'Name: {product["name"]} | '
                f'Brand: {product["brand"]} | '
                f'Date: {product["expire_date"]} | '
                f'Price: {product["buy_price"]}'
            )

            btn = Button(
                text=text,
                size_hint_y=None,
                height=50
            )
            btn.bind(on_press=lambda instance, p=product: self.select_product(p))
            self.list_box.add_widget(btn)


if __name__ == "__main__":
    ProductApp().run()