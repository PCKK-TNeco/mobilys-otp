##  Local Environment Setup Procedure

Follow these steps to set up the local development environment for the `mobilys-be` project.

1. Clone the Repository
   Clone the repository to your local development machine:
```
   git clone https://github.com/PCKK-TNeco/mobilys-otp.git
   cd mobilys-otp
```

2. Create a Feature Branch
   Follow the branch naming convention for new features:
```
   git checkout -b feature/{ticket-name}/feature-name

   Example:
   git checkout -b feature/SCRUM-123/add-login-api
```


4. Build Docker Image and Start Containers
   Run the following command to start the development environment:
```
   docker-compose up --build
```

   This will:
   - Build the Docker image
   - Start the fastapi and nginx server

 You're all set! Once the containers are running:
- FastApi server: Port 8001 
- Nginx server: Port 8080
