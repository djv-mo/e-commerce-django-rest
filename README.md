E-Commerce Project

Welcome to the E-Commerce Project! This is a simple online store where users can browse and purchase products.
Features

    User authentication
    Product listings and categories
    Shopping cart
    Checkout with payment processing
    Order history and tracking
    Admin dashboard for managing products and orders

Technologies

    Django for the backend
    Stripe for payment processing

Installation

To set up the project locally, follow these steps:

    Clone the repository to your local machine

git clone https://github.com/user/e-commerce-project.git

    Create a virtual environment and activate it

python -m venv ecommerce-env
source ecommerce-env/bin/activate

    Install the requirements

pip install -r requirements.txt

    Set up the database

python manage.py makemigrations
python manage.py migrate

    Create a superuser

python manage.py createsuperuser

    Run the server and visit the site at http://localhost:8000

python manage.py runserver

Docker Setup

    Install Docker on your machine.

    Clone the project repository:

git clone https://github.com/USERNAME/PROJECT_NAME.git

    Navigate to the project directory:

cd PROJECT_NAME

    Build the Docker image:

docker build -t PROJECT_NAME .

    Run the Docker container:

docker run -p 8000:8000 PROJECT_NAME

    Open your web browser and go to http://localhost:8000 to view the project.

    To stop the Docker container, press CTRL + C in the terminal.

environmental variables

export SECRET_KEY="your_secret_key"
export DEBUG=True
export ALLOWED_HOSTS="localhost,127.0.0.1"
export DATABASE_URL="postgresql://user:password@localhost:5432/database_name"
export STRIPE_PUBLISHABLE_KEY="your_publishable_key"
export STRIPE_SECRET_KEY="your_secret_key"
export STRIPE_LIVE_MODE=False
export DJSTRIPE_WEBHOOK_SECRET="your_webhook_secret"

License

This project is licensed under the MIT License. See the LICENSE file for more details.
