# Техническая архитектура "Робот Светлана"

## Общая архитектура

### Диаграмма компонентов

```
┌─────────────────────────────────────────┐
│              Web Client                 │
│          (Vue.js SPA)                   │
│                                         │
│  - Dashboard                            │
│  - Document Editor                      │
│  - Approval Interface                   │
│  - Admin Panel                          │
└─────────────────┬───────────────────────┘
                  │ HTTP/HTTPS
                  │ REST API
┌─────────────────┴───────────────────────┐
│         FastAPI Backend                 │
│       (Python Application)              │
│                                         │
│  ┌────────────────────────────────┐    │
│  │   Auth Service                  │    │
│  │   - JWT Token Management       │    │
│  │   - Role-based Access Control  │    │
│  └────────────────────────────────┘    │
│                                         │
│  ┌────────────────────────────────┐    │
│  │   Document Service             │    │
│  │   - Create/Update/Delete       │    │
│  │   - Generate from templates    │    │
│  │   - Export to DOCX/PDF         │    │
│  └────────────────────────────────┘    │
│                                         │
│  ┌────────────────────────────────┐    │
│  │   Template Engine              │    │
│  │   - Load templates             │    │
│  │   - Generate content           │    │
│  │   - Apply formatting rules     │    │
│  └────────────────────────────────┘    │
│                                         │
│  ┌────────────────────────────────┐    │
│  │   Workflow Engine              │    │
│  │   - Route documents            │    │
│  │   - Track approval status      │    │
│  │   - Manage versions            │    │
│  └────────────────────────────────┘    │
│                                         │
│  ┌────────────────────────────────┐    │
│  │   Validation Service           │    │
│  │   - Check required fields     │    │
│  │   - Validate style            │    │
│  │   - Ensure GOST compliance    │    │
│  └────────────────────────────────┘    │
│                                         │
│  ┌────────────────────────────────┐    │
│  │   Notification Service         │    │
│  │   - Send emails                │    │
│  │   - In-app notifications       │    │
│  └────────────────────────────────┘    │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│         SQLite (Main Database)          │
│                                         │
│  - Users, Documents, Approvals         │
│  - Templates, Versions                 │
│  - File metadata, Indexes              │
└─────────────────────────────────────────┘
         │
┌────────┴────────┐
│  File System    │
│  (Local Storage)│
│                 │
│  - DOCX files   │
│  - PDF files    │
│  - Attachments  │
└─────────────────┘

Примечание: PostgreSQL, Redis (кэш) и MinIO (объектное хранилище) 
будут добавлены на этапе масштабирования при необходимости.
```

## Компоненты системы

### Backend (Python/FastAPI)

