# Remove the __pycache__ directory first
rm -rf semantic/__pycache__

# Remove the files from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch semantic/__pycache__/embedder.cpython-313.pyc" \
  --prune-empty --tag-name-filter cat -- --all

# Force push to remote
git push origin --force --all
