# Django Posts API

A RESTful API built with Django for managing posts with JWT authentication, Redis-based token blacklisting, and Stripe-powered wallet system.

## Features

- **User Authentication**: Register and login with JWT tokens
- **Token Blacklisting**: Secure logout with Redis-based token invalidation (auto-expires after 2 days)
- **Posts CRUD**: Create, read, update, and delete posts
- **Role-based Users**: Support for "viewer" and "editor" user types
- **Rating System**: Posts include a 1-5 rating system
- **Wallet System**: User wallets with balance tracking and transaction history
- **Stripe Integration**: Fund wallet via Stripe payments

## Tech Stack

- Python 3.12
- Django 5.2
- PyJWT for authentication
- Redis for token blacklisting
- Stripe for payment processing
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

### Posts

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/posts/` | Get all posts | Yes |
| GET | `/posts/<id>/` | Get a single post | Yes |
| POST | `/posts/create/` | Create a new post (costs wallet fee) | Yes |
| PUT/PATCH | `/posts/<id>/edit/` | Update a post (owner only) | Yes |
| DELETE | `/posts/<id>/delete/` | Delete a post (owner only) | Yes |

### Wallet

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/wallet/balance/` | Get wallet balance | Yes |
| GET | `/wallet/transactions/` | Get transaction history (last 50) | Yes |
| POST | `/wallet/fund/` | Create Stripe payment intent | Yes |
| POST | `/wallet/webhook/stripe/` | Stripe webhook handler | No* |

*Webhook is verified using Stripe signature

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

### Get Wallet Balance

```bash
curl http://localhost:8000/wallet/balance/ \
  -H "Authorization: Bearer <your_token>"
```

Response:
```json
{
  "balance": "100.00",
  "currency": "USD"
}
```

### Get Transaction History

```bash
curl http://localhost:8000/wallet/transactions/ \
  -H "Authorization: Bearer <your_token>"
```

Response:
```json
{
  "transactions": [
    {
      "id": 1,
      "amount": "10.00",
      "type": "deposit",
      "description": "Stripe deposit",
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

### Fund Wallet (Create Payment Intent)

```bash
curl -X POST http://localhost:8000/wallet/fund/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "amount": 10.00
  }'
```

Response:
```json
{
  "client_secret": "pi_xxx_secret_xxx",
  "payment_intent_id": "pi_xxx"
}
```

Use the `client_secret` with Stripe.js on the frontend to complete the payment. Minimum deposit is $1.00.

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
| author | FK | Reference to User |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last update timestamp |

### Wallet

| Field | Type | Description |
|-------|------|-------------|
| user | OneToOne | Reference to User |
| balance | decimal | Current balance (USD) |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last update timestamp |

### Transaction

| Field | Type | Description |
|-------|------|-------------|
| wallet | FK | Reference to Wallet |
| amount | decimal | Transaction amount |
| transaction_type | string | "deposit" or "withdrawal" |
| description | string | Transaction description |
| stripe_payment_intent_id | string | Stripe payment ID (for deposits) |
| created_at | datetime | Transaction timestamp |

## Configuration

### Redis Settings

Redis settings can be configured in `myproject/settings.py`:

```python
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
TOKEN_BLACKLIST_TTL = 60 * 60 * 24 * 2  # 2 days
```

### Stripe Settings

Configure Stripe via environment variables:

```bash
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

### Post Creation Cost

Set the fee deducted from wallet when creating a post:

```python
POST_CREATION_COST = '1.00'  # $1.00 per post
```

## License

MIT
