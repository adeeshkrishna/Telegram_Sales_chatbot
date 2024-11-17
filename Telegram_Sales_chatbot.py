from typing import List, Dict
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import logging

# Define Product and ShoppingCart classes
class Product:
    def __init__(self, name: str, description: str, price: float, available: bool = True):
        self.name = name
        self.description = description
        self.price = price
        self.available = available

class ShoppingCart:
    def __init__(self):
        self.items: Dict[Product, int] = {}
        
    def add_item(self, product: Product, quantity: int = 1):
        if product in self.items:
            self.items[product] += quantity
        else:
            self.items[product] = quantity
            
    def get_total(self) -> float:
        return sum(product.price * quantity for product, quantity in self.items.items())
    
    def display(self) -> str:
        if not self.items:
            return "Your cart is empty."
        
        cart_display = "Your cart:\n"
        for product, quantity in self.items.items():
            cart_display += f"- {product.name} (x{quantity}): Rs {product.price * quantity:.2f}\n"
        cart_display += f"\nTotal: Rs {self.get_total():.2f}"
        return cart_display

# Define SalesChatbot class
class SalesChatbot:
    def __init__(self):
        self.products = [
            Product("Laptop", "Ryzen 5000 (16GB RAM/512GB SSD/FHD/Windows 11/MS Office 21/Backlit Keyboard/ 15.6” (39.6 cm)/Silver/2.21 KG)", 59999),
            Product("Smartphone", "5G (Onyx Green, 12GB RAM, 256GB Storage) | 120 Hz 3D Curved AMOLED Display | 5500 mAh Ultra-Thin Battery | Dimesity 7300 5G Processor | Sony IMX882 OIS Camera with Aura Light", 29999),
            Product("Headphones", "Bluetooth Wireless in Ear Earphones with Mic, Bombastic Bass - 12.4 mm Drivers, 10 Mins Charge - 20 Hrs Music, 30 Hrs Battery Life, IP55 Dust and Water Resistant (Magico Black)", 3000),
            Product("Smartwatch", "1.85 Display, Bluetooth Calling Smart Watch, 10 Days Battery, 550 NITS Brightness, Smart DND, 100 Sports Modes, Smartwatch for Men and Women (Rose Pink)", 2500),
            Product("Tablet", "All Day Battery | Qualcomm Snapdragon 680| 90Hz Refresh Rate| 8GB, 128GB Tablet| FHD+ Display (11-inch/27.81cm)| Dolby Atmos| Quad Speakers| Wi-Fi| Gray", 19999),
        ]
        self.cart = ShoppingCart()
        
    def process_input(self, user_input: str) -> str:
        user_input = user_input.lower()
        
        if any(greeting in user_input for greeting in ["hello", "hi", "hey"]):
            return "Hello! Welcome to our virtual store. How can I help you today?"
        
        if any(phrase in user_input for phrase in ["what products", "show products", "list products"]):
            return self.list_products()
        
        if "tell me about" in user_input or "information about" in user_input:
            return self.get_product_info(user_input)
        
        if "recommend" in user_input:
            return self.recommend_product()
        
        if any(cart_phrase in user_input for cart_phrase in ["show cart", "view cart", "my cart"]):
            return self.cart.display()
        
        if "add" in user_input and any(product.name.lower() in user_input for product in self.products):
            return self.add_to_cart(user_input)
        
        if any(purchase_phrase in user_input for purchase_phrase in ["checkout", "complete purchase", "buy"]):
            return self.complete_purchase()
        
        return "I'm not sure what you mean. You can ask about our products, request recommendations, or manage your cart."

    def list_products(self) -> str:
        products_list = "Here are our available products:\n"
        for product in self.products:
            status = "Available" if product.available else "Out of stock"
            products_list += f"- {product.name}: Rs {product.price:.2f} ({status})\n"
        return products_list

    def get_product_info(self, query: str) -> str:
        for product in self.products:
            if product.name.lower() in query:
                return f"{product.name}: {product.description}\nPrice: Rs {product.price:.2f}"
        return "I couldn't find information about that product."

    def recommend_product(self) -> str:
        recommended = max(self.products, key=lambda p: p.price)
        return f"I recommend our {recommended.name}! {recommended.description}\nPrice: Rs {recommended.price:.2f}"

    def add_to_cart(self, query: str) -> str:
        for product in self.products:
            if product.name.lower() in query:
                if not product.available:
                    return f"Sorry, {product.name} is currently out of stock."
                
                quantity = 1
                quantity_match = re.search(r'(\d+)', query)
                if quantity_match:
                    quantity = int(quantity_match.group(1))
                
                self.cart.add_item(product, quantity)
                return f"Added {quantity} {product.name}(s) to your cart.\n" + self.cart.display()
        return "I couldn't find that product."

    def complete_purchase(self) -> str:
        if not self.cart.items:
            return "Your cart is empty. Add some products before checking out!"
        
        total = self.cart.get_total()
        self.cart = ShoppingCart()  # Reset cart after purchase
        return f"Thank you for your purchase! Your total was Rs {total:.2f}. Your order will be processed shortly."

# Initialize the SalesChatbot
chatbot = SalesChatbot()

# Telegram bot token
bot_token = "bot_token"

# Configure logging for debugging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# Define the start function for the /start command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! Welcome to our virtual store. How can I help you today?")

# Define the handle_message function to process user messages
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text
    response = chatbot.process_input(user_input)
    await update.message.reply_text(response)

# Main function to start the bot
def main():
    # Create the Application and set up the bot token
    application = Application.builder().token(bot_token).build()
    
    # Add handlers for start and general messages
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot with polling
    application.run_polling()

if __name__ == "__main__":
    main()
