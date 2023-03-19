# Hitoha
Hitoha is a discord bot.

# Commands
Hitoha uses "!!" as the prefix to recognise commands

<ul>
  <li>ping (pings Hitoha and sends back the latency in miliseconds)</li>
  <li>pfp (returns an image of the uses profile picture and server profile picture if available)</li>
  <li>choose (randomly selects a choice from the given options)</li>
  <li>8ball (roll the magic 8ball)</li>
  <li>purge (deletes messages default: 10)</li>
  <li>stealemote (steals the sent emote)</li>
  <li>calculate (gives the answer based on the equation given)</li>
  <li>remind (sets a reminder)</li>
</ul>

# Chat
Hitoha uses ChatGPT API to "talk" to the users"
<ul>
  <li>ask (ask a question)</li>
  <li>convo (starts a conversation between the bot and the user)</li>
</ul>

# Economy
Hitoha uses a SQL database to store the data for economy
<ul>
  <li>bal (checks current balance of user (default: author))</li>
</ul>

# Games
<ul>
  <li>tictactoe</li>
  <li>blackjack</li>
</ul>

# Music
<ul>
  <li>play (finds a song on youtube from the keywords)</li>
  <li>pause (pauses current song)</li>
  <li>resume (resumes player)</li>
  <li>queue (shows current queue)</li>
  <li>skip (skip current song)</li>
  <li>loop (loops current song)</li>
  <li>np (shows the current playing song)</li>
  <li>shuffle (shuffles the queue)</li>
  <li>move (moves song from its current spot in the queue)</li>
</ul>

# API
<ul>
  <li>Discord API</li>
  <li>OpenAI API</li>
</ul>

# Requirements
These are python libraries required to run the bot
<ul>
  <li>discord.py</li>
  </li>openai</li>
  <li>python-dotenv</li>
  <li>youtube-dl</li>
  <li>PyNaCl</li>
  <li>mysql-connector-python</li>
  <li>APScheduler</li>
  <li>voicevox-client<li>
</ul>

# Miscellaneous
<ul>
  <li>Speach</li>
  <ul>
    <li>Hitoha uses VoiceVox on a private API to synthesize Japanese dialog from text.</li>
    <li>It uses a the voicevox-engine docker on a virtual machine as the server to process information.</li>
  </ul>
</ul>

# Tokens
Hitoha uses 2 API keys, one from Discord to connect with the bot and one for OpenAI. Replacing the keys in index.py to your own keys.
