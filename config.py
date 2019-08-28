import configparser

# List of subdirectories with ini files
ports = {
    "ap":5000,
    "cp":8080
}

config = configparser.ConfigParser()
for x in ports.keys():
    file = x +"/app.ini"
    config.read(file)
    config[config.sections()]["socket"] = ports.get(x)
    config.write(file)
