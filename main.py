import logging
import requests
import json
import time
import sys
import websocket
import threading
import asyncio
import random

# Set up logging to remove timestamps and info level
logger = logging.getLogger()
logger.setLevel(logging.INFO)
log_formatter = logging.Formatter(
    '%(message)s')  # Only log messages without timestamp or level
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)


# Load configuration from config.json
def load_config():
    with open("config.json", "r",
              encoding="utf-8") as f:  # Ensure UTF-8 encoding
        return json.load(f)


# Load predefined static content (e.g., steps, promises, etc.) from static.json
def load_static_content():
    with open("static.json", "r",
              encoding="utf-8") as f:  # Ensure UTF-8 encoding
        return json.load(f)


# Load sponsor data from sponsors.json
def load_sponsors():
    try:
        with open("sponsors.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# Save sponsor data to sponsors.json
def save_sponsors(sponsors):
    with open("sponsors.json", "w", encoding="utf-8") as f:
        json.dump(sponsors, f, indent=4)


# Meditation command
async def meditation_command(channel_id):
    static_content = load_static_content(
    )  # Load the static content (including meditation quotes)
    meditation_quotes = static_content.get("meditation_quotes", [])

    if meditation_quotes:
        random_quote = random.choice(meditation_quotes)
        await send_message(channel_id, f"_**{random_quote}**_")
    else:
        await send_message(channel_id, "No meditation quotes found.")


# Async function to send a message to a specific channel
async def send_message(channel_id, message):
    message_with_blockquote = f">>> {message}"  # Wrap the message in block quotes
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    data = {"content": message_with_blockquote}
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        logger.info(f"Message successfully sent!")
    else:
        logger.error(
            f"Error sending message: {response.status_code} - {response.text}")


def split_message(message, max_length=2000):
    """Split message into chunks that are within the Discord limit."""
    chunks = [
        message[i:i + max_length] for i in range(0, len(message), max_length)
    ]
    logger.info(f"Message split into {len(chunks)} chunks.")
    return chunks


# Async function to process incoming messages and respond to commands
async def process_message(channel_id, message):
    content = message["content"].strip()
    static_content = load_static_content()

    if content.startswith("?"):  # Commands start with '?'
        command = content[1:].lower()
        logger.info(f"Received Command: {command}")

        # Meditation Command
        if command == "meditation":
            await meditation_command(channel_id)

        # Display help with all available commands
        if command == "help":
            help_message = (
                "# Available Commands:\n"
                "_**?help**_ - `Shows this message`\n"
                "_**?preamble**_ - `Displays the Preamble`\n"
                "_**?howitworks**_ - `Explains How it Works`\n"
                "_**?steps**_ - `Lists the 12 Steps`\n"
                "_**?promises**_ - `Lists the Promises`\n"
                "_**?prayers**_ - `Lists Available Prayers`\n"
                "_**?prayer <name>**_ - `Displays a Specific Prayer`\n"
                "_**?sponsors**_ - `Lists Available Sponsors`\n"
                "_**?add_sponsor <username> <role>**_ - `Adds a New Sponsor`\n"
                "_**?remove_sponsor <username>**_ - `Removes a Sponsor`\n"
                "_**?meditation**_ - `Random Meditation Quote!`")
            await send_message(channel_id, help_message)

        # Sponsor Section
        if command == "sponsors":  # List all sponsors
            sponsors = load_sponsors()
            if sponsors:
                sponsor_list = "\n".join([
                    f"{username}: {data['role']}"
                    for username, data in sponsors.items()
                ])
                await send_message(channel_id,
                                   f"List of Sponsors:\n>>> {sponsor_list}")
            else:
                await send_message(channel_id, "No Sponsors available.")

        elif command.startswith("add_sponsor "):  # Add a new sponsor
            try:
                _, username, role = command.split(" ", 2)
                sponsors = load_sponsors()
                sponsors[username] = {"role": role}
                save_sponsors(sponsors)
                await send_message(
                    channel_id, f"Added Sponsor: {username} with role: {role}")
            except ValueError:
                await send_message(
                    channel_id,
                    "Invalid format! Use: ?add_sponsor <username> <role>")

        elif command.startswith("remove_sponsor "):  # Remove a sponsor
            try:
                _, username = command.split(" ", 1)
                sponsors = load_sponsors()
                if username in sponsors:
                    del sponsors[username]
                    save_sponsors(sponsors)
                    await send_message(channel_id,
                                       f"Removed sponsor: {username}")
                else:
                    await send_message(
                        channel_id,
                        f"No sponsor found with username: {username}")
            except ValueError:
                await send_message(
                    channel_id,
                    "Invalid format! Use: ?remove_sponsor <username>")

        # End Sponsor Section

        # Static Commands like ?steps, ?promises, ?prayers, etc.
        elif command in static_content:
            response = static_content[command]

            # If response is a list, join it into a string
            if isinstance(response, list):
                response = "\n".join(response)

            await send_message(channel_id, response)

            # Log success message for each content type
            if command == "steps":
                logger.info("Steps Successfully Sent!")
            elif command == "promises":
                logger.info("Promises Successfully Sent!")
            elif command == "prayers":
                logger.info("Prayers Successfully Sent!")
            elif command == "traditions":
                logger.info("Traditions Successfully Sent!")

        # How it works command
        if command == "howitworks":
            part1 = static_content.get("howitworks_part1", [])
            part2 = static_content.get("howitworks_part2", [])
            part3 = static_content.get("howitworks_part3", [])

            # Send each part in order
            for part in [part1, part2, part3]:
                if part:
                    for chunk in part:
                        logger.info(
                            f"Sending chunk: {chunk[:50]}..."
                        )  # Log first 50 chars of chunk for debugging
                        await send_message(channel_id,
                                           chunk)  # Send each chunk
                await asyncio.sleep(
                    1
                )  # Optional: Add a short delay between parts to avoid rate limiting
            logger.info("How It Works content successfully sent!")

        elif command == "prayers":  # List all available prayers from the static content
            prayers_data = static_content.get("prayers", {})
            available_prayers = list(prayers_data.keys(
            ))  # Get all the keys (prayer names) from the "prayers" section

            prayers_list = "\n".join(
                available_prayers)  # Create a list of prayer names
            chunks = split_message(
                prayers_list)  # Split into chunks if the list is too long

            # Send each chunk as a separate message
            for chunk in chunks:
                await send_message(channel_id, chunk)

        elif command.startswith(
                "prayer "
        ):  # Handle specific prayer requests (e.g., ?prayer 3rd)
            prayer_name = content.split(" ", 1)[1].strip().lower() if len(
                content.split(" ", 1)) > 1 else ""

            # Look up the prayer in the static content
            prayer = static_content.get("prayers", {}).get(prayer_name)

            if prayer:
                await send_message(channel_id, prayer)
            else:
                await send_message(
                    channel_id,
                    f"Prayer '{prayer_name}' not found. Available prayers are: serenity, 3rd, 3alt, 7th, 7alt, 11th, lords."
                )
        elif content == "":
            logger.info("Received an empty message.")


# WebSocket to handle bot presence updates
def on_message(ws, message):
    data = json.loads(message)
    if data["op"] == 10:  # Hello packet from Discord
        heartbeat_interval = data["d"]["heartbeat_interval"]
        # Send IDENTIFY to start the connection
        identify_payload = {
            "op": 2,
            "d": {
                "token": bot_token,
                "intents": 513,  # Required for receiving messages
                "properties": {
                    "$os": "linux",
                    "$browser": "my_library",
                    "$device": "my_device"
                }
            }
        }
        ws.send(json.dumps(identify_payload))
        # Set the bot's presence
        presence_payload = {
            "op": 3,
            "d": {
                "since": None,
                "status": "online",
                "afk": False,
                "game": {
                    "name": "?help",
                    "type": 0  # Playing a game
                }
            }
        }
        ws.send(json.dumps(presence_payload))

    elif data["op"] == 11:  # Heartbeat acknowledgment
        logger.info("Heartbeat received, sending pong.")
        ws.send(json.dumps({"op": 1, "d": None}))  # Send heartbeat response


def on_error(ws, error):
    logger.error(f"Error: {error}")


def on_close(ws, close_status_code, close_msg):
    logger.error(f"Closed WebSocket connection.")
    if close_status_code != 1000:
        logger.error(
            f"WebSocket closed with status code {close_status_code}. Attempting to reconnect..."
        )


# Start WebSocket connection for presence updates
def start_websocket(bot_token, stop_event):
    global ws  # Declare ws as a global variable to access it elsewhere
    url = "wss://gateway.discord.gg/?v=10&encoding=json"
    websocket.enableTrace(False)  # Disable raw trace logs

    ws = websocket.WebSocketApp(url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    while not stop_event.is_set():
        try:
            ws.run_forever()
        except Exception as e:
            logger.error(f"WebSocket error: {e}. Attempting to reconnect...")
            time.sleep(5)  # Wait before attempting to reconnect


# Main function
def main():
    config = load_config()
    global bot_token
    bot_token = config["bot_token"]
    channels = config["channels"]

    global headers
    headers = {
        "Authorization": f"Bot {bot_token}",
        "Content-Type": "application/json"
    }

    stop_event = threading.Event()
    websocket_thread = threading.Thread(target=start_websocket,
                                        args=(bot_token, stop_event),
                                        daemon=True)
    websocket_thread.start()

    processed_message_ids = set()  # Track processed message IDs

    try:
        while True:
            for channel_id in channels:
                url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
                response = requests.get(url,
                                        headers=headers,
                                        params={"limit": 5})

                if response.status_code == 200:
                    for message in response.json():
                        message_id = message["id"]
                        if message_id not in processed_message_ids:
                            asyncio.run(process_message(channel_id, message))
                            processed_message_ids.add(message_id)

                            # To avoid memory overflow, limit the size of the processed_message_ids set
                            if len(processed_message_ids
                                   ) > 1000:  # Adjust as needed
                                processed_message_ids.pop()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Bot stopped.")
        stop_event.set()
        sys.exit(0)


if __name__ == "__main__":
    main()
