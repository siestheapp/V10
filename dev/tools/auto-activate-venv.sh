#!/bin/bash
# Auto-activate virtual environment for V10 project
# Add this to your ~/.zshrc file:

# V10 Project Auto-Activation
function cd() {
    builtin cd "$@"
    if [[ $(pwd) == "/Users/seandavey/projects/V10"* ]] && [[ -z "$VIRTUAL_ENV" ]]; then
        if [[ -f "/Users/seandavey/projects/V10/venv/bin/activate" ]]; then
            echo "🐍 Auto-activating V10 virtual environment..."
            source /Users/seandavey/projects/V10/venv/bin/activate
        fi
    fi
}

# Alternative: Add alias to easily activate
alias v10env="cd /Users/seandavey/projects/V10 && source venv/bin/activate" 