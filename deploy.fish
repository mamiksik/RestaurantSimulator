 # Script to take care of building and dopleyin the app to azure

 echo "Collect static files"
 uv run python manage.py collectstatic --no-input

 echo "Deploy to Azure"
 az webapp up --runtime PYTHON:3.14 --sku F1 --logs --name restaurantsim