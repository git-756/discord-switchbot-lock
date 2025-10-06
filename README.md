# Discord SwitchBot Lock Bot

## 📖 概要 (Overview)

このプロジェクトは、SwitchBot API v1.1 を介してスマートロックや温湿度計の状態取得や操作を行い、その結果をDiscordに通知するPython Botです。

➡️ **ブログ記事: [【Mac miniではじめるPython IoT開発】Discord BotでSwitchBot Lockを遠隔操作する](https://samurai-human-go.com/python-discord-bot-switchbot-lock/)**

---

## ✨ 主な機能 (Features)

* **スマートロックの遠隔操作**:
    * `鍵開けて！`: スマートロックを解錠します。
    * `鍵閉めて！`: スマートロックを施錠します。
    * `鍵閉まってる？`: 現在の状態（施錠/解錠/電池残量）を確認します。
* **温湿度計のデータ取得**:
    * `温湿度は？`: SwitchBot温湿度計から現在の温度、湿度、電池残量を取得します。

---

## 🚀 準備と実行方法 (Prerequisites and How to Run)

このBotを動作させるには、いくつかの事前準備（APIキーの取得、Discord Botのセットアップなど）が必要です。

**詳しい手順は、上記のブログ記事でステップバイステップで解説しています。まずはこちらをご覧ください。**

---

## 📜 ライセンス (License)

このプロジェクトは **MIT License** のもとで公開されています。

また、このプロジェクトは以下のサードパーティ製ライブラリを使用しています。各ライブラリのライセンス条文の詳細は、プロジェクトルートの [`LICENSE`](LICENSE) ファイルをご確認ください。

* **discord.py**: MIT License
* **requests**: Apache License 2.0
* **python-dotenv**: BSD 3-Clause License

---

## 💬 質問など (Questions)

もしこの記事を読んで分からないことがあれば、ブログのコメント欄で質問してみてください。Tech Samuraiが気づけば、回答するかもしれませんよ！

-------------------------------------------

## 📖 (English) Usage and Detailed Guide

This is a Python bot that operates a SwitchBot Lock and sends notifications to Discord.

### Prerequisites and How to Run

To run this bot, you'll need to complete several setup steps first (e.g., getting API keys, setting up a Discord Bot).

**A detailed, step-by-step guide is available on my blog. Please read this article first.**

➡️ **[【Mac miniではじめるPython IoT開発】Discord BotでSwitchBot Lockを遠隔操作する](https://samurai-human-go.com/python-discord-bot-switchbot-lock/)** (The article is in Japanese, but contains all the necessary code and setup flow.)

### License

This project is licensed under the **MIT License**. For more details, see the `LICENSE` file in the project root.

### Questions?

If you have any questions after reading the article, feel free to ask them in the blog's comment section. If Tech Samurai notices, you might just get an answer!