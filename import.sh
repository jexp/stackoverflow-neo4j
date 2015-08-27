NEO=${1-../neo}
DB=${2-$NEO/data/graph.db}
echo NEO $NEO DB $DB
rm -rf $DB
$NEO/bin/neo4j-import \
--bad-tolerance 10000 \
--skip-bad-relationships \
--into $DB \
--id-type string \
--nodes:Post csvs/posts.csv.gz \
--nodes:User csvs/users.csv.gz \
--nodes:Tag csvs/tags.csv.gz \
--relationships:PARENT_OF csvs/posts_rel.csv.gz \
--relationships:ANSWER csvs/posts_answers.csv.gz \
--relationships:HAS_TAG csvs/tags_posts_rel.csv.gz \
--relationships:POSTED csvs/users_posts_rel.csv.gz
#$NEO/bin/neo4j restart
