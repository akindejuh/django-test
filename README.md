# Django Posts API

A RESTful API built with Django for managing posts with JWT authentication and Redis-based token blacklisting.

## Features

- **User Authentication**: Register and login with JWT tokens
- **Token Blacklisting**: Secure logout with Redis-based token invalidation (auto-expires after 2 days)
- **Posts CRUD**: Create, read, update, and delete posts
- **Role-based Users**: Support for "viewer" and "editor" user types
- **Rating System**: Posts include a 1-5 rating system

## Tech Stack

- Python 3.12
- Django 5.2
- PyJWT for authentication
- Redis for token blacklisting
- SQLite (default database)

## Installation

### Prerequisites

- Python 3.10+
- Redis server

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/akindejuh/django-test.git
   cd django-test/myproject
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Start Redis server:
   ```bash
   # macOS with Homebrew
   brew services start redis

   # Or run directly
   redis-server
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register/` | Register a new user |
| POST | `/auth/login/` | Login and get JWT token |
| POST | `/auth/logout/` | Logout and blacklist token |

### Posts (Protected - requires JWT)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/posts/` | Get all posts |
| GET | `/posts/<id>/` | Get a single post |
| POST | `/posts/create/` | Create a new post |
| PUT/PATCH | `/posts/<id>/edit/` | Update a post |
| DELETE | `/posts/<id>/delete/` | Delete a post |

## Usage Examples

### Register a User

```bash
curl -X POST http://localhost:8000/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "password": "securepass123",
    "dob": "1990-01-15",
    "user_type": "editor"
  }'
```

Response:
```json
{
  "message": "User registered successfully",
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "editor"
  }
}
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

### Create a Post

```bash
curl -X POST http://localhost:8000/posts/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "title": "My First Post",
    "description": "This is the content of my post.",
    "rating": 5
  }'
```

### Get All Posts

```bash
curl http://localhost:8000/posts/ \
  -H "Authorization: Bearer <your_token>"
```

### Update a Post

```bash
curl -X PUT http://localhost:8000/posts/1/edit/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "title": "Updated Title",
    "rating": 4
  }'
```

### Delete a Post

```bash
curl -X DELETE http://localhost:8000/posts/1/delete/ \
  -H "Authorization: Bearer <your_token>"
```

### Logout

```bash
curl -X POST http://localhost:8000/auth/logout/ \
  -H "Authorization: Bearer <your_token>"
```

## Data Models

### User

| Field | Type | Description |
|-------|------|-------------|
| email | string | Unique email (used for login) |
| first_name | string | User's first name |
| last_name | string | User's last name |
| password | string | Hashed password |
| dob | date | Date of birth (YYYY-MM-DD) |
| user_type | string | "viewer" or "editor" |
| created_at | datetime | Account creation timestamp |

### Post

| Field | Type | Description |
|-------|------|-------------|
| title | string | Post title (max 200 chars) |
| description | text | Post content |
| rating | integer | Rating from 1 to 5 |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last update timestamp |

## Configuration

Redis settings can be configured in `myproject/settings.py`:

```python
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
TOKEN_BLACKLIST_TTL = 60 * 60 * 24 * 2  # 2 days
```

## License

MIT
