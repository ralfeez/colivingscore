# Gunicorn configuration for CoLivingScore
# The /api/market-analysis endpoint calls Claude AI with web search,
# which can take 60–120 seconds. Timeout must exceed that.

bind = "0.0.0.0:10000"
workers = 2
timeout = 180          # 3 minutes — covers Claude web search calls
worker_class = "sync"
