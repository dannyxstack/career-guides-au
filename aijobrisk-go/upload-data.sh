#scp -P 62828 -r ./data root@207.57.133.99:/root/work/career-guides-au/aijobrisk-go/data
#scp -P 62828 ./data.zip root@207.57.133.99:/root/work/career-guides-au/aijobrisk-go/data.zip
rsync -e 'ssh -p 62828' -avz --delete data root@207.57.133.99:/opt/career-guides-au/aijobrisk-go/
# rsync -e 'ssh -p 62828' -avz --delete aijobrisk-go/data/derived root@207.57.133.99:/root/work/career-guides-au/aijobrisk-go/data/
