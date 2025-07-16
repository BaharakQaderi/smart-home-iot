# Git Flow Guide for Smart Home IoT Project

## 🎯 **Educational Git Flow Strategy**

This project follows a **structured git flow** to teach students professional development practices used in real-world projects.

## 🌳 **Branch Structure**

```
main (production-ready)
├── develop (integration branch)
├── feature/phase-2-sensors
├── feature/frontend-dashboard
├── feature/websocket-improvements
└── hotfix/security-updates
```

### **Branch Purposes**

| Branch | Purpose | Who can merge |
|--------|---------|---------------|
| `main` | Production-ready code, stable releases | Project maintainers only |
| `develop` | Integration branch, ongoing development | Team leads, via PR review |
| `feature/*` | New features and improvements | Developers, via PR to develop |
| `hotfix/*` | Critical bug fixes | Emergency fixes, via PR to main |

## 📝 **Development Workflow**

### **1. Starting a New Feature**

```bash
# Always start from develop
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/sensor-simulation

# Work on your feature
# ... make changes ...

# Commit with descriptive messages
git add .
git commit -m "feat: add temperature sensor simulation"

# Push feature branch
git push origin feature/sensor-simulation
```

### **2. Commit Message Convention**

Follow **Conventional Commits** format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```bash
git commit -m "feat: add temperature sensor simulation"
git commit -m "fix: resolve WebSocket connection timeout"
git commit -m "docs: update API documentation"
git commit -m "style: format code with prettier"
git commit -m "refactor: optimize database queries"
```

### **3. Pull Request Process**

1. **Create PR**: `feature/sensor-simulation` → `develop`
2. **Code Review**: Team reviews the changes
3. **Testing**: Ensure all tests pass
4. **Merge**: Squash and merge to develop
5. **Cleanup**: Delete feature branch

### **4. Release Process**

```bash
# Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v1.1.0

# Final testing and bug fixes
# ... make release-specific changes ...

# Merge to main
git checkout main
git merge release/v1.1.0
git tag v1.1.0
git push origin main --tags

# Merge back to develop
git checkout develop
git merge release/v1.1.0
git push origin develop
```

## 🚀 **Phase 2 Development Example**

### **Starting Phase 2: Sensor Simulation**

```bash
# Start from develop
git checkout develop
git pull origin develop

# Create phase 2 branch
git checkout -b feature/phase-2-sensors

# Work on sensor simulation
# ... implement temperature sensors ...
git add .
git commit -m "feat: implement temperature sensor simulation"

# ... implement humidity sensors ...
git add .
git commit -m "feat: add humidity sensor with realistic data"

# ... implement energy monitoring ...
git add .
git commit -m "feat: add energy consumption monitoring"

# Push and create PR
git push origin feature/phase-2-sensors
```

### **Multiple Developers Working Together**

```bash
# Developer A: Frontend Dashboard
git checkout -b feature/frontend-dashboard

# Developer B: WebSocket Improvements  
git checkout -b feature/websocket-improvements

# Developer C: Database Optimization
git checkout -b feature/database-optimization
```

## 📊 **Current Project Status**

- **main**: Phase 1 complete, all infrastructure working
- **develop**: Ready for Phase 2 development
- **next**: Phase 2 sensor simulation and real-time data

## 🔧 **Useful Git Commands**

### **Check Status**
```bash
git status                    # Check working directory
git branch -a                # List all branches
git log --oneline            # View commit history
git remote -v                # Check remote repositories
```

### **Syncing with Remote**
```bash
git fetch origin             # Fetch latest changes
git pull origin develop      # Pull and merge develop
git push origin feature/xyz  # Push feature branch
```

### **Cleaning Up**
```bash
git branch -d feature/xyz    # Delete local branch
git push origin --delete feature/xyz  # Delete remote branch
```

## 🎓 **Learning Outcomes**

Students will learn:
- **Professional Git Workflow**: Industry-standard branching strategy
- **Code Review Process**: Collaborative development practices
- **Continuous Integration**: Automated testing and deployment
- **Version Control**: Proper commit messages and history
- **Team Collaboration**: Working with multiple developers

## 🐛 **Emergency Hotfix Process**

```bash
# Critical bug in production
git checkout main
git pull origin main
git checkout -b hotfix/security-patch

# Fix the critical issue
git add .
git commit -m "fix: resolve security vulnerability"

# Deploy immediately
git checkout main
git merge hotfix/security-patch
git push origin main

# Merge back to develop
git checkout develop
git merge hotfix/security-patch
git push origin develop
```

## 📚 **Resources for Students**

- **Git Flow**: https://nvie.com/posts/a-successful-git-branching-model/
- **Conventional Commits**: https://www.conventionalcommits.org/
- **GitHub Flow**: https://guides.github.com/introduction/flow/
- **Git Best Practices**: https://www.git-tower.com/learn/git/ebook/

## 🎯 **Next Steps**

1. **Students**: Create your feature branch from `develop`
2. **Work**: Implement Phase 2 features
3. **Review**: Submit PR for code review
4. **Merge**: Integrate into develop branch
5. **Deploy**: Release to main when ready

---

**Remember**: This git flow teaches real-world development practices that students will use in their professional careers! 🌟 