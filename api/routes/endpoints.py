from dataclasses import dataclass


@dataclass
class ApiEndpoints:
    PING: str = "/ping"
    HEALTH: str = "/health"
    ASSISTANTS: str = "/assistants"
    HN: str = "/hn"
    ARXIV_DISCORD: str = "/arxiv_discord"


endpoints = ApiEndpoints()
