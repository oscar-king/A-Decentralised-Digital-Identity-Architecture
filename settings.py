import configparser
import os
import dotenv
import nginx

# Load the environment variables from the .env file
dotenv.load_dotenv('.env')

# All app subdirectories
subdirs = [x.strip() for x in os.environ.get("SUBDIRS").split(',')]

# We need to edit the sockets in the INI files in the application directories
config = configparser.ConfigParser()
nginx_config = nginx.Conf()
for subdir in subdirs:
    # Load the respective config file and get the respective env variables
    file = subdir + "/" + subdir +".ini"
    host = os.environ.get(subdir + "_host")
    port = os.environ.get(subdir + "_port")

    # Read the INI file
    config.read(file)

    # Generate required socket and set it
    socket = host + ":" + port
    config.set('uwsgi', 'socket', socket)

    # Write the updates to the file
    with open(file, 'w') as configfile:
        config.write(configfile)

    configfile.close()

    # Add server module to the nginx file object
    server = nginx.Server()
    server.add(
        nginx.Key('listen', port + " " + "ssl"),
        nginx.Key('ssl_certificate', "/etc/nginx/" + subdir + "_cert.crt"),
        nginx.Key('ssl_certificate_key', "/etc/nginx/" + subdir + "_cert.key"),
        nginx.Location('/',
                       nginx.Key('include', 'uwsgi_params'),
                       nginx.Key('uwsgi_pass', subdir + ":" + port)
                       )
    )
    nginx_config.add(server)

# Hardcoded redirect for base localhost
# server = nginx.Server()
# server.add(
#     nginx.Key('listen', "80"),
#     nginx.Key('listen', "8080"),
#     nginx.Key('server_name', "localhost"),
#     nginx.Key('return', "307 https://github.com/oscar-king/A-Decentralised-Digital-Identity-Architecture$request_uri")
# )
# nginx_config.add(server)

# Write the nginx.conf file
nginx.dumpf(nginx_config, 'nginx/nginx.conf')
