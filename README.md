# networks project

Infrastructure for analyzing social and other networks:
1. Load raw data into PostgreSQL using Singer (Meltano)
2. Clean and normalize data using dbt (Meltano)
3. Transform to nodes and edges tables using dbt (Meltano)
4. Analyze in Gephi via database import from PostgreSQL

## ELT

```
python -m venv tap-rest-api-venv
.\tap-rest-api-venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install tap-rest-api
python -m venv target-csv-venv
.\target-csv-venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install target-csv
```

## Server Setup

### OpenStack
I use a cloud provider that uses OpenStack. These are the commands I used to create and configure the database server:

```
python -m venv networks-venv
.\networks-venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
.\Initialize-OpenStack.secret.ps1
openstack keypair create --public-key ~\.ssh\id_rsa.pub panasenco
openstack server create --key-name panasenco --flavor a2-ram4-disk20-perf1 --network ext-net1 --image "Debian 11.1 bullseye" sql-db
openstack security group rule create --ingress --protocol tcp --dst-port 22 --ethertype IPv4 default
openstack security group rule create --ingress --protocol tcp --dst-port 22 --ethertype IPv6 default
openstack security group create postgresql
openstack security group rule create --ingress --protocol tcp --dst-port 5432 --ethertype IPv4 postgresql
openstack security group rule create --ingress --protocol tcp --dst-port 5432 --ethertype IPv6 postgresql
openstack server add security group sql-db postgresql
```

I also had to go to my modem settings and enable an IPv6 address to be able to connect to IPv6 addresses.

After all that, I could connect to the new VM via ssh.

### Setting up PostgreSQL on Debian 11

First ssh into the server via `ssh debian@<IP address>`, then:

```
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y postgresql-13
sudo -u postgres createuser -P loader
sudo -u postgres createuser -P transformer
sudo -u postgres createuser -P reporter
sudo -u postgres createdb raw
sudo -u postgres createdb analytics
sudo -u postgres psql -c "grant all privileges on database raw to loader;"
sudo -u postgres psql -c "grant all privileges on database analytics to transformer;"
sudo -u postgres psql -d raw -c "grant select on all tables in schema public to transformer;"
sudo -u postgres psql -d analytics -c "grant select on all tables in schema public to reporter;"
sudo sed -i "s/#listen_addresses.*/listen_addresses = '*'/" /etc/postgresql/13/main/postgresql.conf
echo 'host    all        all         all                   md5' | sudo tee -a /etc/postgresql/13/main/pg_hba.conf
sudo systemctl restart postgresql
```

After all these steps, you should be able to connect to the database as either one of the 3 users.
