### chenkx找到的启动augur方法

> 提一句
> 原repo推出了v0.40版本，但是默认的main分支还是老版本。
> 新版本应该在`augur-new`相关的分支上。

设置环境变量
```shell
export AUGUR_DB_PORT=5434
export AUGUR_GITHUB_USERNAME=<your github username>
export AUGUR_GITHUB_API_KEY=<your github token>
export AUGUR_GITLAB_USERNAME=<your github username>
export AUGUR_GITLAB_API_KEY=<your github token>
```

#### 使用docker的postgres数据库
```shell
docker compose up
```
#### 使用本地的postgres数据库

##### 搭建、配置本地postgres数据库
设置`postgresql.conf`
```conf
listen_addresses = '*' 
```
使用docker连接数据库，还需要在`pg_hba.conf`后面添加
```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD
host      all             all             0.0.0.0/0               md5
```

##### 创建augur数据库以及augur账户，并配置权限
```sql
CREATE DATABASE augur;
CREATE USER augur WITH ENCRYPTED PASSWORD 'augur';
-- GRANT ALL PRIVILEGES ON DATABASE augur TO augur;
ALTER DATABASE augur OWNER TO augur;
```
##### 还要多设置一个环境变量

wsl中的ip地址可以通过`ip addr | grep eth0`输出中inet后面的地址得到。
```shell
# if in wsl:
export AUGUR_DB=postgresql+psycopg2://augur:augur@172.24.64.222:5432/augur
# if in windows:
export AUGUR_DB=postgresql+psycopg2://augur:augur@localhost:5432/augur
```
##### 启动augur

```shell
# 使用wsl或者windows中的postgres
docker compose -f docker-compose-externalDB.yml  up -d
```