# MicroAnalytics - Complete Project Overview

## System Architecture

MicroAnalytics is a comprehensive demand prediction system with conversational AI integration, built using a modern microservices architecture.

### Core Components

#### 1. Backend API (FastAPI)
- **Location**: `backend/`
- **Main File**: `backend/app.py`
- **Database**: SQLite with SQLAlchemy ORM
- **Features**:
  - RESTful API endpoints for all business entities
  - CRUD operations for products, suppliers, inventory, transactions
  - ML model integration for demand predictions
  - Data validation with Pydantic schemas

#### 2. Frontend Interface (Streamlit)
- **Location**: `frontend/`
- **Main Files**: 
  - `frontend/chatbot_app.py` (primary interface)
  - `frontend/chatbot_app_working.py` (stable version)
  - `frontend/app.py` (alternative interface)
- **Features**:
  - Interactive chatbot interface
  - Data visualization with Plotly
  - Real-time communication with backend API
  - ML prediction visualization

#### 3. Machine Learning Models
- **Location**: `models/`
- **Main File**: `models/predict.py`
- **Supported Models**:
  - Linear Regression
  - Polynomial Regression
  - Advanced models with feature engineering
- **Features**:
  - Model comparison and evaluation
  - Caching system for predictions
  - Automated model selection
  - Performance metrics tracking

#### 4. Conversational AI (Ollama Integration)
- **Location**: `chatbot/`
- **Key Files**:
  - `chatbot/ollama_integration.py`
  - `chatbot/communication_schema.py`
- **Features**:
  - Natural language processing
  - Context-aware responses
  - Integration with business logic
  - Structured communication schema

#### 5. Data Scraping Module
- **Location**: `scraping/`
- **Purpose**: External data collection and processing

## Key Features

### 1. Demand Prediction
- Multiple ML algorithms for demand forecasting
- Historical data analysis
- Seasonal trend detection
- Model performance comparison

### 2. Inventory Management
- Real-time inventory tracking
- Automated reorder point calculations
- Supplier price comparison
- Stock level optimization

### 3. Business Intelligence
- Transaction analysis
- Product performance metrics
- Supplier evaluation
- Revenue forecasting

### 4. Conversational Interface
- Natural language queries
- Interactive data exploration
- Automated report generation
- Context-aware assistance

## Database Schema

### Core Entities
- **Products**: Product catalog with categories
- **Suppliers**: Supplier information and pricing
- **Inventory**: Stock levels and movements
- **Transactions**: Sales and purchase records
- **Categories**: Product categorization
- **Users**: System users and permissions

## API Endpoints

### Product Management
- `GET /products/` - List all products
- `POST /products/` - Create new product
- `GET /products/{id}` - Get product details
- `PUT /products/{id}` - Update product
- `DELETE /products/{id}` - Delete product

### Inventory Operations
- `GET /inventory/` - List inventory items
- `POST /inventory/` - Add inventory item
- `GET /inventory/low-stock` - Get low stock items

### Supplier Management
- `GET /suppliers/` - List suppliers
- `POST /suppliers/` - Create supplier
- `GET /supplier-prices/` - Get price comparisons

### Predictions
- `POST /predict/` - Generate demand predictions
- `GET /predictions/history` - Get prediction history

## Development Workflow

### Setup and Installation
1. **Environment Setup**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Database Initialization**:
   ```bash
   cd backend
   python init_db.py
   python seed_data.py
   ```

3. **Start Services**:
   ```bash
   # Backend API
   cd backend && uvicorn app:app --reload --port 8000
   
   # Frontend Interface
   cd frontend && streamlit run chatbot_app.py --server.port 8501
   
   # Ollama Service (if using conversational AI)
   ollama serve
   ```

### Docker Deployment
- **Configuration**: `docker-compose.yml`
- **Services**: Backend, Frontend, Nginx, Ollama
- **Commands**:
  ```bash
  docker-compose up -d
  docker-compose logs -f
  ```

### Testing
- **Unit Tests**: `tests/`
- **Model Tests**: `tests/test_predict.py`
- **API Tests**: Integrated with FastAPI testing framework

## File Structure Summary

```
MicroAnalitycs/
├── backend/              # FastAPI backend
│   ├── app.py           # Main application
│   ├── models/          # Database models
│   ├── routes/          # API endpoints
│   ├── crud/            # Database operations
│   └── schemas/         # Pydantic schemas
├── frontend/            # Streamlit interfaces
│   ├── chatbot_app.py   # Main chatbot interface
│   └── app.py           # Alternative interface
├── models/              # ML models and utilities
│   ├── predict.py       # Main prediction engine
│   ├── training/        # Model training scripts
│   └── utils/           # Utility functions
├── chatbot/             # Conversational AI
│   ├── ollama_integration.py
│   └── communication_schema.py
├── scraping/            # Data collection
├── tests/               # Test suite
└── docs/                # Documentation
```

## Configuration Files

### Docker Configuration
- `docker-compose.yml` - Multi-service orchestration
- `Dockerfile.backend` - Backend container
- `Dockerfile.frontend` - Frontend container
- `nginx.conf` - Reverse proxy configuration

### System Management
- `run_system.sh` - System startup and management script
- `requirements.txt` - Python dependencies
- `seed_requirements.txt` - Database seeding dependencies

## Model Performance

### Latest Comparison Results
The system tracks model performance with detailed metrics:
- **Accuracy**: R² score, MAE, MSE, RMSE
- **Efficiency**: Training time, prediction speed
- **Robustness**: Cross-validation scores
- **Generalization**: Test set performance

### Model Artifacts
- Trained models stored in `models/artifacts/`
- Cached predictions in `models/cache/`
- Performance history in `models/metrics_history/`

## Security and Best Practices

### Data Protection
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy
- Environment variable configuration
- Secure API endpoints

### Code Quality
- Type hints throughout codebase
- Comprehensive error handling
- Logging and monitoring
- Unit test coverage

## Future Enhancements

### Planned Features
1. **Advanced Analytics**: Time series analysis, forecasting
2. **Mobile Interface**: React Native or Flutter app
3. **Real-time Data**: WebSocket integration
4. **Advanced ML**: Deep learning models, ensemble methods
5. **Multi-tenancy**: Support for multiple businesses

### Scalability Considerations
- Microservices architecture ready for horizontal scaling
- Database optimization for large datasets
- Caching strategies for improved performance
- Load balancing and clustering support

## Deployment Environments

### Development
- Local development with hot reload
- SQLite database for quick setup
- Debug logging enabled

### Production
- Docker containerization
- PostgreSQL or MySQL database
- Nginx reverse proxy
- Environment-specific configuration

## Monitoring and Maintenance

### Logging
- Application logs in `logs/`
- Structured logging format
- Error tracking and alerting

### Performance Monitoring
- API response times
- Model prediction accuracy
- Database query performance
- System resource utilization

## Contact and Support

For questions, issues, or contributions:
- Review the documentation in each module
- Check the test suite for usage examples
- Refer to the API documentation at `/docs` endpoint
- Follow the development workflow outlined above

---

**Last Updated**: December 2024
**Version**: 1.0.0
**Status**: Production Ready
