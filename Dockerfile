# The package is not offical, for production code we might want to build our own image with python and node
# !! The repo is marked "Experimental" !!
FROM nikolaik/python-nodejs:python3.14-nodejs25-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# !!! for now this is fine since, we do not use docker for deployment !!!
ENV DEBUG=True

WORKDIR /home/pn/app


# Install uv for faster Python package management
#RUN #pip install --no-cache-dir uv


# Install dependencies
COPY pyproject.toml uv.lock* ./
RUN uv pip install --system -r pyproject.toml


WORKDIR /home/pn/app/theme/static_src/
COPY theme/static_src/package-lock.json theme/static_src/package.json* ./
RUN npm ci && npm cache clean --force
WORKDIR /home/pn/app/
COPY . .

# Copy project
RUN SECRET_KEY=nothing python manage.py tailwind build
RUN SECRET_KEY=nothing python manage.py collectstatic --noinput;

USER pn

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
