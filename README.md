<div align="center">
  <img src="https://get.snaz.in/3zZ3niN.png" alt="logo" align="left" width=256>
  <br>
  <br>
  <br>
  <h1>VideoBox</h1>
  <hr>
  <p>A Discord bot that makes and renders funny videos.</p>
</div>
<br>

### Installation
You need [Python 3.6](https://www.python.org/) with [ImageMagick](http://www.imagemagick.org/) and [FFmpeg](https://ffmpeg.org/).
```
sudo apt install python3.6 ffmpeg imagemagick

# Install dependencies
python3.6 -m pip install -r requirements.txt
```

### Usage
You can run `python3.6 main.py` (`python3` also works) to start the bot.
Make sure to copy and paste `config-example.json` into `config.json` and fill in the properties below **BEFORE** starting the bot.

### config.json
| Property | Type | Description |
| -------- | ---- | ----------- |
| name | string | The name of the bot. (i.e. "VideoBox") |
| version | string | The version of the bot. |
| description | string | The description of the bot. |
| token | string | The token to the bot, duh. |
| prefixes | array[string] | The prefixes that the bot will use. |
| owners | array[int] | The Discord IDs of the people able to use dev commands. |
| case_insensitive | bool | Whether or not commands aren't case sensitive |
| custom_help | bool | Whether or not to use custom help |
| stitch_mpy_audio | bool | If your server has problems with MoviePy having no audio in its output, enable this to have FFmpeg add audio instead. This will make rendering slower than usual. |
| botlist | object | Bot list tokens supported by [dbots.py](https://github.com/dbots-pkg/dbots.py) |

### Sources
- [Dank Memer](https://github.com/DankMemer) by Melmsie