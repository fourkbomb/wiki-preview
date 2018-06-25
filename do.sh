change=$1
commit=$2
ref=$3
baseurl=$4
dest=$5

echo change=$1 commit=$2 ref=$3 baseurl=$4 dest=$5

# Try multiple times to let replication happen
for i in 0 2 4 8 16 32; do
    sleep $i
    git fetch origin $ref
    GITRET=$?
    [ $GITRET -eq 0 ] && break;
done


[ $GITRET -ne 0 ] && exit 1

git worktree add ../$commit $commit || exit 2
cd ../$commit

EXIT_CODE=3

for i in 0; do # use this to make sure we clean up at the end

    bundle install || break
    echo "baseurl: $baseurl" > _config_ci.yml || break
    JEKYLL_ENV=$commit bundle exec jekyll build --config _config.yml,_config_ci.yml || break

    rm -rf _site/images/devices
    rm -rf $dest || break

    mv _site $dest || break
    EXIT_CODE=0
done

git worktree remove --force .

exit $EXIT_CODE