#### Структура проекта

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration settings
│   │
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── documents.py        # Document endpoints
│   │   ├── templates.py        # Template endpoints
│   │   ├── approvals.py        # Approval endpoints
│   │   └── users.py            # User management
│   │
│   ├── core/                   # Core functionality
│   │   ├── security.py        # JWT, password hashing
│   │   ├── exceptions.py      # Custom exceptions
│   │   └── dependencies.py    # Dependency injection
│   │
│   ├── services/               # Business logic
│   │   ├── document_service.py
│   │   ├── template_service.py
│   │   ├── workflow_service.py
│   │   ├── validation_service.py
│   │   └── notification_service.py
│   │
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── template.py
│   │   └── approval.py
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── user_schema.py
│   │   ├── document_schema.py
│   │   └── approval_schema.py
│   │
│   ├── db/                     # Database
│   │   ├── session.py
│   │   └── base.py
│   │
│   └── utils/                  # Utilities
│       ├── document_generator.py  # DOCX/PDF generation
│       ├── style_validator.py     # Style checking
│       └── gost_validator.py      # GOST compliance
│
├── alembic/                    # Database migrations
├── tests/                      # Unit tests
└── requirements.txt
```

#### Основные модули

**1. Document Service**
- Генерация документов из запроса чата + метаданных (MVP)
- Экспорт в форматы DOCX/PDF
- Сохранение результата и метаданных
- (после MVP) Загрузка/редактирование существующих, версии

**1.1. LLM Agent (новый компонент)**
- Классификация типа документа по запросу пользователя
- Извлечение сути и параметров из запроса
- Генерация текста по шаблонам с официально-деловым стилем
- Использование инструментов для подстановки данных

**2. Template Engine**
- Загрузка шаблонов из БД или файловой системы
- Парсинг шаблонов с плейсхолдерами ({{адресат}}, {{тема}}, {{содержание}})
- Замена плейсхолдеров на реальные данные
- Применение правил форматирования
- Поддержка условной логики в шаблонах

**2.1. Agent Tools (инструменты агента)**
- `classify_document_type`: определение типа документа по запросу
- `extract_parameters`: извлечение сути, суммы, сроков, ответственных
- `generate_content`: генерация текста по шаблону с официальным стилем
- `substitute_data`: подстановка данных организации, должностей, дат
- `validate_style`: проверка соответствия официально-деловому стилю

**3. Workflow Engine**
- Определение маршрутов согласования
- Отслеживание текущего этапа согласования
- Управление переходами между статусами
- Версионирование при изменениях
- История действий и комментариев

**4. Validation Service**
- Проверка полноты обязательных полей
- Валидация стиля и тона текста
- Проверка соответствия ГОСТ Р 7.0.97-2016
- Контроль корректности реквизитов
- Проверка дат и номеров

**5. Notification Service**
- Отправка email уведомлений
- In-app уведомления через WebSocket
- Напоминания о сроках согласования
- Интеграция с внешними системами

### Frontend (Vue.js)

#### Структура проекта

```
frontend/
├── public/
├── src/
│   ├── main.js
│   ├── App.vue
│   │
│   ├── views/                  # Vue pages
│   │   ├── Chat.vue                # Чат для генерации документов (MVP)
│   │   ├── GeneratedList.vue       # Список сгенерированных документов (MVP)
│   │   └── AdminPanel.vue          # (после MVP) расширение
│   │
│   ├── components/             # Reusable components
│   │   ├── ChatInput.vue           # Поле ввода чата
│   │   ├── ChatMessages.vue        # Сообщения чата
│   │   └── DocumentViewer.vue      # Просмотр PDF/DOCX
│   │
│   ├── router/                 # Vue Router
│   │   └── index.js
│   │
│   ├── store/                  # State management
│   │   ├── index.js
│   │   ├── auth.js
│   │   └── documents.js            # generate, list, download
│   │
│   ├── services/               # API services
│   │   ├── api.js
│   │   ├── authService.js
│   │   └── documentService.js      # generateFromChat, getList, download
│   │
│   ├── utils/                  # Utilities
│   │   ├── formatters.js
│   │   └── validators.js
│   │
│   └── styles/                 # Global styles
│
├── package.json
└── vite.config.js             # Build config
```

#### Основные страницы

**1. Dashboard**
- Статистика документов
- Быстрые действия
- Уведомления
- Последние документы

**2. Document Editor**
- Пошаговый мастер создания
- Редактор текста с проверкой стиля
- Предпросмотр документа
- Прикрепление файлов

**3. Approval Queue**
- Список документов на согласование
- Фильтры и сортировка
- Возможность правки
- История изменений

**4. Document List**
- Список всех документов
- Поиск и фильтрация
- Статусы и даты
- Экспорт и действия

**5. Admin Panel**
- Управление пользователями
- Настройка шаблонов
- Конфигурация маршрутов
- Мониторинг системы

## База данных

### Схема данных

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    department VARCHAR(255),
    position VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Documents table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_by INTEGER REFERENCES users(id),
    outgoing_number VARCHAR(100),
    outgoing_date DATE,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Document versions
CREATE TABLE document_versions (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    version_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    changes_summary TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Approvals
CREATE TABLE approvals (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    approver_id INTEGER REFERENCES users(id),
    status VARCHAR(50) NOT NULL,
    comments TEXT,
    approved_at TIMESTAMP,
    position_in_queue INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Templates
CREATE TABLE templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Attachments
CREATE TABLE attachments (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    uploaded_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## API Specification

### Authentication

```
POST /api/auth/login
Body: { email, password }
Response: { access_token, refresh_token, user }

