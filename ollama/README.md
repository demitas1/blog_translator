# Ollamaをインストール

- Linux
- Docker (Linux)
- Docker (macOS)


## Linux

```
curl -fsSL https://ollama.com/install.sh | sh
```

### サービスを開始

```
sudo systemctl enable ollama
sudo systemctl start ollama
```

### 動作確認

```
curl http://localhost:11434
# "Ollama is running" と表示されればOK
```


### モデルの保存場所を変更

```
sudo SYSTEMD_EDITOR=vim systemctl edit ollama.service
```

下記を追加

```
[Service]
Environment="OLLAMA_MODELS=/path/to/your/models"
```

### モデルの保存

```
# 軽量モデル（テスト用）
ollama pull qwen2.5:0.5b

# 推奨モデル（実用用途向け）
ollama pull qwen2.5:14b
```

### モデル確認

```
ollama list
```

### カスタムモデルの作成

```
ollama create translation-helper -f Modelfile
```

### 動作確認

```
ollama run translation-helper "To configure the API_KEY, edit the config.json file in the /etc/app/ directory."

```

## Docker (Linux)

### NVidia Container Toolkit のインストール

公式を参照のこと

```
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
    sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg   && \
    curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
```

```
export NVIDIA_CONTAINER_TOOLKIT_VERSION=1.17.8-1
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

```
sudo nvidia-ctk runtime configure --runtime=crio
sudo systemctl restart crio
sudo docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi
```

### ホスト側 systemd で Ollama が動いている場合は停止

```
sudo systemctl stop ollama
sudo systemctl disable ollama
```

### モデルの保存場所を変更

使用する環境にあわせてマウントパスを設定してください

- `docker/docker-compose.yml`

```
    volumes:
      - /mnt/ext-ssd1/Application/ai_models/ollama:/root/.ollama
```

### Docker で Ollama を起動

```
cd docker
docker compose up -d

docker ps
docker compose logs ollama
ollama ps
```

### カスタムモデルの作成

```
ollama create translation-helper -f Modelfile
```

### 動作確認

```
ollama run translation-helper "To configure the API_KEY, edit the config.json file in the /etc/app/ directory."
```

## Docker (macOS)

```
cd docker/macos
docker compose up -d
```

### Modelfileをコンテナにコピー

```
docker cp ./Modelfile ollama:/tmp/Modelfile
```

### コンテナ内でモデルを作成

```
docker exec -it ollama ollama create my-model -f /tmp/Modelfile
```

### 一時ファイルを削除

```
docker exec -it ollama rm /tmp/Modelfile
```
