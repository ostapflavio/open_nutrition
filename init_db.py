from alembic.config import Config
from alembic import command 

def main():
    cfg = Config("alembic.ini")
    command.upgrade(cfg, 'head')
    print("Database initialized!")

if __name__ == "__main__":
    main()
