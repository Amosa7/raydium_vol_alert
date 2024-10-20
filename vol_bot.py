from typing import Final
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, JobQueue

# Telegram bot credentials
TOKEN: Final = '7595781510:AAGbJB9IGOXS1OK6t5043SHvv2W3G5kc-Hc'
BOT_USERNAME: Final = '@G_don_raydiumvol_bot'

# Raydium API for token pairs
RAYDIUM_API_URL = "https://api-v3.raydium.io/pairs"
ALERT_THRESHOLD = 1000  # Volume threshold for recent activity in a 3-minute window

# Dictionary to store previous volumes for each token
previous_volumes = {}

# Function to fetch token data from Raydium
def fetch_ray_volume():
    try:
        response = requests.get(RAYDIUM_API_URL)
        response.raise_for_status()  # Raise an error for any bad responses
        return response.json()['data']  # Return list of token pairs with data
    except requests.RequestException as e:
        print(f"Error fetching Raydium data: {e}")
        return None

# Function to check token volumes and send Telegram notifications if conditions are met
async def monitor_raydium_tokens(context: ContextTypes.DEFAULT_TYPE):
    global previous_volumes
    tokens = fetch_ray_volume()
    if tokens:
        for token in tokens:
            name = token.get('name', 'Unknown')
            pair_address = token.get('pairAddress', 'Unknown')
            current_volume = token.get('volume24', 0)  # Get 24-hour volume
            
            # Check the previous volume of the token
            previous_volume = previous_volumes.get(pair_address, 0)
            
            # Calculate the difference in volume since the last check (assumed 3 minutes ago)
            volume_difference = current_volume - previous_volume
            
            # Update the stored volume for the token
            previous_volumes[pair_address] = current_volume
            
            # Simulating the number of buys (for demo purposes, you can adjust this logic)
            buys_count = int(volume_difference / 1.5)  # Assuming each buy averages 1.5 SOL, you can modify this

            # Check if the volume difference exceeds the threshold
            if volume_difference > ALERT_THRESHOLD:
                message = (
                    f"🚨 New {name} Volume Alert! 🚨\n\n"
                    f"Token: {name}\n"
                    f"Last 3 mins buy: {volume_difference:.2f} SOL in {buys_count} buys\n"
                    f"Current 24h Volume: {current_volume}\n"
                    f"Pair Address: {pair_address}\n"
                    f"Potential trading opportunity!"
                )
                await context.bot.send_message(chat_id=context.job.chat_id, text=message)

# Function to start automatic monitoring of Raydium tokens
async def start_auto_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    job_queue: JobQueue = context.job_queue
    job_queue.run_repeating(monitor_raydium_tokens, interval=180, first=10, chat_id=chat_id)  # Run every 3 minutes
    await update.message.reply_text("Monitoring Raydium token volumes. Alerts will be sent for significant spikes in recent activity.")

# Command to start the bot and display a welcome message
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use /auto to start receiving Raydium volume alerts.")

# Main function to run the bot
def main():
    application = Application.builder().token(TOKEN).build()
    
    # Register the command handlers
    application.add_handler(CommandHandler("start", start_command))  # Handles /start command
    application.add_handler(CommandHandler("auto", start_auto_notifications))  # Handles /auto command
    
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
