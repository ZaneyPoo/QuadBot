### QuadBot

QuadBot is a silly little Discord bot for my friends' server.


### Build

1. Ensure docker and docker-compose are installed and working.

2. Clone the repo to your desired location.

3. Build the image by running
```bash
$ docker build -t quadbot .
```

4. Create a .env file in the root of the project directory and set DISCORD_TOKEN to the
API token you'd like to use.

Like this:
```bash
DISCORD_TOKEN= #Put your API token here
# Optional: if you have a test instance and you don't want 
# command prefixes to conflict
QUADBOT_TESTING=true
```

5. Then run this command to start the container:
```bash 
$ docker compose up 
```
