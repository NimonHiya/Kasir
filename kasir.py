import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from PIL import Image, ImageTk
import cv2
from pyzbar.pyzbar import decode
import barcode
from barcode.writer import ImageWriter
import os

class KasirApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kasir SMK 21")
        self.root.geometry("800x600")

        # Item Display
        self.item_label = tk.Label(self.root, text="ITEM", font=("Arial", 16))
        self.item_label.pack(pady=10)

        # Cart Section
        self.cart_tree = ttk.Treeview(self.root, columns=("Item", "Price"), show="headings")
        self.cart_tree.heading("Item", text="Item")
        self.cart_tree.heading("Price", text="Price (Rp)")
        self.cart_tree.pack(pady=20)

        # Total Section
        self.total_label = tk.Label(self.root, text="Total: Rp 0", font=("Arial", 16))
        self.total_label.pack(pady=10)

        # Buttons
        self.add_button = tk.Button(self.root, text="Scan Item", command=self.scan_barcode)
        self.add_button.pack(pady=10)

        self.remove_button = tk.Button(self.root, text="Remove Item", command=self.remove_item)
        self.remove_button.pack(pady=10)

        self.create_item_button = tk.Button(self.root, text="Create Item", command=self.create_item)
        self.create_item_button.pack(pady=10)

        self.total_button = tk.Button(self.root, text="Complete Transaction", command=self.complete_transaction)
        self.total_button.pack(pady=10)

        self.cart_items = []
        self.total_price = 0

        # Dictionary to store item data (barcode as key)
        self.items = {
            "12345": ("Item A", 10000),
            "67890": ("Item B", 20000),
            "11111": ("Item C", 30000)
        }

        self.generate_barcodes(self.items)

    def generate_barcodes(self, items):
        """Generate barcode images for each item."""
        if not os.path.exists("barcodes"):
            os.makedirs("barcodes")

        for barcode_data in items:
            item_name = items[barcode_data][0]
            barcode_image_path = f"barcodes/{item_name}.png"
            # Generate barcode using Code128 (supports variable length)
            code128 = barcode.get('code128', barcode_data, writer=ImageWriter())
            code128.save(barcode_image_path)
            print(f"Barcode for {item_name} saved at {barcode_image_path}")

    def create_item(self):
        """Create a new item and generate its barcode."""
        item_name = simpledialog.askstring("Item Name", "Enter the item name:")
        barcode_data = simpledialog.askstring("Barcode", "Enter the barcode number:")
        item_price = simpledialog.askinteger("Price", "Enter the item price (in Rp):")

        if item_name and barcode_data and item_price is not None:
            # Add new item to the items dictionary
            self.items[barcode_data] = (item_name, item_price)
            self.generate_barcodes({barcode_data: (item_name, item_price)})
            print(f"New item added: {item_name} with barcode {barcode_data} and price Rp {item_price}")
        else:
            print("Item creation canceled or incomplete.")

    def scan_barcode(self):
        """Scan the barcode using the webcam."""
        cap = cv2.VideoCapture(0)

        while True:
            _, frame = cap.read()
            for barcode in decode(frame):
                barcode_data = barcode.data.decode('utf-8')

                if barcode_data in self.items:
                    item_name, item_price = self.items[barcode_data]
                    self.cart_items.append((item_name, item_price))
                    self.cart_tree.insert("", "end", values=(item_name, item_price))
                    self.total_price += item_price
                    self.total_label.config(text=f"Total: Rp {self.total_price}")

                    cap.release()
                    cv2.destroyAllWindows()
                    return

            cv2.imshow('Scan Barcode', frame)
            if cv2.waitKey(1) == 27:  # Press Esc to exit
                break

        cap.release()
        cv2.destroyAllWindows()

    def remove_item(self):
        """Remove selected item from the cart."""
        selected_item = self.cart_tree.selection()
        if selected_item:
            item_values = self.cart_tree.item(selected_item)["values"]
            item_name = item_values[0]
            item_price = item_values[1]

            # Create a tuple to match the format in self.cart_items
            item_tuple = (item_name, item_price)

            # Check if the item_tuple is in the cart_items list
            if item_tuple in self.cart_items:
                self.cart_items.remove(item_tuple)
                self.total_price -= item_price
                self.total_label.config(text=f"Total: Rp {self.total_price}")
                self.cart_tree.delete(selected_item)
            else:
                print("Item not found in cart_items.")

    def complete_transaction(self):
        """Complete the transaction and reset the cart."""
        self.cart_items.clear()
        self.cart_tree.delete(*self.cart_tree.get_children())
        self.total_price = 0
        self.total_label.config(text="Total: Rp 0")
        print("Transaction completed!")

if __name__ == "__main__":
    root = tk.Tk()
    app = KasirApp(root)
    root.mainloop()
