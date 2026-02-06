"""
Football Agent - Main entry point.
Run this file to start the server.
"""

import uvicorn


def main():
    """Start the Football Agent server."""
    print("⚽ Starting Football Agent...")
    print("🌐 Open http://localhost:8000 in your browser")
    print("📚 API docs at http://localhost:8000/docs")
    
    uvicorn.run(
        "backend.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
