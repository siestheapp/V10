#!/bin/bash

# Setup script to add V10 startup alias to your shell configuration

PROJECT_DIR="/Users/seandavey/projects/V10"
ALIAS_LINE="alias v10='cd $PROJECT_DIR && ./start_all.sh'"

echo "🔧 Setting up V10 startup alias..."

# Detect shell and config file
if [[ "$SHELL" == *"zsh"* ]]; then
    CONFIG_FILE="$HOME/.zshrc"
    SHELL_NAME="zsh"
elif [[ "$SHELL" == *"bash"* ]]; then
    CONFIG_FILE="$HOME/.bash_profile"
    SHELL_NAME="bash"
else
    echo "⚠️  Unsupported shell: $SHELL"
    echo "Please manually add this line to your shell configuration:"
    echo "$ALIAS_LINE"
    exit 1
fi

# Check if alias already exists
if grep -q "alias v10=" "$CONFIG_FILE" 2>/dev/null; then
    echo "✅ V10 alias already exists in $CONFIG_FILE"
    echo "Current alias:"
    grep "alias v10=" "$CONFIG_FILE"
else
    echo "📝 Adding V10 alias to $CONFIG_FILE..."
    echo "" >> "$CONFIG_FILE"
    echo "# V10 Project Quick Start" >> "$CONFIG_FILE"
    echo "$ALIAS_LINE" >> "$CONFIG_FILE"
    echo "✅ Alias added successfully!"
fi

echo ""
echo "🎉 Setup complete! You can now use:"
echo "   v10    - Start all V10 services from anywhere"
echo ""
echo "To activate the alias in your current session, run:"
echo "   source $CONFIG_FILE"
echo ""
echo "Or simply open a new terminal window."