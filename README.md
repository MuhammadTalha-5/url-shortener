# URL Shortener 🔗

A simple and efficient URL shortener service built with Flask and Docker. Shorten long URLs and track click statistics with a clean web interface and REST API.

## Features ✨

- **URL Shortening**: Convert long URLs to short, memorable codes
- **Click Tracking**: Monitor how many times each short URL is clicked
- **Web Interface**: User-friendly web UI for easy URL management
- **REST API**: Programmatic access to all functionality
- **Data Persistence**: SQLite database with Docker volume persistence
- **Dockerized**: Easy deployment with Docker and Docker Compose
- **Health Checks**: Built-in health monitoring endpoints

## Tech Stack 🛠️

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Containerization**: Docker & Docker Compose
- **Frontend**: HTML, CSS, JavaScript
- **API**: RESTful JSON API

## Quick Start 🚀

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/MuhammadTalha-5/url-shortener.git
cd url-shortener

# Build and run with Docker Compose
docker-compose up --build -d

# Access the application
open http://localhost:5000