from dataclasses import dataclass
from environs import Env

env = Env()
env.read_env()


@dataclass
class Config:
    bot_token: str
    expert_ids: list[int]
    db_path: str = "bot.db"


def load_config() -> Config:
    return Config(
        bot_token=env.str("BOT_TOKEN"),
        expert_ids=list(map(int, env.list("EXPERT_IDS"))),
        db_path=env.str("DB_PATH", "bot.db"),
    )
