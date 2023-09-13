<h1 align="center">MicroRide</h1>
MicroRide is a scalable microservice application that showcases a robust implementation of distributed systems and the effective utilization of modern technologies in an event-driven architecture. MicroRide demonstrates key architectural patterns and seamless integration with various tools. Developed as a hands-on project to learn about building microservice applications, MicroRide encompasses essential features while providing insights into future enhancements.

## 🚀 Key Features

- **Microservice Architecture:** MicroRide follows a microservice architecture, ensuring the system's scalability, modularity, and maintainability. Each service is designed with a specific responsibility, making it easy to scale individual components independently.

- **Asynchronous Communication:** The application leverages RabbitMQ, a robust message broker, to enable asynchronous communication between services.
  
- **Efficient Data Storage:** MicroRide uses a combination of relational and NoSQL databases to suit different service requirements. PostgreSQL handles user-account-service,driver-service, payment-service,and ride-service, while MongoDB handles the tracking-service. Redis is utilized as a temporary data store to enhance response time and to improve overall user experience.

- **Authentication and Authorization:** The user-account-service provides a secure and reliable authentication and authorization mechanism. By validating user credentials and storing them in Redis, the application optimizes subsequent requests, reducing latency and ensuring an optimal user experience.

- **Driver Tracking and ETA Calculation:** The tracking-service includes features for finding the nearest available driver using MongoDB geospatial queries and calculating the estimated time of arrival (ETA) for drivers based on their recent location data and speed.

- **Real-time Notifications**: The notification-service employs websockets to deliver real-time notifications to both drivers and users. Whether it's ride cancellations, ride confirmations, driver arrivals, or ride completions, MicroRide ensures timely updates and seamless user experience.

## 📋 Services Overview

1. **User Account Service:** Handles user registration, login, and robust authentication. It serves as the authentication service for other microservices, validating JWT tokens and providing a secure token-based authentication mechanism.

2. **Driver Service:** Responsible for various driver-related tasks, including driver registration, handling driver responses to ride requests (acceptance and rejection), and retrieving driver information.

3. **Ride Service:** Responsible for managing all aspects of ride-related operations, including ride requests, ride confirmations, ride cancellations, and retrieval of past ride history.

4. **Payment Service:** The payment service provides endpoints to simulate payment successes and failures. While it doesn't integrate with an actual payment gateway, it enables testing and validation of payment-related functionalities.
   
5. **Tracking Service:** The tracking service is pivotal for efficient rider-driver matching. It employs MongoDB geospatial queries to locate the nearest available driver, optimizing response time. Additionally, the service calculates driver estimated time of arrival (ETA) using a custom algorithm, factoring in recent location history, distance and the driver average speed. To maintain accuracy, MicroRide provides the client application an endpoint for frequent driver location updates, typically every 30 seconds(configurable), ensuring real-time positioning and enhancing the rider's experience.

6. **Analysis Service:** The analysis service, While not fully functional, its primary function is to gather ride fare price data. This serves as the foundation for future enhancements in data analytics, enabling the service to provide valuable insights into ride fare prices, including trends, patterns, and more accurate pricing information.

7. **Notification Service:** Facilitates real-time notifications to users and drivers about various ride events, improving overall user experience and engagement.

## ⚒️ Technology Stack

- **Backend:** The backend of all services is powered by FastAPI, a modern and high-performance web framework for building APIs with Python. FastAPI's asynchronous capabilities complement the microservices architecture, ensuring exceptional performance and scalability.
  
- **Databases:** PostgreSQL is used for services handling structured data, while MongoDB is utilized for the tracking service's location data storage. Redis acts as a cache for temporary data storage, optimizing performance.

- **Message Broker:** RabbitMQ enables efficient asynchronous communication between services, promoting scalability and flexibility.

- **Websockets:** Websockets are employed in the notification service to provide real-time updates to users and drivers, ensuring timely notifications.
  
- **Docker:** Each microservice is containerized using Docker, enabling seamless deployment across various environments.

- **Helm Charts and Helmfile**: Helmfile and Helm charts are utilized to manage the Kubernetes deployments of the microservices,simplifying service management and scalability.
  
- **Kubernetes:** The services are deployed and orchestrated using Kubernetes, facilitating easy scaling and management.

## 💫 Running MicroRide

To run the MicroRide project follow these simple steps:

### Prerequisites

1. [Helm](https://helm.sh/docs/intro/install/ ) and [Helmfile](https://github.com/roboll/helmfile#installation): Make sure you have Helm and Helmfile installed on your local machine.

2. [Kubernetes Cluster](https://kubernetes.io/docs/setup/): Set up a Kubernetes cluster locally or use any Kubernetes cluster that you can access.

3. [Nginx Ingress Controller](https://kubernetes.github.io/ingress-nginx/deploy/): Ensure that you have an Nginx Ingress Controller deployed in your Kubernetes cluster.

### Step 1: Clone the Repository

Clone the MicroRide repository to your local machine:

```
git clone https://github.com/your-username/MicroRide.git
cd MicroRide
```

### Step 2: Start MicroRide Services

In the project directory, run the start script to deploy all services:

```
./start.sh
```

### Step 3: Port Forwarding (Local Setup Only)

If you are running MicroRide locally, you need to port forward to the Ingress Controller to access the services. Execute the following command:

```
kubectl port-forward svc/nginx-ingress-controller 8080:80
```

### Step 3: Get External IP(Online Setup Only)
If you are running MicroRide on an online Kubernetes cluster, get the external IP of the Ingress Controller by running:
```
kubectl get service ingress-nginx-controller --namespace=ingress-nginx
```

### Step 4: Accessing the API Docs

Documentation for each service can be accessed at the following URLs:

**Locally (using localhost):**
 - User Account Service API Docs: `http://localhost:8080/user-account-service/docs`
- Driver Service API Docs: `http://localhost:8080/driver-service/docs`
- Ride Service API Docs: `http://localhost:8080/ride-service/docs`
- Payment Service API Docs: `http://localhost:8080/payment-service/docs`
- Tracking Service API Docs: `http://localhost:8080/tracking-service/docs`
- Notification Service API Docs: `http://localhost:8080/notification-service/docs`

**Online (using external IP):**
  - User Account Service Docs: `http://EXTERNAL_IP/user-account-service/docs`
  - Driver Service API Docs: `http://EXTERNAL_IP/driver-service/docs`
  - Ride Service API Docs: `http://EXTERNAL_IP/ride-service/docs`
  - Payment Service API Docs: `http://EXTERNAL_IP/payment-service/docs`
  - Tracking Service API Docs: `http://EXTERNAL_IP/tracking-service/docs`
  - Notification Service API Docs: `http://EXTERNAL_IP/notification-service/docs`

Replace `EXTERNAL_IP` with the actual external IP of the Nginx Ingress Controller.

### Step 4: Stop MicroRide Services

To stop all services and clean up the deployment, run the end script:

```
./end.sh
```
