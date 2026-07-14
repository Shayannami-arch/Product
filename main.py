from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.storage.jsonstore import JsonStore
from kivy.properties import NumericProperty


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


class CardLabel(Card):
    def __init__(self, text, danger=False, **kwargs):
        super().__init__(orientation="vertical", bg=NAVY_800, size_hint_y=None, height=dp(60), **kwargs)
        self.add_widget(Label(
            text=str(text),
            color=DANGER if danger else PAPER,
            font_size=dp(13),
            halign="left",
            valign="middle"
        ))


class StatCard(Card):
    def __init__(self, title, value, subtitle, accent=TEAL, **kwargs):
        super().__init__(orientation="vertical", bg=NAVY_900, size_hint_y=None, height=dp(105), **kwargs)

        self.add_widget(Label(
            text=str(title),
            color=MUTED,
            font_size=dp(12),
            halign="left",
            size_hint_y=None,
            height=dp(24)
        ))

        self.add_widget(Label(
            text=str(value),
            color=accent,
            font_size=dp(26),
            bold=True,
            halign="left",
            size_hint_y=None,
            height=dp(36)
        ))

        self.add_widget(Label(
            text=str(subtitle),
            color=MUTED,
            font_size=dp(11),
            halign="left",
            size_hint_y=None,
            height=dp(24)
        ))


class ProductCard(Card):
    product_id = NumericProperty(0)

    def __init__(self, product, edit_callback, delete_callback, **kwargs):
        super().__init__(orientation="vertical", bg=NAVY_800, size_hint_y=None, height=dp(195), **kwargs)
        self.product = product
        self.product_id = product.get("id", 0)
        self.edit_callback = edit_callback
        self.delete_callback = delete_callback

        top = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(28), spacing=dp(8))

        category = Label(
            text=str(product.get("category", "General")),
            color=MUSTARD,
            font_size=dp(11),
            size_hint_x=0.60,
            halign="left"
        )

        warning = ""
        try:
            if int(product.get("qty", 0)) <= int(product.get("min_qty", 0)):
                warning = "LOW STOCK"
        except Exception:
            warning = ""

        low = Label(
            text=warning,
            color=DANGER,
            font_size=dp(11),
            size_hint_x=0.40,
            halign="right"
        )

        top.add_widget(category)
        top.add_widget(low)
        self.add_widget(top)

        self.add_widget(Label(
            text=str(product.get("name", "Untitled Product")),
            color=PAPER,
            font_size=dp(16),
            bold=True,
            halign="left",
            size_hint_y=None,
            height=dp(34)
        ))

        self.add_widget(Label(
            text="Product ID: " + str(product.get("sku", "-")),
            color=MUTED,
            font_size=dp(12),
            halign="left",
            size_hint_y=None,
            height=dp(24)
        ))

        self.add_widget(Label(
            text="Brand: " + str(product.get("brand", "-")),
            color=MUTED,
            font_size=dp(12),
            halign="left",
            size_hint_y=None,
            height=dp(24)
        ))

        self.add_widget(Label(
            text="Expire Date: " + str(product.get("expire", "-")),
            color=MUTED,
            font_size=dp(12),
            halign="left",
            size_hint_y=None,
            height=dp(24)
        ))

        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(32))

        price = Label(
            text=f"{int(product.get('buy_price', 0)):,} Toman",
            color=TEAL,
            bold=True,
            font_size=dp(13),
            halign="left"
        )

        qty = Label(
            text=f"Stock: {product.get('qty', 0)}",
            color=PAPER,
            font_size=dp(13),
            halign="right"
        )

        row.add_widget(price)
        row.add_widget(qty)
        self.add_widget(row)

        actions = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(38), spacing=dp(8))

        btn_edit = Button(
            text="Edit",
            background_normal="",
            background_color=NAVY_700,
            color=PAPER,
            font_size=dp(12)
        )
        btn_edit.bind(on_press=lambda x: self.edit_callback(self.product_id))

        btn_delete = Button(
            text="Delete",
            background_normal="",
            background_color=(0.55, 0.18, 0.16, 1),
            color=PAPER,
            font_size=dp(12)
        )
        btn_delete.bind(on_press=lambda x: self.delete_callback(self.product_id))

        actions.add_widget(btn_edit)
        actions.add_widget(btn_delete)
        self.add_widget(actions)


