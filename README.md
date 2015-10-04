# IRC_bot: Python bot for IRC

Simple IRC bot wrote by python, using socket.

Usage:

    python IRC_bot.py

We can change the nick name of the bot (default is cribot).

Controlling the bot thought IRC:

You need login to channel and chat with bot to control it.

Execute IRC command:

    irc <command>

Execute database command: 

    exec <command>

    List of command:
      add_db(<string>): add information to database
      show_db: show database
      remove_db: delete ALL information from database

Execute CLI command:

    cli <command>
    
Inspect in channel: You can inspect information in channel by using database. The bot can stay on channel, alert you when one of string in database appear.

    inspect --start/--stop: start/stop inspect process

Caution: before using control function, you need login by command: authen. You must enter right name and password to login. You can change name and pass in source code (use hash value) :)
