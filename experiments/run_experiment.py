from han.core.episode import Episode
from han.core.config import load_config

def main():
    config = load_config("configs/env.yaml")
    ep = Episode(config)
    result = ep.run()
    print(result)

if __name__ == "__main__":
    main()
