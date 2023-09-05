SteamDB Discord Bot

This Discord bot allows you to retrieve and process game and DLC IDs from SteamDB using the ZenRows API. You can provide a list of game IDs, and the bot will fetch information about those games, including their DLCs, and provide you with a ZIP archive containing the collected data.

Use the following command to fetch and process game and DLC IDs:

css

!game_data [game_ids]

    [game_ids] is a comma-separated list of Steam game IDs. For example: 12345, 67890, 54321.
    The bot will prompt you if you want to add games in case they are from family sharing. You can reply with 'yes' or 'no'.