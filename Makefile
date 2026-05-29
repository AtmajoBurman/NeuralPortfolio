.PHONY: dev frontend backend

# Run both frontend and backend concurrently
dev:
	@$(MAKE) -j 2 frontend backend

frontend:
	@echo "Starting Frontend Server..."
	cd frontend-user && npm run dev

backend:
	@echo "Starting Backend Server..."
	cd backend && python run.py
