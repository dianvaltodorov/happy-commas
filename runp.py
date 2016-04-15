#!env/bin/python
"""Run the app in production"""

from app import app
app.run(debug=False)
