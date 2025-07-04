# Happyloop Challenge - AI-Powered Soda Vending Machine

A simple AI-powered API for a soda vending machine that interprets natural language commands to sell products, track inventory, and manage transactions.

## Features

- Natural language processing for user interactions
- Product inventory management
- Transaction history tracking
- RESTful API with FastAPI
- SQLite database with SQLModel ORM
- Docker containerization with Nginx load balancer

## Architecture

The application is built with 3 core modules:

- **Products Module**: Handles product management operations including create, update, remove, and list products. Manages inventory and stock levels.
- **Purchase Module**: Processes natural language queries using AI, interprets user intent from text input, and calls the purchase service with parsed user intent.
- **Transaction Module**: Handles and stores transaction history, provides transaction records and analytics, and manages purchase logging.

## Technology Stack

- **FastAPI** - REST API framework
- **SQLModel** - Database ORM
- **SQLite** - Database
- **Instructor** - AI response parsing
- **OpenAI GPT** - Natural language processing
- **Nginx** - Load balancer and reverse proxy
- **Docker** - Containerization
- **uv** - Python package management

## Quick Start

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/JulioPeixoto/happyloop-challenge.git
cd happyloop-challenge
```

2. Install dependencies:
```bash
uv sync
```

3. Set up environment variables:
```bash
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

4. Run database migrations:
```bash
uv run makemigrations "Initial migration"
uv run migrate
```

5. Start the application:
```bash
docker-compose up --build
```

The API will be available at `http://localhost/docs`

## API Endpoints

### Chat Interface
- `POST /api/v1/chat` - Natural language interaction

Example:
```json
{
  "message": "I want to buy 3 cokes"
}
```

### Products
- `GET /api/v1/products` - List all products
- `POST /api/v1/products` - Create a new product
- `GET /api/v1/products/{id}` - Get product by ID
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product

### Transactions
- `GET /api/v1/transactions` - Get transaction history
- `GET /api/v1/transactions/{id}` - Get transaction by ID

## Usage Examples

### Buy Products
```bash
curl -X POST "http://localhost/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to buy 2 sprites"}'
```

### Check Inventory
```bash
curl -X POST "http://localhost/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What do you have in stock?"}'
```

### Check Stock Levels
```bash
curl -X POST "http://localhost/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "How many cokes are left?"}'
```

## Development

### Database Commands

```bash
# Create new migration
uv run makemigrations "Migration description"

# Apply migrations
uv run migrate

# Start development server
uv run dev
```

### Project Structure
