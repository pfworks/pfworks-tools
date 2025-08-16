#!/bin/bash

# HAL 9000 Interface - GitLab Repository Initialization Script
# This script helps set up the GitLab repository with proper configuration

set -e

echo "🚀 HAL 9000 Interface - GitLab Repository Setup"
echo "=============================================="

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    echo "✓ Git repository initialized"
else
    echo "✓ Git repository already exists"
fi

# Set up Git configuration (if not already set)
if [ -z "$(git config user.name)" ]; then
    echo "👤 Setting up Git user configuration..."
    read -p "Enter your name: " git_name
    read -p "Enter your email: " git_email
    git config user.name "$git_name"
    git config user.email "$git_email"
    echo "✓ Git user configuration set"
fi

# Add all files to git
echo "📦 Adding files to Git..."
git add .
echo "✓ Files added to Git"

# Create initial commit
if [ -z "$(git log --oneline 2>/dev/null)" ]; then
    echo "💾 Creating initial commit..."
    git commit -m "feat: initial HAL 9000 Interface v2.0.0

- Add dual color themes (Green/Amber)
- Add IBM terminal fonts with fallback system
- Add shell mode with tab completion
- Add full-height HAL panel with proper aspect ratio
- Add comprehensive documentation and CI/CD
- Add PIL-free version for compatibility
- Add automated installer and troubleshooting tools"
    echo "✓ Initial commit created"
else
    echo "✓ Repository already has commits"
fi

# Set up GitLab remote (if provided)
echo ""
echo "🔗 GitLab Remote Setup"
echo "To connect to GitLab, you'll need your repository URL."
echo "Example: https://gitlab.com/username/hal9000-interface.git"
echo ""
read -p "Enter GitLab repository URL (or press Enter to skip): " gitlab_url

if [ -n "$gitlab_url" ]; then
    # Remove existing origin if it exists
    git remote remove origin 2>/dev/null || true
    
    # Add new origin
    git remote add origin "$gitlab_url"
    echo "✓ GitLab remote added: $gitlab_url"
    
    # Ask about pushing
    echo ""
    read -p "Push to GitLab now? (y/N): " push_now
    if [[ $push_now =~ ^[Yy]$ ]]; then
        echo "📤 Pushing to GitLab..."
        git branch -M main
        git push -u origin main
        echo "✓ Pushed to GitLab successfully!"
        
        echo ""
        echo "🎉 Repository setup complete!"
        echo "Your HAL 9000 Interface is now on GitLab at:"
        echo "$gitlab_url"
    else
        echo "ℹ️  To push later, run:"
        echo "   git branch -M main"
        echo "   git push -u origin main"
    fi
else
    echo "ℹ️  GitLab remote not configured. You can add it later with:"
    echo "   git remote add origin <your-gitlab-url>"
fi

echo ""
echo "📋 Next Steps:"
echo "1. Visit your GitLab repository"
echo "2. Configure project settings and visibility"
echo "3. Set up GitLab Pages (if desired)"
echo "4. Configure branch protection rules"
echo "5. Set up issue labels and milestones"

echo ""
echo "🔧 Available GitLab Features:"
echo "• CI/CD Pipeline (.gitlab-ci.yml)"
echo "• Issue Templates (Bug, Feature)"
echo "• Merge Request Templates"
echo "• Automated Releases"
echo "• Package Distribution"

echo ""
echo "📚 Documentation Available:"
echo "• README.md - Main project documentation"
echo "• CONTRIBUTING.md - Contribution guidelines"
echo "• CHANGELOG.md - Version history"
echo "• SHELL_MODE_GUIDE.md - Shell usage guide"

echo ""
echo "✨ HAL 9000 Interface GitLab setup complete!"
echo "   'I'm sorry, Dave. I'm afraid I can't do that.'"
echo "   But this HAL can help you with AWS and system operations! 🚀"
