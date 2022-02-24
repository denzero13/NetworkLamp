from network_lamp_app.index import app


if __name__ == "__main__":
    app.run_server(port=8051)

server = app.server
