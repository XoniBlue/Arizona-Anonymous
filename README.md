# Arizona Anonymous Discord Bot

Welcome to the **Arizona Anonymous Discord Bot**! This bot is designed to assist members of the Arizona Anonymous Discord server with tools to support their recovery journey, featuring daily reflections, prayer, meeting schedules, and more.

## Features

- **Daily Reflections**: The bot posts daily thoughts, prayers, and reflections to help members stay grounded.
- **Meeting Schedules**: Easily access a list of upcoming meetings and their details.
- **12 Steps & Traditions**: Access the 12 Steps and Traditions of AA directly in your Discord server.
- **Role Management**: Automatically assigns recovery-related roles (e.g., 1 month, 2 months) to members.
- **Sponsor/Sponsee Lists**: Get a list of sponsors and sponsees for members.
- **Preamble, Promises, & More**: Displays relevant information like the preamble, promises, and other important texts.

## Requirements

- Python 3.x
- pip (Python package installer)
- Discord API token (stored as an environment variable)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Arizona-Anonymous.git
   cd Arizona-Anonymous
   ```

2. Set up your environment (virtual environment recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your **Discord Bot Token**:
   - Create a `.env` file in the root directory of the project and add your bot token:
     ```
     DISCORD_TOKEN=your-bot-token
     ```

5. Run the bot:
   ```bash
   python main.py
   ```

## Usage

Once the bot is running, you can interact with it through Discord by using specific commands:

- `!dailies`: Get daily reflections, prayers, and thoughts.
- `!meetings`: View upcoming meetings and their details.
- `!steps`: Displays the 12 Steps of AA.
- `!traditions`: Displays the 12 Traditions of AA.
- `!sponsor`: List sponsors in the server.
- `!sponsee`: List sponsees in the server.
- `!preamble`, `!promise`: Access recovery-related texts.

## Docker Deployment

You can also deploy the bot using Docker:

1. Build the Docker image:
   ```bash
   docker build -t aabot .
   ```

2. Run the container:
   ```bash
   docker run -d --name aabot-container -p 8080:8080 aabot
   ```

## Contributing

If you'd like to contribute to the development of this bot, feel free to fork the repository and submit pull requests. We'd love to have your help!

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
