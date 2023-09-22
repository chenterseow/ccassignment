# Either add sudo before all commands or use sudo su first
# Amazon Linux 2023

#!binbash
dnf install git -y
git clone httpsgithub.comlowchoonkeataws-live.git
cd aws-live
dnf install python-pip -y
pip3 install flask pymysql boto3
python3 jobapply.py


