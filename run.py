from app import create_app


# Development config
app = create_app('config.DevConfig')
app.run(host='localhost', port=5000)

# Prod config
#app = create_app('config.ProdConfig')

