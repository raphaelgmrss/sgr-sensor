# sgr-sensor


### Configurando o ambiente virtual

```bash
cd ./backend
python3 -m venv venv
. venv/bin/activate
```

### Instalando os pacotes de dependências

```bash
pip3 install -r requirements.txt
```

```bash
cd ./frontend
npm install
```

### Executado o projeto em desenvolvimento

```bash
cd ./backend/api
export FLASK_APP=run
flask db init
flask db migrate
flask db upgrade
python3 ./run.py

cd ../../frontend
npm run dev
```

### Executando o projeto em produção

```bash
cd ./backend/build
rm -rf dist
./build.sh
```

### Salvando a imagem do projeto 

```bash
docker save sgr-sensor | gzip > sgr-sensor.tar.gz
```

### Carregando a imagem do projeto 

```bash
docker load -i sgr-sensor.tar.gz
```