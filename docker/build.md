# Build

This project uses Docker and Docker Compose to isolate the application and its dependencies in containers, so that it runs always in the same environment and avoids compatibility issues. Therefore, this tools are needed to build the project.

## Running the application:
- Frontend:
  - On Linux:
  ```bash
  chmod +x dev-setup.sh 
  sudo ./dev-setup.sh
  ```
  - On Windows:
  ```bash
  ./dev-setup.bat
  ```

## Accessing the application
In any web browser of your preference
- Frontend: http://localhost:5173/

## Useful Docker commands:
- Build and start containers: ```docker compose up --build```

- Start in detached mode: ``` docker compose up -d ```

- Stop all containers: ``` docker compose down ```
