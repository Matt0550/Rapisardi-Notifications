# Rapisardi Sostituzioni API & Notifications

API per ricevere le sostituzioni dell'Istituto Rapisardi da Vinci. Le sostituzioni vengono anche inviate tramite email ad ogni nuovo aggiornamento.

API to receive the substitutions of the Rapisardi da Vinci Institute. The substitutions are also sent via email with each new update.

_This project is not affiliated, associated, authorized, endorsed by, or in any way officially connected with the Istituto Rapisardi da Vinci, or any of its subsidiaries or its affiliates. In addition, it uses web scraping techniques that may not be authorized by the Institute._

_Questo progetto non è affiliato, associato, autorizzato, approvato o in alcun modo connesso ufficialmente con l'Istituto Rapisardi da Vinci o con una delle sue sussidiarie o affiliate. Inoltre utilizza delle tecniche di web scraping che potrebbero non essere autorizzate dall'Istituto._

# Ricevere le notifiche - Receive notifications
Per ricevere le notifiche, puoi scegliere tra due metodi:
1. Utilizzare il servizio hostato da me - Use the service hosted by me
2. Hostare il servizio da te - Host the service yourself

Nel primo caso, inviami un'email all'indirizzo [me@matteosillitti.it](mailto:me@matteosillitti.it) con l'indirizzo email a cui vuoi ricevere le notifiche e le classi per le quali vuoi ricevere le notifiche.

In the first case, send me an email at [me@matteosillitti.it](mailto:me@matteosillitti.it) with the email address you want to receive notifications and the classes for which you want to receive notifications.

# Docker compose

```yaml
version: '3'

services:
  rapisardi-notifications:
    image: matt0550/rapisardi_notifications
    ports:
      - "8000:8000"
    environment:
      - SMTP_HOST=
      - SMTP_PORT=587
      - SMTP_USERNAME=
      - SMTP_PASSWORD=
      - SMTP_SSL=False
      - SMTP_FROM=
      - MONGODB_HOST=
      - MONGODB_USERNAME=
      - MONGODB_PASSWORD=
      - MONGODB_DATABASE=
      - MONGODB_PORT=27017
      - ADMIN_TOKEN=
    restart: unless-stopped
```

## Installazione - Install (Docker)

1. Installare Docker e Docker Compose - Install Docker and Docker Compose
2. Clonare il repository - Clone the repository
3. Creare il file .env con le variabili d'ambiente (vedi sotto) - Create the .env file with the environment variables (see below)
4. Buildare il container con `docker compose build` - Build the container with `docker compose build`
5. Avviare il container con `docker compose up -d` - Start the container with `docker compose up -d` 
6. Aprire il browser all'indirizzo `http://<ip>:8080` - Open the browser at `http://<ip>:8080`

## Installazione - Install (Manuale)

1. Installare Python 3.9 - Install Python 3.9
2. Clonare il repository - Clone the repository
3. Creare il file .env con le variabili d'ambiente (vedi sotto) - Create the .env file with the environment variables (see below)
4. Installare le dipendenze con `pip install -r requirements.txt` - Install the dependencies with `pip install -r requirements.txt`
5. Avviare il server con `uvicorn api:app --reload` - Start the server with `uvicorn api:app --reload`

## Variabili d'ambiente - Environment variables

| Nome - Name | Descrizione - Description | Default | Obbligatorio - Mandatory |
| ----------- | ------------------------ | ------- | ----------------------- |
| `SMTP_HOST` | Host SMTP per l'invio delle email - SMTP host for email sending | `None` | :heavy_check_mark: |
| `SMTP_PORT` | Porta SMTP per l'invio delle email - SMTP port for email sending | `587` | :heavy_check_mark: |
| `SMTP_USERNAME` | Username SMTP per l'invio delle email - SMTP username for email sending | `None` | :heavy_check_mark: |
| `SMTP_PASSWORD` | Password SMTP per l'invio delle email - SMTP password for email sending | `None` | :heavy_check_mark: |
| `SMTP_SSL` | Abilita SSL per l'invio delle email - Enable SSL for email sending | `True` | :heavy_check_mark: |
| `SMTP_FROM` | Indirizzo email mittente - Sender email address | `None` | :heavy_check_mark: |
| `MONGODB_HOST` | Host MongoDB - MongoDB host | `None` | :heavy_check_mark: |
| `MONGODB_USERNAME` | Username MongoDB - MongoDB username | `None` | :heavy_check_mark: |
| `MONGODB_PASSWORD` | Password MongoDB - MongoDB password | `None` | :heavy_check_mark: |
| `MONGODB_DATABASE` | Database MongoDB - MongoDB database | `None` | :heavy_check_mark: |
| `ADMIN_TOKEN` | Token per l'aggiornamento del database - Token for database update | `None` | :heavy_check_mark: |

## Admin token

Il token per l'aggiornamento del database può essere generato con il comando `python -c "import secrets; print(secrets.token_urlsafe())"`.

The token for database update can be generated with the command `python -c "import secrets; print(secrets.token_urlsafe())"`.
> [!IMPORTANT]
> Il token generato non deve contenere caratteri non supportati da JSON.
> 
> The generated token must not contain characters not supported by JSON.

## API

Le API Docs sono disponibili all'indirizzo `http://<ip>:8080/docs`.

The API Docs are available at `http://<ip>:8080/docs`.

## Database

Esempio di database - Example of database:

Users collection:
```json
{
  "_id": {
    "$oid": ""
  },
  "email": "@gmail.com",
  "classi": [
    "5C inf"
  ],
  "endpoint": "margherita",
  "last_sostituzioni": {
    "5C inf": [
      "",
      "",
      "",
      "",
      "",
      "",
      ""
    ]
  },
  "last_notification": {
    "5C inf": {
      "$date": "2023-12-18T00:00:23.630Z"
    }
  }
}
```

Per attivare le notifiche per un singolo utente, aggiungere alla collection `users` un documento con tutti i campi sopra elencati.

To activate notifications for a single user, add to the `users` collection a document with all the fields listed above.

## Notifiche - Notifications

Le notifiche vengono inviate tramite email all'indirizzo specificato nel campo `email` del documento nella collection `users`.

Tramite un cronjob bisogna inviare una richiesta POST all'endpoint `/admin/update_db` passandogli il token specificato nel campo `ADMIN_TOKEN` delle variabili d'ambiente come parametro `token` (Form). Nella mia configurazione, il cronjob viene eseguito ogni ora.

Notifications are sent via email to the address specified in the `email` field of the document in the `users` collection.

Through a cronjob you have to send a POST request to the `/admin/update_db` endpoint passing the token specified in the `ADMIN_TOKEN` field of the environment variables as the `token` parameter (Form). In my configuration, the cronjob is executed every hour.

## Dashboard - Alpha (WIP)

La dashboard è disponibile all'indirizzo `http://<ip>:8080/dashboard`.

Tramite la dashboard è possibile da parte dell'utente aggiungere o rimuovere le classi per le quali ricevere le notifiche.

The dashboard is available at `http://<ip>:8080/dashboard`.

Through the dashboard the user can add or remove the classes for which to receive notifications.

## Licenza - License

[MIT](https://choosealicense.com/licenses/mit/)

## Contribuire - Contributing

Le pull request sono benvenute. Per modifiche importanti, aprire prima un issue per discutere di cosa si vuole cambiare.

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Supportami - Support me

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/matt05)

[![buy-me-a-coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/Matt0550)

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://paypal.me/sillittimatteo)
