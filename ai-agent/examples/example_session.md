# Example Session: Building a Todo API

This is an example conversation showing how to use the multi-agent system to build a complete project.

## Session Transcript

```
👤 You: @planner build a REST API for a todo application with Python Flask

🤖 Planner: I'll design a comprehensive REST API for a todo application using Flask.

## Project Overview
A RESTful API for managing todo items with CRUD operations, built with Flask and SQLite.

## Architecture
- **Backend Framework**: Flask (Python)
- **Database**: SQLite (easy setup, can upgrade to PostgreSQL later)
- **API Style**: RESTful with JSON responses
- **Authentication**: Basic (can add JWT later)

## Tech Stack
- **Flask**: Lightweight web framework
- **Flask-SQLAlchemy**: ORM for database operations
- **Flask-CORS**: Handle cross-origin requests
- **SQLite**: Database (development)

## Folder Structure
```
todo-api/
├── app.py              # Main application
├── models.py           # Database models
├── config.py           # Configuration
├── requirements.txt    # Dependencies
└── tests/
    └── test_api.py     # API tests
```

## API Endpoints
- `GET /todos` - List all todos
- `GET /todos/<id>` - Get specific todo
- `POST /todos` - Create new todo
- `PUT /todos/<id>` - Update todo
- `DELETE /todos/<id>` - Delete todo

## Implementation Steps
1. Set up project structure
2. Install dependencies
3. Create database models
4. Implement API endpoints
5. Add error handling
6. Write tests
7. Run and verify

Ready to proceed with implementation?

---

👤 You: @developer start implementing the backend

🤖 Developer: I'll create the Flask API with all necessary files.

[Creates files: app.py, models.py, config.py, requirements.txt]

✅ Created todo-api/requirements.txt
✅ Created todo-api/config.py
✅ Created todo-api/models.py
✅ Created todo-api/app.py

All files created! The API includes:
- Complete CRUD operations
- SQLite database with SQLAlchemy
- Error handling
- JSON responses
- CORS support

To run:
```bash
cd todo-api
pip install -r requirements.txt
python app.py
```

The API will be available at http://localhost:5000

---

👤 You: @tester write tests for the API

🤖 Tester: I'll create comprehensive tests for the Todo API.

[Creates test file and runs tests]

✅ Created todo-api/tests/test_api.py

Test suite includes:
- Test creating todos
- Test listing todos
- Test getting specific todo
- Test updating todos
- Test deleting todos
- Test error cases (404, 400)

Running tests...

```bash
pytest tests/test_api.py -v
```

Results:
✅ test_create_todo PASSED
✅ test_list_todos PASSED
✅ test_get_todo PASSED
✅ test_update_todo PASSED
✅ test_delete_todo PASSED
✅ test_get_nonexistent_todo PASSED

All tests passed! The API is working correctly.

---

👤 You: @developer add a feature to mark todos as complete

🤖 Developer: I'll add the completion feature to the API.

[Updates models.py and app.py]

✅ Updated models.py - Added 'completed' field
✅ Updated app.py - Added PATCH /todos/<id>/complete endpoint

New endpoint:
- `PATCH /todos/<id>/complete` - Toggle todo completion status

Example usage:
```bash
curl -X PATCH http://localhost:5000/todos/1/complete
```

The database will be automatically updated with the new field.

---

👤 You: @tester test the new completion feature

🤖 Tester: I'll add tests for the completion feature.

[Updates test file and runs tests]

✅ Updated tests/test_api.py - Added completion tests

New tests:
- test_complete_todo
- test_uncomplete_todo
- test_complete_nonexistent_todo

Running tests...

Results:
✅ All 9 tests passed!

The completion feature is working correctly.

---

👤 You: run the application

🤖 Developer: Starting the Flask application...

```bash
python app.py
```

Output:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

✅ Application is running!

You can now:
1. Create todos: POST http://localhost:5000/todos
2. List todos: GET http://localhost:5000/todos
3. Update todos: PUT http://localhost:5000/todos/1
4. Complete todos: PATCH http://localhost:5000/todos/1/complete
5. Delete todos: DELETE http://localhost:5000/todos/1

Example request:
```bash
curl -X POST http://localhost:5000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn AI agents", "description": "Build a multi-agent system"}'
```
```

## Summary

In this session, we:
1. ✅ Planned the architecture with @planner
2. ✅ Implemented the API with @developer
3. ✅ Wrote tests with @tester
4. ✅ Added a new feature with @developer
5. ✅ Tested the feature with @tester
6. ✅ Ran the application

The entire process was automated by the AI agents, demonstrating:
- Intelligent agent routing
- Autonomous tool usage
- File creation and modification
- Command execution
- Testing and verification

## Key Takeaways

1. **Agent Specialization**: Each agent focuses on its expertise
2. **Tool Usage**: Agents automatically use tools to accomplish tasks
3. **Iteration**: Easy to add features and test incrementally
4. **Automation**: Minimal manual intervention required
5. **Quality**: Code includes error handling, tests, and documentation
