<h1 align="center">MicroRide</h1>
MicroRide is a scalable and modular microservice application designed to showcase my proficiency in building distributed systems and effectively utilizing modern technologies. While the project focuses on a simplified ride application, it demonstrates key architectural patterns and integration with various tools.

## Key Features

- **Microservices Architecture:** MicroRide follows a microservices architecture, enabling scalability, modularity, and maintainability. Each service has its own responsibility, allowing for easy scaling of individual components.

- **Asynchronous Communication:** The application leverages RabbitMQ, a robust message broker, to enable asynchronous communication between services. This promotes loose coupling and enhances overall system performance.

- **Efficient Data Storage:** MicroRide uses a combination of relational and NoSQL databases to suit different service requirements. PostgreSQL handles user-account-service,driver-service, payment-service,and ride-service, while MongoDB handles the tracking-service. Redis is utilized as a temporary data store to improve response times.

- **Authentication and Authorization:** The user-account-service provides robust authentication and authorization functionalities. When a user accesses a service, the service validates their credentials by making an initial request to the user-account-service. Once the credentials are verified as valid, the service securely stores the credentials in Redis, acting as a temporary data store. This optimization eliminates the need for repeated network requests to the user-account-service for subsequent requests, significantly improving performance and reducing latency.

- **Real-time Notifications**: The notification-service employs websockets to deliver real-time notifications to both drivers and users. Notifications are sent for various ride-related events, such as ride cancellations, ride confirmations, driver arrivals, and ride completions, ensuring timely updates and a seamless user experience.

