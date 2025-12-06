
<!-- PROJECT LOGO -->
<a href="https://github.com/Matt0550/Rapisardi-Notifications">
  <img src="src/api/static/Banner OG.png">
</a>
<br />
<div align="center">
  <h3 align="center">Rapisardi Notifications</h3>

  <p align="center">
    An unofficial notification system for ITET Rapisardi da Vinci substitutions and timetables
    <br />
    <br />
    <a href="https://matt05.it/rapisardi-notifications">Try It Now</a>
    ·
    <a href="https://github.com/Matt0550/Rapisardi-Notifications/issues">Report Bug</a>
    ·
    <a href="https://github.com/Matt0550/Rapisardi-Notifications/issues">Request Feature</a>
  </p>

  [![Forks][forks-shield]][forks-url]
  [![Stargazers][stars-shield]][stars-url]
  [![Issues][issues-shield]][issues-url]
  [![MIT License][license-shield]][license-url]
  [![Discord][discord-shield]][discord-url]
  [![Docker Pulls][docker-shield]][docker-url]
</div>

# Rapisardi Notifications & API

Unofficial API and Notification System for ITET Rapisardi da Vinci substitutions and timetables.
Get real-time updates about class substitutions, teacher absences, and timetables via API, Email, or Telegram.

> **Disclaimer**: This project is not affiliated, associated, authorized, endorsed by, or in any way officially connected with the Istituto Rapisardi da Vinci, or any of its subsidiaries or its affiliates. It uses web scraping techniques that may not be authorized by the Institute.

## Features

-   **Substitutions API**: Retrieve substitution data for different school locations (Margherita, Turati, Serale).
-   **Timetable API**: Access timetables for classes, teachers, classrooms, and support teachers.
-   **Multi-Channel Notifications**:
    -   **Email**: Receive beautiful, responsive emails (MJML templates) with substitution details.
    -   **Telegram**: Get instant alerts directly on your Telegram chat.
-   **Smart Monitoring**:
    -   **Class Monitoring**: Subscribe to specific classes to get notified about their substitutions.
    -   **Teacher Monitoring**: Subscribe to specific teachers to get notified if they are absent or if they are substituting in *any* class.
-   **Web Dashboard**: A user-friendly interface to manage your subscriptions (classes, teachers, Telegram ID).
-   **Dockerized**: Easy deployment with Docker and Docker Compose, including a native cron job for automatic updates.

## Getting Started

### Prerequisites

-   Docker & Docker Compose (Recommended)
-   Or Python 3.9+ and MongoDB

### Installation (Docker)

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Matt0550/Rapisardi-Notifications.git
    cd Rapisardi-Notifications
    ```

2.  **Configure Environment**:
    Create a `.env` file based on `example.env` and fill in your details (SMTP, MongoDB, Telegram, etc.).

3.  **Build and Run**:
    ```bash
    docker compose up -d --build
    ```

4.  **Access**:
    -   Dashboard: `http://localhost:8000/v1/dashboard`
    -   API Docs: `http://localhost:8000/v1/docs`

### Installation (Manual)

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment**:
    Create a `.env` file with the necessary variables.

3.  **Run the Server**:
    ```bash
    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    ```

## Environment Variables

| Variable | Description | Required |
| :--- | :--- | :---: |
| `SMTP_HOST` | SMTP server host for emails | Yes |
| `SMTP_PORT` | SMTP server port | Yes |
| `SMTP_USERNAME` | SMTP username | Yes |
| `SMTP_PASSWORD` | SMTP password | Yes |
| `SMTP_FROM` | Sender email address | Yes |
| `MONGODB_HOST` | MongoDB host address | Yes |
| `MONGODB_USERNAME` | MongoDB username | Yes |
| `MONGODB_PASSWORD` | MongoDB password | Yes |
| `MONGODB_DATABASE` | MongoDB database name | Yes |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token (from @BotFather) | No |
| `ADMIN_TOKEN` | Token to secure the update endpoint | Yes |
| `HEALTHCHECK_URL` | URL for healthcheck pings | No |

## API Documentation

The API is documented using OpenAPI (Swagger). You can view the interactive documentation at `/v1/docs`.

### Key Endpoints

#### Substitutions
-   `GET /v1/sostituzioni/{sede}/today/{classe}`: Get today's substitutions for a class.
-   `GET /v1/sostituzioni/{sede}/next/{classe}`: Get next day's substitutions for a class.
    -   `sede`: `margherita`, `turati`, `serale`

#### Timetables (Orario)
-   `GET /v1/orario/classi/all`: Get all class timetables.
-   `GET /v1/orario/docenti/all`: Get all teacher timetables.
-   `GET /v1/orario/aule/all`: Get all classroom timetables.
-   `GET /v1/orario/sostegno/all`: Get support teacher timetables.

#### Dashboard
-   `GET /v1/dashboard`: Access the user dashboard.

#### Admin
-   `POST /v1/admin/update_db`: Trigger a manual update check (requires `token` form field matching `ADMIN_TOKEN`).

## Notifications & Automation

The system is designed to check for updates automatically.
-   **Docker**: The container includes a cron job that runs the update script every 45 minutes (Mon-Fri).
-   **Manual**: You can trigger an update via the `/v1/admin/update_db` endpoint.

### Telegram Setup
1.  Create a bot with [@BotFather](https://t.me/BotFather) and get the token.
2.  Set `TELEGRAM_BOT_TOKEN` in your `.env`.
3.  Users can find their Chat ID via [@userinfobot](https://t.me/userinfobot) and save it in the Dashboard.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Support

If you find this project useful, consider supporting it!

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/matt05)

[![buy-me-a-coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/Matt0550)

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://paypal.me/sillittimatteo)

[contributors-shield]: https://img.shields.io/github/contributors/Matt0550/Rapisardi-Notifications.svg
[contributors-url]: https://github.com/Matt0550/Rapisardi-Notifications/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Matt0550/Rapisardi-Notifications.svg
[forks-url]: https://github.com/Matt0550/Rapisardi-Notifications/network/members
[stars-shield]: https://img.shields.io/github/stars/Matt0550/Rapisardi-Notifications.svg?
[stars-url]: https://github.com/Matt0550/Rapisardi-Notifications/stargazers
[issues-shield]: https://img.shields.io/github/issues/Matt0550/Rapisardi-Notifications.svg
[issues-url]: https://github.com/Matt0550/Rapisardi-Notifications/issues
[license-shield]: https://img.shields.io/github/license/Matt0550/Rapisardi-Notifications.svg
[license-url]: https://github.com/Matt0550/Rapisardi-Notifications/blob/master/LICENSE
[discord-shield]: https://img.shields.io/discord/828990499507404820
[discord-url]: https://discord.gg/5WrVyQKWAr
[docker-shield]: https://img.shields.io/docker/pulls/matt0550/rapisardi_notifications
[docker-url]: https://hub.docker.com/r/matt0550/rapisardi_notifications