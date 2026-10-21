#scp -P 62828 -r ./data root@207.57.133.99:/root/work/career-guides-au/aijobrisk-go/data
#scp -P 62828 ./data.zip root@207.57.133.99:/root/work/career-guides-au/aijobrisk-go/data.zip
# 排除 blog/：博客由服务器上的 ops/blog-pull.sh 从 git 同步（GitHub Actions 自动发布）。
# 不排除的话 --delete 会用本地的旧副本覆盖、删掉 CI 新发的文章。
rsync -e 'ssh -p 62828' -avz --delete --exclude 'blog/' data root@207.57.133.99:/opt/career-guides-au/aijobrisk-go/
# rsync -e 'ssh -p 62828' -avz --delete aijobrisk-go/data/derived root@207.57.133.99:/root/work/career-guides-au/aijobrisk-go/data/
