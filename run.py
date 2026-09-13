import os

from dotenv import load_dotenv

load_dotenv()

from app import create_app  # noqa: E402
from app.config import DevConfig, ProdConfig  # noqa: E402

config = ProdConfig if os.environ.get("FLASK_ENV") == "production" else DevConfig
app = create_app(config)

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], port=5000)