POST /api/auth/refresh
Body: { refresh_token }
Response: { access_token }
```

### Documents (MVP)

```
POST /api/documents/generate
Body: { documentType, metadata, prompt }
Response: { documentId, title, download: { docxUrl, pdfUrl } }

GET /api/documents
Query: page, limit, type
Response: { documents[], total }

POST /api/documents
Body: { type, title, content, metadata }
Response: { document }

GET /api/documents/{id}
Response: { document }

DELETE /api/documents/{id}
Response: 204

GET /api/documents/{id}/download
Query: format='docx' | 'pdf'
Response: Binary file
```

### Approvals

```
GET /api/approvals/pending
Response: { documents[] }

POST /api/approvals/{id}/approve
Body: { comments?, requires_changes }
Response: { approval }

POST /api/approvals/{id}/reject
Body: { comments }
Response: { approval }
```

## Технологический стек

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM для работы с БД
- **Alembic**: Миграции БД
- **Pydantic**: Валидация данных
- **python-docx**: Генерация DOCX
- **ReportLab**: Генерация PDF
- **JWT**: Аутентификация
- **python-multipart**: Загрузка файлов
- **LangChain/LangGraph**: LLM агент с инструментами
- **OpenAI/Anthropic**: LLM для генерации текста

### Дополнительно (для масштабирования)
- **PostgreSQL**: Production база данных
- **Celery**: Асинхронные задачи
- **Redis**: Кэш и брокер сообщений
- **MinIO**: Объектное хранилище для файлов

### Frontend
- **Vue 3**: Progressive JavaScript framework
- **Pinia**: State management
- **Vue Router**: Client-side routing
- **Axios**: HTTP client
- **Vuetify**: Material Design components
- **Monaco Editor**: Code editor для текста
- **PDF.js**: Просмотр PDF файлов
- **Vite**: Build tool

### Database
- **SQLite**: Основная база данных для MVP
  - Все основные данные (users, documents, approvals, templates)
  - Файловая система для хранения документов
  - Простота развертывания и разработки
- **PostgreSQL**: Production база данных (для масштабирования)
- **Redis**: Кэш и брокер сообщений (опционально, для масштабирования)
- **MinIO**: Объектное хранилище (опционально, для масштабирования)

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Local development
- **NGINX**: Reverse proxy
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization

## Развертывание

### Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# SQLite база создается автоматически при первом запуске
```

### Production (упрощенная версия)

```yaml
# docker-compose.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl

  backend:
    build: ./backend
    environment:
      - SECRET_KEY=your-secret-key-here
      - DATABASE_URL=sqlite:///./app.db
    volumes:
      - ./data:/app/data  # Для SQLite и файлов

  frontend:
    build: ./frontend
    depends_on:
      - backend

# PostgreSQL для production (опционально):
# postgres:
#   image: postgres:14
#   environment:
#     - POSTGRES_DB=documents
#     - POSTGRES_USER=admin
#     - POSTGRES_PASSWORD=secret
#   volumes:
#     - postgres_data:/var/lib/postgresql/data

volumes:
  # postgres_data:  # Только для PostgreSQL
```

## Безопасность

### Аутентификация и авторизация
- JWT токены с коротким временем жизни
- Ролевая модель доступа (RBAC)
- Refresh токены для обновления сессий

### Защита данных
- Шифрование данных в покое (AES-256)
- Шифрование данных в передаче (TLS 1.3)
- Маскирование персональных данных в логах
- Регулярные бэкапы с шифрованием

### Аудит и мониторинг
- Логирование всех действий пользователей
- Мониторинг подозрительной активности
- Алерты на критические события

## Масштабируемость

### Горизонтальное масштабирование
- Микросервисная архитектура
- Load balancing на уровне API Gateway
- Кэширование на нескольких уровнях

### Вертикальное масштабирование
- Автоматическое масштабирование контейнеров
- Мониторинг ресурсов и производительности
- Оптимизация запросов к базе данных
