# 📝 MyNotesApp
https://quiznotes.ink

Web application that allows users to take notes while staying organized with the ability to generate quizzes based on the notes using OpenAI's integrated LLM.  Uses Flask for the backend and MongoDB for the Database.  Currently deployed on the cloud and containerized with Docker / Docker Compose.


**3/4/26 Update**
- Deployed app onto AWS using an EC2 instance
- Configured Certbot for HTTPS
- Enabled Nginx as reverse proxy for encryption of SSL/TLS

**3/5/26 Update**
- Added gunicorn for improved performance
- Added Security Groups to AWS for strengthened security
