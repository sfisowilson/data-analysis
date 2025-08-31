#!/usr/bin/env python3
"""
Streamlit Community Cloud Deployment Helper
Prepares the repository for deployment to Streamlit Community Cloud.
"""

import os
import subprocess
import sys
from pathlib import Path

def check_git_status():
    """Check if we're in a git repository and get status."""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print("❌ Not in a git repository or git not available")
        return None

def check_github_remote():
    """Check if GitHub remote exists."""
    try:
        result = subprocess.run(['git', 'remote', '-v'], 
                              capture_output=True, text=True, check=True)
        remotes = result.stdout
        
        has_github = 'github.com' in remotes
        has_origin = 'origin' in remotes
        
        return has_github, has_origin, remotes
    except subprocess.CalledProcessError:
        return False, False, ""

def validate_requirements():
    """Validate that all required files exist."""
    required_files = [
        'enhanced_dashboard.py',
        'requirements.txt',
        '.streamlit/config.toml'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    return missing_files

def optimize_for_deployment():
    """Create deployment-optimized version hints."""
    print("💡 DEPLOYMENT OPTIMIZATION TIPS:")
    print("=" * 50)
    
    # Check file sizes
    output_dir = Path("output")
    if output_dir.exists():
        csv_files = list(output_dir.glob("*.csv"))
        total_size = sum(f.stat().st_size for f in csv_files)
        total_mb = total_size / (1024 * 1024)
        
        print(f"📊 CSV Data Size: {total_mb:.1f} MB")
        
        if total_mb > 100:
            print("⚠️  Large data size detected (>100MB)")
            print("   Consider data optimization for faster loading")
        else:
            print("✅ Data size suitable for Streamlit Cloud")
    
    # Check memory usage
    print("\n🧠 MEMORY OPTIMIZATION:")
    print("   - Streamlit Cloud limit: 1GB RAM")
    print("   - Current data should fit comfortably")
    print("   - Dashboard uses caching for efficiency")
    
    # Performance tips
    print("\n⚡ PERFORMANCE TIPS:")
    print("   - Data is cached with @st.cache_data decorators")
    print("   - Charts render efficiently with Plotly")
    print("   - Filtering is optimized for responsiveness")

def create_github_instructions():
    """Create step-by-step GitHub setup instructions."""
    print("\n🐙 GITHUB SETUP INSTRUCTIONS:")
    print("=" * 50)
    print("1. Go to https://github.com")
    print("2. Click 'New repository'")
    print("3. Repository name: 'stock-analytics-dashboard'")
    print("4. Description: 'Stock Data Analytics Dashboard'")
    print("5. Set to 'Public' (required for free Streamlit Cloud)")
    print("6. Don't initialize with README (we have existing code)")
    print("7. Click 'Create repository'")
    
    print("\n📤 PUSH TO GITHUB:")
    print("After creating GitHub repo, run these commands:")
    print("git remote add github https://github.com/YOUR_USERNAME/stock-analytics-dashboard.git")
    print("git push github main")

def create_streamlit_cloud_instructions():
    """Create Streamlit Cloud deployment instructions."""
    print("\n☁️ STREAMLIT CLOUD DEPLOYMENT:")
    print("=" * 50)
    print("1. Go to https://share.streamlit.io")
    print("2. Sign in with your GitHub account")
    print("3. Click 'New app'")
    print("4. Select your repository: 'YOUR_USERNAME/stock-analytics-dashboard'")
    print("5. Branch: 'main'")
    print("6. Main file path: 'enhanced_dashboard.py'")
    print("7. App URL: Choose a custom name (e.g., 'stock-analytics')")
    print("8. Click 'Deploy!'")
    
    print("\n⏱️ DEPLOYMENT TIME:")
    print("   - Initial deployment: 5-10 minutes")
    print("   - App will be available at: https://your-app-name.streamlit.app")
    print("   - Automatic updates when you push to GitHub")

def main():
    """Main deployment preparation function."""
    print("🚀 STREAMLIT COMMUNITY CLOUD DEPLOYMENT HELPER")
    print("=" * 60)
    
    # Check git status
    git_status = check_git_status()
    if git_status is None:
        return
    
    if git_status:
        print("⚠️  Uncommitted changes detected:")
        print(git_status)
        print("\nCommit changes before deployment:")
        print("git add .")
        print("git commit -m 'Prepare for Streamlit Cloud deployment'")
        print()
    else:
        print("✅ Git repository is clean")
    
    # Check GitHub remote
    has_github, has_origin, remotes = check_github_remote()
    
    print(f"\n📡 REMOTE REPOSITORIES:")
    if remotes:
        print(remotes)
    else:
        print("No remotes configured")
    
    # Validate required files
    missing_files = validate_requirements()
    if missing_files:
        print(f"\n❌ Missing required files: {missing_files}")
        return
    else:
        print("\n✅ All required files present")
    
    # Optimization tips
    optimize_for_deployment()
    
    # Instructions
    if not has_github:
        create_github_instructions()
    else:
        print("\n✅ GitHub remote already configured")
        print("You can proceed directly to Streamlit Cloud deployment")
    
    create_streamlit_cloud_instructions()
    
    print("\n" + "=" * 60)
    print("🎯 READY FOR DEPLOYMENT!")
    print("Follow the instructions above to deploy your dashboard")
    print("📧 Your dashboard will be publicly accessible and free forever")
    print("=" * 60)

if __name__ == "__main__":
    main()
