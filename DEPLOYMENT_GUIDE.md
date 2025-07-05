# MicroAnalytics Deployment Guide

## Quick Start

### Prerequisites
- Python 3.8+
- Docker and Docker Compose (for containerized deployment)
- Git
- Ollama (for AI chatbot features)

### Local Development Setup

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd MicroAnalitycs
   git checkout dev
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Database Setup**:
   ```bash
   cd backend
   python setup_database.py  # Initialize database schema
   python seed_data.py       # Load sample data
   ```

3. **Start Backend API**:
   ```bash
   uvicorn backend.app:app --reload
   # API will be available at http://localhost:8000
   # Documentation at http://localhost:8000/docs
   ```

4. **Start Frontend (New Terminal)**:
   ```bash
   cd frontend
   streamlit run chatbot_app.py --server.port 8501
   # Frontend will be available at http://localhost:8501
   ```

5. **Start Ollama (Optional, for AI features)**:
   ```bash
   ollama serve
   ollama pull llama2  # Or your preferred model
   ```

### Docker Deployment

1. **Build and Start Services**:
   ```bash
   chmod +x run_system.sh
   ./run_system.sh start
   ```

2. **Or manually with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

3. **Check Service Status**:
   ```bash
   ./run_system.sh status
   # Or: docker-compose ps
   ```

### Service URLs
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Nginx (if configured)**: http://localhost:80

## Production Deployment

### Environment Variables
Create a `.env` file:
```env
# Database
DATABASE_URL=sqlite:///./microanalytics.db
# Or for PostgreSQL: postgresql://user:password@localhost/dbname

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,your-domain.com
```

### Production Checklist
- [ ] Update `DEBUG=false` in environment
- [ ] Configure proper database (PostgreSQL/MySQL)
- [ ] Set up SSL certificates
- [ ] Configure domain and DNS
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline

## Architecture

### System Components
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │────│   Nginx     │────│   Backend   │
│ (Streamlit) │    │ (Reverse    │    │  (FastAPI)  │
│   :8501     │    │  Proxy)     │    │    :8000    │
└─────────────┘    └─────────────┘    └─────────────┘
                                              │
                   ┌─────────────┐           │
                   │   Ollama    │───────────┤
                   │    :11434   │           │
                   └─────────────┘           │
                                              │
                   ┌─────────────┐           │
                   │  Database   │───────────┘
                   │  (SQLite/   │
                   │ PostgreSQL) │
                   └─────────────┘
```

### Data Flow
1. User interacts with Streamlit frontend
2. Frontend sends requests to FastAPI backend
3. Backend processes requests, queries database
4. ML models generate predictions when needed
5. Ollama provides AI responses for chatbot
6. Results displayed in frontend interface

## Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   # Check what's using the port
   lsof -i :8000
   # Kill the process or use different port
   uvicorn app:app --port 8001
   ```

2. **Database Connection Issues**:
   ```bash
   # Reinitialize database
   cd backend
   rm microanalytics.db  # Remove existing database
   python setup_database.py
   python seed_data.py
   ```

3. **Missing Dependencies**:
   ```bash
   pip install -r requirements.txt
   # If using seed data:
   pip install -r backend/seed_requirements.txt
   ```

4. **Ollama Not Responding**:
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   # Restart Ollama service
   ollama serve
   ```

### Logs and Debugging

1. **Application Logs**:
   ```bash
   tail -f logs/microanalytics_*.log
   ```

2. **Docker Logs**:
   ```bash
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

3. **Backend Debug Mode**:
   ```bash
   cd backend
   uvicorn app:app --reload --log-level debug
   ```

## Monitoring

### Health Checks
- Backend: `http://localhost:8000/health`
- Frontend: Should respond to HTTP requests
- Database: Check connection in backend logs

### Performance Monitoring
- API response times in logs
- Database query performance
- Model prediction accuracy in `models/metrics/`
- System resource usage with `htop` or `docker stats`

## Backup and Recovery

### Database Backup
```bash
# SQLite
cp backend/microanalytics.db backup/microanalytics_$(date +%Y%m%d).db

# PostgreSQL
pg_dump dbname > backup/microanalytics_$(date +%Y%m%d).sql
```

### Model Artifacts
```bash
# Backup trained models
tar -czf backup/models_$(date +%Y%m%d).tar.gz models/artifacts/
```

## Updates and Maintenance

### Updating the System
```bash
git pull origin dev
pip install -r requirements.txt
# Restart services
./run_system.sh restart
```

### Database Migrations
```bash
cd backend
# Create migration script if schema changes
python migrate_database.py
```

## Security Considerations

### Production Security
- Use HTTPS in production
- Configure proper CORS settings
- Set up authentication and authorization
- Regular security updates
- Monitor for vulnerabilities
- Secure database connections
- Environment variable protection

### Network Security
- Configure firewall rules
- Use VPN for sensitive environments
- Monitor access logs
- Set up intrusion detection

---

For additional support, refer to:
- `PROJECT_OVERVIEW.md` for system architecture
- `WORKFLOW_COMPLETO.md` for development workflow
- API documentation at `/docs` endpoint
- Individual module documentation in respective directories
