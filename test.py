from core.steam_api import SteamAPI


if __name__ == '__main__':
    test = SteamAPI.get_games_inventory(page=1)
