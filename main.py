from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.storage.jsonstore import JsonStore
from kivy.properties import StringProperty, NumericProperty

import os


# ---------- Persian text helper ----------
try:
    import arabic_reshaper
    from bidi.algorithm import get_display

    def fa(text):
        return get_display(arabic_reshaper.reshape(str(text)))
except Exception:
    def fa(text):
        return str(text)


# ---------- Colors ----------
NAVY_950 = (0.05, 0.10, 0.18, 1)
NAVY_900 = (0.07, 0.13, 0.23, 1)
NAVY_800 = (0.10, 0.19, 0.33, 1)
NAVY_700 = (0.14, 0.25, 0.43, 1)
PAPER = (0.96, 0.95, 0.90, 1)
MUTED = (0.60, 0.65, 0.72, 1)
TEAL = (0.18, 0.79, 0.72, 1)
MUSTARD = (0.94, 0.66, 0.22, 1)
DANGER = (0.89, 0.38, 0.31, 1)
WHITE_SOFT = (1, 1, 1, 0.08)


Window.clearcolor = NAVY_950


class Card(BoxLayout):
    def __init__(self, bg=NAVY_900, radius=14, **kwargs):
        super().__init__(**kwargs)
        self.bg = bg
        self.radius = radius
        self.padding = dp(14)
        self.spacing = dp(8)
        with self.canvas.before:
            Color(*self.bg)
            self.rect = RoundedRectangle(radius=[self.radius], pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class StatCard(Card):
    def __init__(self, title, value, subtitle, accent=TEAL, **kwargs):
        super().__init__(orientation="vertical", bg=NAVY_900, size_hint_y=None, height=dp(105), **kwargs)

        self.add_widget(Label(
            text=fa(title),
            color=MUTED,
            font_size=dp(12),
            halign="right",
            size_hint_y=None,
            height=dp(24),
            text_size=(self.width, None)
        ))

        self.value_label = Label(
            text=fa(value),
            color=accent,
            font_size=dp(26),
            bold=True,
            halign="right",
            size_hint_y=None,
            height=dp(36)
        )
        self.add_widget(self.value_label)

        self.add_widget(Label(
            text=fa(subtitle),
            color=MUTED,
            font_size=dp(11),
            halign="right",
            size_hint_y=None,
            height=dp(24)
        ))


class ProductCard(Card):
    product_id = NumericProperty(0)

    def __init__(self, product, edit_callback, delete_callback, **kwargs):
        super().__init__(orientation="vertical", bg=NAVY_800, size_hint_y=None, height=dp(190), **kwargs)
        self.product = product
        self.product_id = product.get("id", 0)
        self.edit_callback = edit_callback
        self.delete_callback = delete_callback

        top = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(28), spacing=dp(8))

        category = Label(
            text=fa(product.get("category", "عمومی")),
            color=MUSTARD,
            font_size=dp(11),
            size_hint_x=0.55,
            halign="right"
        )

        warning = ""
        try:
            if int(product.get("qty", 0)) <= int(product.get("min_qty", 0)):
                warning = "کمبود"
        except Exception:
            warning = ""

        low = Label(
            text=fa(warning),
            color=DANGER,
            font_size=dp(11),
            size_hint_x=0.45,
            halign="left"
        )

        top.add_widget(low)
        top.add_widget(category)
        self.add_widget(top)

        name = Label(
            text=fa(product.get("name", "بدون نام")),
            color=PAPER,
            font_size=dp(16),
            bold=True,
            halign="right",
            size_hint_y=None,
            height=dp(32)
        )
        self.add_widget(name)

        sku = Label(
            text=fa("کد کالا: " + str(product.get("sku", "-"))),
            color=MUTED,
            font_size=dp(12),
            halign="right",
            size_hint_y=None,
            height=dp(24)
        )
        self.add_widget(sku)

        brand = Label(
            text=fa("برند: " + str(product.get("brand", "-"))),
            color=MUTED,
            font_size=dp(12),
            halign="right",
            size_hint_y=None,
            height=dp(24)
        )
        self.add_widget(brand)

        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(32))

        price = Label(
            text=fa(f"{int(product.get('buy_price', 0)):,} تومان"),
            color=TEAL,
            bold=True,
            font_size=dp(13),
            halign="left"
        )

        qty = Label(
            text=fa(f"موجودی: {product.get('qty', 0)}"),
            color=PAPER,
            font_size=dp(13),
            halign="right"
        )

        row.add_widget(price)
        row.add_widget(qty)
        self.add_widget(row)

        actions = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(38), spacing=dp(8))

        btn_delete = Button(
            text=fa("حذف"),
            background_normal="",
            background_color=(0.55, 0.18, 0.16, 1),
            color=PAPER,
            font_size=dp(12)
        )
        btn_delete.bind(on_press=lambda x: self.delete_callback(self.product_id))

        btn_edit = Button(
            text=fa("ویرایش"),
            background_normal="",
            background_color=NAVY_700,
            color=PAPER,
            font_size=dp(12)
        )
        btn_edit.bind(on_press=lambda x: self.edit_callback(self.product_id))

        actions.add_widget(btn_delete)
        actions.add_widget(btn_edit)
        self.add_widget(actions)


