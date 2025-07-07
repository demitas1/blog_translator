# Ollamaをインストール

```
curl -fsSL https://ollama.com/install.sh | sh
```

# サービスを開始

```
sudo systemctl enable ollama
sudo systemctl start ollama
```

# 動作確認

```
curl http://localhost:11434
# "Ollama is running" と表示されればOK
```


# モデルの保存場所を変更

```
sudo SYSTEMD_EDITOR=vim systemctl edit ollama.service
```

下記を追加

```
[Service]
Environment="OLLAMA_MODELS=/path/to/your/models"
```

# モデルの保存

```
# 軽量モデル（テスト用）
ollama pull qwen2.5:0.5b

# 推奨モデル（実用用途向け）
ollama pull qwen2.5:14b
```

# モデル確認

```
ollama list
```

# カスタムモデルの作成

```
ollama create translation-helper -f Modelfile
```

# 動作確認

```
ollama run translation-helper "To configure the API_KEY, edit the config.json file in the /etc/app/ directory."

```
