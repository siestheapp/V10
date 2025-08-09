#!/bin/bash
# Quick access script for V10 project files

case "$1" in
    "ref"|"reference"|"quick")
        open docs/development/QUICK_REFERENCE.md
        ;;
    "db"|"database") 
        open docs/database/DATABASE_CONFIG.md
        ;;
    "start"|"howto")
        open docs/development/start_howto.md
        ;;
    "reorg"|"reorganization")
        open docs/REORGANIZATION_SUMMARY.md
        ;;
    "session"|"log")
        open docs/development/SESSION_LOG.md
        ;;
    *)
        echo "Quick access to V10 project files:"
        echo "  qa ref      - QUICK_REFERENCE.md"
        echo "  qa db       - DATABASE_CONFIG.md" 
        echo "  qa start    - start_howto.md"
        echo "  qa reorg    - REORGANIZATION_SUMMARY.md"
        echo "  qa session  - SESSION_LOG.md"
        ;;
esac 