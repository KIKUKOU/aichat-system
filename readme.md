# Config
コンフィグ設定の一覧は、config.yamlに記載する。

__（工事中）__

# 事前にインストールが必要なソフトウェア
下記のソフトウェアを使用するため、事前にインストールしておくこと。

## ffmpeg
[リンク](https://ffmpeg.org/)から適当にzipでダウンロードする。

適当な場所に解凍したソフトを配置し、環境変数からpathを通し使えるようにする。

# 使い方
docsやlog_files等があるディレクトリで、下記のようにコマンドを実行する。

また、仮想環境を構築する場合は、上記のディレクトリに構築することを想定している。

#### コンソールチャットを実行する場合
```shell-session
$ python ./aichat_system/console_chat.py
```

#### 生成される音声の確認を行う場合（not use AI）
```shell-session
$ python ./aichat_system/sound_test.py
```

#### Discordのbotを実行する場合
```shell-session
$ python ./aichat_system/discord_bot.py
```

