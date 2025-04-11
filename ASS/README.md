# Online Event Booking Platform
A microservices-based platform for booking events.

## Microservices
1. **User Service**: Manages user authentication and profiles.
2. **Event Service**: Manages event listings and details.
3. **Booking Service**: Handles ticket bookings and payments.
4. **Notification Service**: Sends confirmation notifications.

## Setup
1. Clone the repository.
2. Install dependencies for each microservice using `pip install -r requirements.txt`.
3. Set up databases (PostgreSQL and MongoDB) and RabbitMQ.
4. Run each microservice using:
   - `uvicorn main:app --reload` for FastAPI services.
   - `flask run` for Flask services.