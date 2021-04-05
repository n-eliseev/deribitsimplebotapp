from deribitsimplebot import CBot, CMySQLBotStore
import yaml
import logging.config
import os

def main():

    is_docker= not (os.environ.get('IS_DOCKER_CONTAINER', None) is None)

    with open(('./docker-cfg.yml' if is_docker else './config.yaml'),'r') as f:
        _config = yaml.load(f.read(), Loader = yaml.FullLoader)
        config = _config['x-app'] if is_docker else _config

    logging.config.dictConfig(config['logging'])

    bot = CBot(
        **config['bot'], 
        store = CMySQLBotStore(**config['db'])
    )

    bot.run(
        synch_mod = config['synch']['mod'], 
        synch_actual = config['synch']['actual']
    )
