import logging
import os

from flask import Flask


logging.basicConfig(level=logging.DEBUG)
logging.getLogger("slack").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

# This instantiates the core Flask app instance
app = Flask(__name__)

# We load the configuration into the global app config from the object specified
app.config.from_object(os.environ.get("FLASK_CONFIG", "app.config.DevelopmentConfig"))

from app.handlers import commands, events, interactive, heartbeat

# Start the server on port 5000
if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)))