class ProductApp(App):
    def build(self):
        self.title = "ProductApp"

        self.store = JsonStore("products_data.json")
        self.products = []
        self.next_id = 1
        self.current_page = "dashboard"

        self.load_data()

        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        root.canvas.before.clear()
        with root.canvas.before:
            Color(*NAVY_950)
            self.bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self.update_bg, size=self.update_bg)

        self.header = self.make_header()
        root.add_widget(self.header)

        self.navbar = self.make_navbar()
        root.add_widget(self.navbar)

        self.content = BoxLayout(orientation="vertical")
        root.add_widget(self.content)

        self.render_dashboard()
        return root

    def update_bg(self, instance, *args):
        self.bg.pos = instance.pos
        self.bg.size = instance.size

    # ---------- Data ----------
    def load_data(self):
        if self.store.exists("products"):
            data = self.store.get("products")
            self.products = data.get("items", [])
            self.next_id = data.get("next_id", 1)
        else:
            self.products = [
                {
                    "id": 1,
                    "sku": "PRD-1001",
                    "name": "هدفون بی‌سیم",
                    "brand": "Sony",
                    "category": "الکترونیک",
                    "expire": "ندارد",
                    "buy_price": 1250000,
                    "qty": 14,
                    "min_qty": 5
                },
                {
                    "id": 2,
                    "sku": "PRD-2001",
                    "name": "قهوه ترک",
                    "brand": "Mehmet",
                    "category": "خوراکی",
                    "expire": "2026-12-30",
                    "buy_price": 210000,
                    "qty": 3,
                    "min_qty": 8
                }
            ]
            self.next_id = 3
            self.save_data()

    def save_data(self):
        self.store.put("products", items=self.products, next_id=self.next_id)

    # ---------- Header ----------
    def make_header(self):
        box = Card(orientation="horizontal", bg=NAVY_900, size_hint_y=None, height=dp(78), radius=16)

        title_box = BoxLayout(orientation="vertical")

        title = Label(
            text=fa("انبارک"),
            color=PAPER,
            bold=True,
            font_size=dp(24),
            halign="right",
            size_hint_y=0.6
        )

        subtitle = Label(
            text=fa("سامانه مدیریت محصولات"),
            color=MUTED,
            font_size=dp(12),
            halign="right",
            size_hint_y=0.4
        )

        title_box.add_widget(title)
        title_box.add_widget(subtitle)

        mark = Label(
            text=fa("اک"),
            color=NAVY_950,
            bold=True,
            font_size=dp(18),
            size_hint_x=None,
            width=dp(58)
        )
        with mark.canvas.before:
            Color(*TEAL)
            mark.bg = RoundedRectangle(radius=[12], pos=mark.pos, size=mark.size)
        mark.bind(pos=lambda i, v: setattr(mark.bg, "pos", i.pos))
        mark.bind(size=lambda i, v: setattr(mark.bg, "size", i.size))

        box.add_widget(title_box)
        box.add_widget(mark)
        return box

    def make_navbar(self):
        bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(8))

        buttons = [
            ("داشبورد", "dashboard"),
            ("محصولات", "products"),
            ("افزودن", "add"),
        ]

        for text, page in buttons:
            btn = Button(
                text=fa(text),
                background_normal="",
                background_color=TEAL if page == "add" else NAVY_800,
                color=NAVY_950 if page == "add" else PAPER,
                bold=True,
                font_size=dp(13)
            )
            if page == "dashboard":
                btn.bind(on_press=lambda x: self.render_dashboard())
            elif page == "products":
                btn.bind(on_press=lambda x: self.render_products())
            else:
                btn.bind(on_press=lambda x: self.open_product_form())
            bar.add_widget(btn)

        return bar

    def clear_content(self):
        self.content.clear_widgets()

    # ---------- Dashboard ----------
    def render_dashboard(self):
        self.current_page = "dashboard"
        self.clear_content()

        total = len(self.products)
        total_value = sum(int(p.get("buy_price", 0)) * int(p.get("qty", 0)) for p in self.products)
        low_count = sum(1 for p in self.products if int(p.get("qty", 0)) <= int(p.get("min_qty", 0)))
        categories = len(set(p.get("category", "عمومی") for p in self.products))

        scroll = ScrollView()
        body = GridLayout(cols=1, spacing=dp(12), size_hint_y=None)
        body.bind(minimum_height=body.setter("height"))

        body.add_widget(StatCard("تعداد محصولات", str(total), "قلم کالای ثبت‌شده", TEAL))
        body.add_widget(StatCard("ارزش کل انبار", f"{total_value:,}", "تومان", MUSTARD))
        body.add_widget(StatCard("هشدار موجودی کم", str(low_count), "کالا زیر آستانه", DANGER))
        body.add_widget(StatCard("دسته‌بندی‌ها", str(categories), "دسته فعال", TEAL))

        title = Label(
            text=fa("محصولات با موجودی کم"),
            color=PAPER,
            bold=True,
            font_size=dp(16),
            halign="right",
            size_hint_y=None,
            height=dp(40)
        )
        body.add_widget(title)

        low_items = [p for p in self.products if int(p.get("qty", 0)) <= int(p.get("min_qty", 0))]
        if not low_items:
            body.add_widget(CardLabel("هیچ کالایی زیر آستانه موجودی نیست"))
        else:
            for p in low_items:
                body.add_widget(CardLabel(f"{p.get('name')} | موجودی: {p.get('qty')} | حداقل: {p.get('min_qty')}", danger=True))

        scroll.add_widget(body)
        self.content.add_widget(scroll)

    # ---------- Products ----------
    def render_products(self):
        self.current_page = "products"
        self.clear_content()

        search = TextInput(
            hint_text=fa("جستجوی نام، کد کالا یا برند..."),
            multiline=False,
            size_hint_y=None,
            height=dp(48),
            background_color=NAVY_800,
            foreground_color=PAPER,
            hint_text_color=MUTED,
            cursor_color=TEAL,
            padding=[dp(12), dp(12)]
        )
        self.content.add_widget(search)

        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=dp(12), size_hint_y=None, padding=[0, dp(12), 0, dp(12)])
        grid.bind(minimum_height=grid.setter("height"))

        def draw_products(query=""):
            grid.clear_widgets()
            q = query.strip().lower()

            data = []
            for p in self.products:
                text = f"{p.get('name')} {p.get('sku')} {p.get('brand')} {p.get('category')}".lower()
                if not q or q in text:
                    data.append(p)

            if not data:
                grid.add_widget(CardLabel("محصولی پیدا نشد"))
            else:
                for p in data:
                    grid.add_widget(ProductCard(p, self.open_product_form, self.delete_product))

        search.bind(text=lambda instance, value: draw_products(value))
        draw_products()

        scroll.add_widget(grid)
        self.content.add_widget(scroll)

    # ---------- Form ----------
    def open_product_form(self, product_id=None):
        product = None
        if product_id:
            product = next((p for p in self.products if p.get("id") == product_id), None)

        layout = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(12))

        title = fa("ویرایش محصول" if product else "افزودن محصول جدید")

        fields = {}

        def input_field(key, hint, value=""):
            ti = TextInput(
                hint_text=fa(hint),
                text=str(value),
                multiline=False,
                size_hint_y=None,
                height=dp(46),
                background_color=NAVY_800,
                foreground_color=PAPER,
                hint_text_color=MUTED,
                cursor_color=TEAL,
                padding=[dp(10), dp(10)]
            )
            fields[key] = ti
            layout.add_widget(ti)

        input_field("sku", "کد کالا", product.get("sku", "") if product else "")
        input_field("name", "نام محصول", product.get("name", "") if product else "")
        input_field("brand", "برند", product.get("brand", "") if product else "")
        input_field("category", "دسته‌بندی", product.get("category", "") if product else "عمومی")
        input_field("expire", "تاریخ انقضا", product.get("expire", "") if product else "")
        input_field("buy_price", "قیمت خرید", product.get("buy_price", "") if product else "")
        input_field("qty", "موجودی فعلی", product.get("qty", "") if product else "")
        input_field("min_qty", "حداقل موجودی", product.get("min_qty", "5") if product else "5")

        buttons = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(8))

        cancel = Button(
            text=fa("انصراف"),
            background_normal="",
            background_color=NAVY_700,
            color=PAPER
        )

        save = Button(
            text=fa("ذخیره محصول"),
            background_normal="",
            background_color=TEAL,
            color=NAVY_950,
            bold=True
        )

        buttons.add_widget(cancel)
        buttons.add_widget(save)
        layout.add_widget(buttons)

        popup = Popup(
            title=title,
            content=layout,
            size_hint=(0.92, 0.86),
            background_color=NAVY_900,
            title_color=PAPER,
            separator_color=TEAL
        )

        cancel.bind(on_press=popup.dismiss)

        def save_item(*args):
            sku = fields["sku"].text.strip()
            name = fields["name"].text.strip()

            if not sku or not name:
                self.show_message("کد کالا و نام محصول الزامی است")
                return

            try:
                buy_price = int(fields["buy_price"].text.strip() or 0)
                qty = int(fields["qty"].text.strip() or 0)
                min_qty = int(fields["min_qty"].text.strip() or 0)
            except Exception:
                self.show_message("قیمت و موجودی باید عدد باشند")
                return

            data = {
                "sku": sku,
                "name": name,
                "brand": fields["brand"].text.strip(),
                "category": fields["category"].text.strip() or "عمومی",
                "expire": fields["expire"].text.strip(),
                "buy_price": buy_price,
                "qty": qty,
                "min_qty": min_qty
            }

            if product:
                product.update(data)
            else:
                data["id"] = self.next_id
                self.next_id += 1
                self.products.append(data)

            self.save_data()
            popup.dismiss()
            self.render_products()
            self.show_message("محصول ذخیره شد")

        save.bind(on_press=save_item)
        popup.open()

    def delete_product(self, product_id):
        self.products = [p for p in self.products if p.get("id") != product_id]
        self.save_data()
        self.render_products()
        self.show_message("محصول حذف شد")

    def show_message(self, message):
        popup = Popup(
            title=fa("پیام"),
            content=Label(text=fa(message), color=PAPER, font_size=dp(15)),
            size_hint=(0.78, 0.28),
            background_color=NAVY_900,
            title_color=PAPER,
            separator_color=TEAL
        )
        popup.open()


class CardLabel(Card):
    def __init__(self, text, danger=False, **kwargs):
        super().__init__(orientation="vertical", bg=NAVY_800, size_hint_y=None, height=dp(58), **kwargs)
        self.add_widget(Label(
            text=fa(text),
            color=DANGER if danger else PAPER,
            font_size=dp(13),
            halign="right",
            valign="middle"
        ))


if __name__ == "__main__":
    ProductApp().run()