class ProductApp(App):
    def build(self):
        self.title = "ProductApp"

        self.store = JsonStore("products_data.json")
        self.products = []
        self.next_id = 1

        self.load_data()

        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        with root.canvas.before:
            Color(*NAVY_950)
            self.bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self.update_bg, size=self.update_bg)

        root.add_widget(self.make_header())
        root.add_widget(self.make_navbar())

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
            return

        self.products = [
            {
                "id": 1,
                "sku": "PRD-1001",
                "name": "Wireless Headphone X1",
                "brand": "Sony",
                "category": "Electronics",
                "expire": "No Expiry",
                "buy_price": 1250000,
                "qty": 14,
                "min_qty": 5
            },
            {
                "id": 2,
                "sku": "PRD-2001",
                "name": "Turkish Coffee 250g",
                "brand": "Mehmet",
                "category": "Food",
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

    # ---------- UI ----------
    def make_header(self):
        box = Card(orientation="horizontal", bg=NAVY_900, size_hint_y=None, height=dp(78), radius=16)

        title_box = BoxLayout(orientation="vertical")

        title_box.add_widget(Label(
            text="ANBARAK",
            color=PAPER,
            bold=True,
            font_size=dp(24),
            halign="left",
            size_hint_y=0.6
        ))

        title_box.add_widget(Label(
            text="Product Management System",
            color=MUTED,
            font_size=dp(12),
            halign="left",
            size_hint_y=0.4
        ))

        mark = Label(
            text="AK",
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

        box.add_widget(mark)
        box.add_widget(title_box)
        return box

    def make_navbar(self):
        bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(8))

        nav_items = [
            ("Dashboard", self.render_dashboard, NAVY_800, PAPER),
            ("Products", self.render_products, NAVY_800, PAPER),
            ("Add Product", self.open_product_form, TEAL, NAVY_950),
        ]

        for text, action, bg, fg in nav_items:
            btn = Button(
                text=text,
                background_normal="",
                background_color=bg,
                color=fg,
                bold=True,
                font_size=dp(13)
            )
            btn.bind(on_press=lambda instance, callback=action: callback())
            bar.add_widget(btn)

        return bar

    def clear_content(self):
        self.content.clear_widgets()

    # ---------- Dashboard ----------
    def render_dashboard(self, *args):
        self.clear_content()

        total = len(self.products)
        total_value = sum(int(p.get("buy_price", 0)) * int(p.get("qty", 0)) for p in self.products)
        low_count = sum(1 for p in self.products if int(p.get("qty", 0)) <= int(p.get("min_qty", 0)))
        categories = len(set(p.get("category", "General") for p in self.products))

        scroll = ScrollView()
        body = GridLayout(cols=1, spacing=dp(12), size_hint_y=None)
        body.bind(minimum_height=body.setter("height"))

        body.add_widget(StatCard("Total Products", str(total), "Registered items", TEAL))
        body.add_widget(StatCard("Inventory Value", f"{total_value:,}", "Toman", MUSTARD))
        body.add_widget(StatCard("Low Stock Alerts", str(low_count), "Items below minimum", DANGER))
        body.add_widget(StatCard("Categories", str(categories), "Active categories", TEAL))

        body.add_widget(Label(
            text="Low Stock Products",
            color=PAPER,
            bold=True,
            font_size=dp(16),
            halign="left",
            size_hint_y=None,
            height=dp(40)
        ))

        low_items = [p for p in self.products if int(p.get("qty", 0)) <= int(p.get("min_qty", 0))]
        if not low_items:
            body.add_widget(CardLabel("No products are below the minimum stock level."))
        else:
            for p in low_items:
                body.add_widget(CardLabel(
                    f"{p.get('name')} | Stock: {p.get('qty')} | Min: {p.get('min_qty')}",
                    danger=True
                ))

        scroll.add_widget(body)
        self.content.add_widget(scroll)

    # ---------- Products ----------
    def render_products(self, *args):
        self.clear_content()

        search = TextInput(
            hint_text="Search by name, product ID, brand, or category...",
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

            filtered = []
            for p in self.products:
                searchable = f"{p.get('name')} {p.get('sku')} {p.get('brand')} {p.get('category')}".lower()
                if not q or q in searchable:
                    filtered.append(p)

            if not filtered:
                grid.add_widget(CardLabel("No products found."))
            else:
                for p in filtered:
                    grid.add_widget(ProductCard(p, self.open_product_form, self.delete_product))

        search.bind(text=lambda instance, value: draw_products(value))
        draw_products()

        scroll.add_widget(grid)
        self.content.add_widget(scroll)

    # ---------- Product form ----------
    def open_product_form(self, product_id=None, *args):
        product = None
        if isinstance(product_id, int):
            product = next((p for p in self.products if p.get("id") == product_id), None)

        layout = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(12))
        fields = {}

        def input_field(key, hint, value=""):
            ti = TextInput(
                hint_text=hint,
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

        input_field("sku", "Product ID", product.get("sku", "") if product else "")
        input_field("name", "Product Name", product.get("name", "") if product else "")
        input_field("brand", "Brand", product.get("brand", "") if product else "")
        input_field("category", "Category", product.get("category", "") if product else "General")
        input_field("expire", "Expire Date", product.get("expire", "") if product else "")
        input_field("buy_price", "Buy Price", product.get("buy_price", "") if product else "")
        input_field("qty", "Current Stock", product.get("qty", "") if product else "")
        input_field("min_qty", "Minimum Stock", product.get("min_qty", "5") if product else "5")

        buttons = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(8))

        cancel = Button(
            text="Cancel",
            background_normal="",
            background_color=NAVY_700,
            color=PAPER
        )

        save = Button(
            text="Save Product",
            background_normal="",
            background_color=TEAL,
            color=NAVY_950,
            bold=True
        )

        buttons.add_widget(cancel)
        buttons.add_widget(save)
        layout.add_widget(buttons)

        popup = Popup(
            title="Edit Product" if product else "Add New Product",
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
                self.show_message("Product ID and Product Name are required.")
                return

            try:
                buy_price = int(fields["buy_price"].text.strip() or 0)
                qty = int(fields["qty"].text.strip() or 0)
                min_qty = int(fields["min_qty"].text.strip() or 0)
            except Exception:
                self.show_message("Buy Price, Current Stock, and Minimum Stock must be numbers.")
                return

            data = {
                "sku": sku,
                "name": name,
                "brand": fields["brand"].text.strip(),
                "category": fields["category"].text.strip() or "General",
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
            self.show_message("Product saved successfully.")

        save.bind(on_press=save_item)
        popup.open()

    def delete_product(self, product_id):
        self.products = [p for p in self.products if p.get("id") != product_id]
        self.save_data()
        self.render_products()
        self.show_message("Product deleted.")

    def show_message(self, message):
        popup = Popup(
            title="Message",
            content=Label(text=message, color=PAPER, font_size=dp(15)),
            size_hint=(0.82, 0.28),
            background_color=NAVY_900,
            title_color=PAPER,
            separator_color=TEAL
        )
        popup.open()


if __name__ == "__main__":
    ProductApp().run()
